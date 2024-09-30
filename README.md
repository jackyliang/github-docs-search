# Github Documentation Search Sample App

This is a Github Documentation Search Sample App built with Timescale DB, pgvectorscale, and Python FastAPI. 

This Sample App lets you easily have a document search app setup and running on your local machine. Additionally, it allows you to load data from text files, create embeddings, chunks your data, and perform semantic search over the data. 

You don't need to know anything about Timescale DB, pgvectorscale, or even Postgres to get this running. You can just focus on building out the frontend and gathering your own documentation! 

*Built by Jacky Liang*

![image](https://github.com/user-attachments/assets/6e9274c5-ba01-48eb-baea-453dfe9e64b1)

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
   - Create a new Timescale DB instance on [Timescale Cloud](https://console.cloud.timescale.com/signup).
   - Set a password for the user and update your `DATABASE_URL` in the `.env` file.
   - Make sure to setup the correct `DATABASE_URL` in the `.env` file.

4. **Environment Variables**
   - Create a `.env` file in the same directory as `docs_server.py` with the following content:

     ```
     DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
     ANTHROPIC_API_KEY=your_anthropic_api_key
     OPENAI_API_KEY=your_openai_api_key
     ```

   - Replace the placeholders with your actual database credentials and API keys.
   - Alternatively, you can set the environment variables in your operating system. For example, on Linux or MacOS, you can set the environment variables with the following commands:

     ```bash
     export DATABASE_URL=postgresql://username:password@localhost:5432/your_database_name
     export ANTHROPIC_API_KEY=your_anthropic_api_key
     export OPENAI_API_KEY=your_openai_api_key
     ```

5. **Running the Server**
   - Start the server with:

     ```bash
     python docs_server.py
     ```

   - The server will start on `http://localhost:8000`.

6. **Using the API**

   - Note that a live playground for API docs are also available at `http://localhost:8000/docs`.

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
          -d '{"question": "How do you install pgvectorscale?"}'
     ```

   - View the first few documents:
     ```bash
     curl "http://localhost:8000/head_documents"
     ```

## How to get Github documentation data

1. Go to a Github repo of your choice
2. Click on the `README.md` file
3. Click on the `Raw` button
4. Copy the contents
5. Paste the contents into a text file
6. Use the `/load_data` endpoint to load the data into the database

Some Github docs files are included in `/sample-data/` containing README for
- [Timescale DB](https://github.com/timescale/timescaledb/blob/main/README.md)
- [pgvectorscale](https://github.com/timescale/pgvectorscale/blob/main/README.md)
- [pgai](https://github.com/timescale/pgai/blob/main/README.md)
- [pgvector](https://github.com/pgvector/pgvector/blob/master/README.md)

Feel free to add your own Github README.md files to the `/sample-data/` folder.

## Further developments

- [ ] Use pgai to generate embeddings and generate responses
- [ ] Use a better chunking algorithm like semantic chunking
- [ ] Automatically load README.md files from Github repositories
- [ ] Implement one-click deployment to Vercel

## Notes 

   - Ensure Timescale DB is configured to handle vector operations.
   - The script assumes you have the necessary permissions to create extensions and tables in your database.
   - Adjust the `CharacterTextSplitter` parameters in the `read_custom_dataset` function if you need different chunking behavior.
   - The script uses OpenAI's embedding model and Anthropic's Claude model. Ensure you have sufficient API credits. 
   - The `index.html` file is a simple React frontend that allows you to search the documentation. It uses FastAPI's `query` endpoint to get search results.
