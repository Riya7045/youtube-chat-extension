AI YouTube Assistant 🤖💬

A browser extension that allows you to have a conversation with any YouTube video. Ask questions about the video's content and get instant, context-aware answers powered by a real-time RAG (Retrieval-Augmented Generation) pipeline.

Features

Conversational Q&A: Ask questions in natural language about the video you're watching.

Context-Aware Answers: The AI generates answers based only on the video's transcript, preventing hallucinations.

Real-Time Generation: A new, in-memory vector store is created for each video, ensuring answers are always relevant to the content.

Fast & Lightweight: Built with a modern FastAPI backend and a vanilla JavaScript frontend for minimal overhead.

How It Works (Architecture)

This project uses a dynamic, per-request RAG pipeline to generate answers.

Frontend (Browser Extension): The JavaScript extension injects a chat interface into the YouTube page. When you open a video, it fetches the transcript.

User Query: When you ask a question, the extension sends the query and the full vidDetails (transcript) to the backend.

Backend (FastAPI): A Python server built with FastAPI receives the request at the /videochat endpoint.

Dynamic RAG Pipeline: The server's generate_answer function executes the entire RAG pipeline in real-time:
a.  Chunking: The transcript is split into manageable chunks using langchain.
b.  Embedding: The chunks are embedded using Google's models/embedding-001.
c.  Vector Store: A temporary, in-memory FAISS vector store is built from the embeddings.
d.  Retrieval: The FAISS store retrieves the most relevant transcript chunks based on your query.
e.  Generation: The retrieved chunks (context) and your query are passed to the gemini-2.5-flash LLM via a prompt template.

Response: The generated answer is sent back to the browser extension and displayed in the chat UI.

Tech Stack

Backend: Python

API Server: FastAPI

AI/LLM: Google Gemini Pro (gemini-2.5-flash, embedding-001)

Orchestration: LangChain

Vector Store: FAISS (in-memory)

Frontend: JavaScript (as a browser extension)

Transcript Fetching: youtube-transcript-api

Setup & Installation

You'll need to set up the backend server and the frontend extension separately.

1. Backend Server

Clone the repository:

git clone [https://github.com/your-username/ai-youtube-assistant.git](https://github.com/your-username/ai-youtube-assistant.git)
cd ai-youtube-assistant/backend


Create a virtual environment and install dependencies:

python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate


Create a requirements.txt file with the following content:

fastapi
uvicorn[standard]
langchain-google-genai
langchain-community
faiss-cpu
youtube-transcript-api
python-dotenv


Then, install the requirements:

pip install -r requirements.txt


Create an environment file:
Create a file named .env in the backend directory and add your Gemini API key:

GEMINI_API_KEY="YOUR_GEMINI_API_KEY_HERE"


Run the server:

uvicorn server:app --reload


The server will be running at http://127.0.0.1:8000.

2. Frontend (Browser Extension)

Configure the API Endpoint:
Open the frontend JavaScript file (e.g., content.js or background.js) and ensure the fetch URL points to your local server:

const API_URL = '[http://127.0.0.1:8000/videochat](http://127.0.0.1:8000/videochat)';


Load the Extension in Chrome/Edge:
a. Open your browser and navigate to chrome://extensions or edge://extensions.
b. Enable "Developer mode" (usually a toggle in the top-right corner).
c. Click "Load unpacked".
d. Select the folder containing your extension's manifest.json file.

Start Chatting:
Open any YouTube video, and the chat assistant should appear.

API Endpoint

POST /videochat

Receives a user's query and the video transcript, and returns a generated answer.

Request Body:

{
  "query": "What did the speaker say about nuclear fusion?",
  "vidDetails": "In this video, we'll explore... [full transcript text] ...and that's why it's so important."
}


Success Response (200 OK):

{
  "answer": "The speaker mentioned that nuclear fusion is a promising source of clean energy, but it still faces significant engineering challenges before it can be viable."
}


License

This project is licensed under the MIT License. See the LICENSE file for details.
