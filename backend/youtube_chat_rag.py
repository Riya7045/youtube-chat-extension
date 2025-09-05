# -*- coding: utf-8 -*-
"""
RAG with LangChain, Gemini Pro API, and FAISS Vector Store

This script demonstrates building a Retrieval-Augmented Generation (RAG) pipeline
using the Gemini Pro API for both LLM and embeddings, integrated with LangChain and FAISS.

Dependencies:
- youtube-transcript-api
- langchain-community
- langchain-google-genai
- faiss-cpu
"""

# !pip install -q youtube-transcript-api langchain-community langchain-google-genai faiss-cpu

from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableParallel, RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv
import os

# -----------------------------
# Setup and Configuration
# -----------------------------
def load_api_key():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables.")
    return api_key
api_key = load_api_key()


# ------------------------------
# Step 1a: Document Ingestion
# ------------------------------

def fetch_transcript(video_id: str) -> str:
    """Fetch transcript text from a YouTube video ID."""
    try:
        ytt_api = YouTubeTranscriptApi()
        transcript_list = ytt_api.fetch(video_id).to_raw_data()
        return " ".join(chunk["text"] for chunk in transcript_list)
    except TranscriptsDisabled:
        print("No captions available for this video.")
        return ""

video_id = "Gfr50f6ZBvo"            # Sample video ID
transcript = fetch_transcript(video_id)
# print(transcript[:300])              # Preview first 300 characters

# ------------------------------
# Step 1b: Text Splitting
# ------------------------------

# Split the transcript into manageable chunks for embedding
splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = splitter.create_documents([transcript])
print(f"Number of chunks: {len(chunks)}")
# print(f"Sample chunk:\n{chunks[0].page_content[:200]}...")

# ------------------------------
# Step 1c/1d: Embedding & Vector Store
# ------------------------------

def build_vector_store(chunks, api_key: str):
    """
    Embed text chunks using Gemini embeddings and store them in FAISS.
    """
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001",
        google_api_key=api_key
    )
    return FAISS.from_documents(chunks, embeddings)

vector_store = build_vector_store(chunks, api_key)

# ------------------------------
# Step 2: Retrieval
# ------------------------------

# Create a retriever object for similarity search (top-4 by default)
retriever = vector_store.as_retriever(search_type="similarity", search_kwargs={"k": 4})

# Sample query to retrieve relevant chunks
sample_query = "Is the topic of nuclear fusion discussed in this video? If yes then what was discussed?"
retrieved_docs = retriever.invoke(sample_query)
print(f"Retrieved {len(retrieved_docs)} docs for query: '{sample_query}'\n")
# print(f"Retrieved docs:\n {retrieved_docs}")


# ------------------------------
# Step 3: Augmentation (Prompt Engineering)
# ------------------------------

# Define the prompt template ensuring the LLM answers only using retrieved context
prompt = PromptTemplate(
    template="""
      You are a helpful assistant.
      Answer ONLY from the provided transcript context.
      If the context is insufficient, just say you don't know.

      Context: {context}
      Question: {question}
    """,
    input_variables=['context', 'question']
)

# Preparing the actual context for a question
question = "Is the topic of nuclear fusion discussed in this video? If yes then what was discussed?"
context_text = "\n\n".join(doc.page_content for doc in retrieved_docs)
final_prompt = prompt.invoke({"context": context_text, "question": question})

# print(f"Prompt Template:\n{final_prompt}")
# ------------------------------
# Step 4: Generation (Gemini LLM)
# ------------------------------

# Instantiate Gemini LLM for answer generation
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",             # Gemini Pro LLM
    google_api_key=api_key,
    temperature=0.2
)

# Generate answer from Gemini using the final prompt
answer = llm.invoke(final_prompt)
print(f"Chat Answer:\n{answer.content}")

# ------------------------------
# Step 5: Building the Chain
# ------------------------------

def format_docs(retrieved_docs):
    """
    Format retrieved documents (a list of chunks retrieved from the vector store) into a single context string for prompting.
    """
    return "\n\n".join(doc.page_content for doc in retrieved_docs)




# Construct the chain: Retrieval → Prompt → LLM → Output
parallel_chain = RunnableParallel({
    'context': retriever | RunnableLambda(format_docs),
    'question': RunnablePassthrough()
})

parser = StrOutputParser()

main_chain = parallel_chain | prompt | llm | parser

# Sample chained invocation
result = main_chain.invoke('Is the topic of nuclear fusion discussed in this video? If yes then what was discussed?')
print(f"Chain result: {result}")


# ------------------------------
# Step 6: Cleanup (Shutdown)
# ------------------------------
try:
    # Explicitly delete objects that may hold gRPC connections
    del retriever
    del vector_store
    del llm
except Exception as e:
    print(f"Cleanup warning: {e}")

