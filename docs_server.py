# python rag_server.py

# Load data
# curl -X POST "http://localhost:8000/load_data" \
    #  -H "Content-Type: application/json" \
    #  -d '{"file_path": "/Users/jacky/Code/answerhq/utilities/Scripts/output/docs.timescale.com/results.txt"}'

# Query data
# curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json" -d '{"question": "What is the main topic of this document?"}'

# Delete index
# curl -X DELETE "http://localhost:8000/delete_index/documents_embedding_idx"

# List indexes
# curl "http://localhost:8000/list_indexes"

# Head documents (show first 5)
# curl "http://localhost:8000/head_documents"

import psycopg2
from fastapi import FastAPI, HTTPException, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import os
from anthropic import Anthropic
from fastapi.responses import JSONResponse
import openai
from openai import OpenAI
import threading
from langchain.text_splitter import CharacterTextSplitter

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def relevant_search(conn, query):
    query_embeddings = get_embedding(query)
    with conn.cursor() as cur:
        sql_query = 'SELECT contents, embedding <=> %s::vector AS cosine_distance FROM documents ORDER BY embedding <=> %s::vector LIMIT 20'
        cur.execute(sql_query, (query_embeddings, query_embeddings))
        results = cur.fetchall()
        print(f"Number of relevant documents found: {len(results)}")
        return results

def read_custom_dataset(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    text_splitter = CharacterTextSplitter(
        separator="\n\n",
        chunk_size=256,
        chunk_overlap=20
    )
    
    chunks = text_splitter.split_text(content)
    
    print(f"Total chunks created: {len(chunks)}")
    for i, chunk in enumerate(chunks[:5]):
        print(f"Chunk {i + 1} preview:")
        print(chunk[:100] + "...")
        print("-" * 50)
    
    return chunks

CONNECTION = os.environ.get("DATABASE_URL")
conn = psycopg2.connect(CONNECTION)
cursor = conn.cursor()

cursor.execute("CREATE EXTENSION IF NOT EXISTS vectorscale CASCADE")
conn.commit()

document_table = """CREATE TABLE IF NOT EXISTS documents (
    id BIGINT PRIMARY KEY GENERATED BY DEFAULT AS IDENTITY,
    contents TEXT,
    embedding VECTOR(1536)
)"""
cursor.execute(document_table)
conn.commit()

openai_client = OpenAI()

anthropic_client = Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

import numpy as np

def get_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    embedding = response.data[0].embedding
    normalized_embedding = embedding / np.linalg.norm(embedding)
    return normalized_embedding.tolist()

ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("ANTHROPIC_API_KEY environment variable is not set")

def rag_function(conn, query):
    relevant_docs = relevant_search(conn, query)
    relevant_text = " ".join([doc[0] for doc in relevant_docs])
    full_query = (f"Context: The following are relevant passages related to the query.\n"
        f"{relevant_text}\n\n"
        f"Based on the above context, please answer the following question:\n"
        f"Question: {query}")
    message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20240620",
        max_tokens=4096,
        temperature=0,
        system="You are a helpful assistant made by Jacky Liang, an applicant for the role of Developer Advocate for TimescaleDB. Given a query and context, provide accurate information. Don't hallucinate if the context doesn't provide relevant information. Answer directly, don't mention the context. Write your answer in Markdown.",
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": full_query
                    }
                ]
            }
        ]
    )
    return message.content

class Query(BaseModel):
    question: str

class LoadDataRequest(BaseModel):
    file_path: str

@app.post("/load_data")
async def load_data(request: LoadDataRequest):
    try:
        sample_dataset = read_custom_dataset(request.file_path)
        print(f"Processing {len(sample_dataset)} chunks for embeddings...")
        
        all_embeddings = []
        for i, chunk in enumerate(sample_dataset):
            print(f"Getting embedding for chunk {i+1}")
            embedding = get_embedding(chunk)
            all_embeddings.append(embedding)

        print(f"Inserting {len(all_embeddings)} embeddings into the database...")
        sql = 'INSERT INTO documents (contents, embedding) VALUES (%s, %s)'
        data_to_insert = list(zip(sample_dataset, all_embeddings))
        cursor.executemany(sql, data_to_insert)
        conn.commit()
        print("Database insertion completed.")

        print("Creating index...")
        ivfflat = """CREATE INDEX IF NOT EXISTS documents_embedding_idx ON documents USING diskann (embedding)"""
        cursor.execute(ivfflat)
        conn.commit()
        print("Index creation completed.")

        return {"message": "Data loaded successfully"}
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/query")
async def query(query: Query):
    try:
        relevant_docs = relevant_search(conn, query.question)
        response = rag_function(conn, query.question)
        return {
            "response": response,
            "relevant_docs": [
                {"content": doc[0], "cosine_distance": doc[1]}
                for doc in relevant_docs
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/head_documents")
async def head_documents(limit: int = 5):
    try:
        cursor.execute(f"""
            SELECT id, contents, embedding
            FROM documents
            ORDER BY id
            LIMIT {limit}
        """)
        rows = cursor.fetchall()
        
        result = []
        for row in rows:
            embedding_list = list(row[2])
            result.append({
                "id": row[0],
                "contents": row[1],
                "embedding": embedding_list[:5] + ['...'] if len(embedding_list) > 5 else embedding_list
            })
        
        return JSONResponse(content={"documents": result})
    except Exception as e:
        print(f"Error in head_documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)