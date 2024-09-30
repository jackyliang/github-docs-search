# TimescaleDB Developer Advocate Take Home Assignment

This is a Github Documentation Search built with Timescale DB, pgvectorscale, and Python FastAPI. It allows you to load data from a text file, create embeddings, and perform similarity searches. 

Some Github docs files are included in `/sample-data/` containing README for
- Timescale DB
- pgvectorscale
- pgai
- pgvector

## Installation and Setup Instructions

1. **Python Environment**
   - Ensure you have Python 3.7+ installed on your system.
   - It's recommended to use a virtual environment:

     ```bash
     python -m venv venv
     source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
     ```

2. **Install Dependencies**
   - Create a `requirements.txt` file with the following content:

     ```
     fastapi
     uvicorn
     psycopg2-binary
     anthropic
     openai
     langchain
     numpy
     pydantic
     ```

   - Install the dependencies:

     ```bash
     pip install -r requirements.txt
     ```

3. **Database Setup**
   - Install PostgreSQL 15 or later.
   - Create a new database for this project.
   - Install the `vectorscale` extension in your PostgreSQL instance.

4. **Environment Variables**
   - Create a `.env` file in the same directory as `docs_server.py` with the following content:

     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

   - Replace the placeholders with your actual database credentials and API keys.

5. **Running the Server**
   - Start the server with:

     ```bash
     python docs_server.py
     ```

   - The server will start on `http://localhost:8000`.

6. **Using the API**
   - Load data:
     ```bash
     curl -X POST "http://localhost:8000/load_data" \
          -H "Content-Type: application/json" \
          -d '{"file_path": "/path/to/your/data/file.txt"}'
     ```

   - Query the data:
     ```bash
     curl -X POST "http://localhost:8000/query" \
          -H "Content-Type: application/json" \
          -d '{"question": "What is the main topic of this document?"}'
     ```

   - View the first few documents:
     ```bash
     curl "http://localhost:8000/head_documents"
     ```

7. **Notes**
   - Ensure Timescale DB is configured to handle vector operations.
   - The script assumes you have the necessary permissions to create extensions and tables in your database.
   - Adjust the `CharacterTextSplitter` parameters in the `read_custom_dataset` function if you need different chunking behavior.
   - The script uses OpenAI's embedding model and Anthropic's Claude model. Ensure you have sufficient API credits. 
   - The `index.html` file is a simple React frontend that allows you to search the documentation. It uses FastAPI's `query` endpoint to get search results.
