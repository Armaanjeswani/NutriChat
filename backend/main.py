from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline import generate_answer_with_llama2_ollama, retrieve_relevant_resources, load_embeddings, SentenceTransformer
import torch
import os
from pymongo import MongoClient
from datetime import datetime
from bson.objectid import ObjectId
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB connection (replace with your actual URI)
MONGO_URI = os.getenv("MONGO_URI")
client = MongoClient(MONGO_URI)
db = client.chatbot
chats_collection = db.chats

# Define a relevance threshold
RELEVANCE_THRESHOLD = 0.3  # Adjust this value as needed

# Load embeddings and model at startup
EMBEDDINGS_PATH = "text_chunks_and_embeddings_df.csv"
embedding_model = SentenceTransformer(model_name_or_path="all-mpnet-base-v2", device="cuda")
pages_and_chunks, embeddings = load_embeddings(EMBEDDINGS_PATH)

app = FastAPI()

# Allow CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class NewChatRequest(BaseModel):
    title: str = "New Chat"

class MessageRequest(BaseModel):
    message: str

@app.post("/chats")
def create_chat(req: NewChatRequest):
    chat_doc = {
        "title": req.title,
        "created_at": datetime.utcnow(),
        "messages": []
    }
    result = chats_collection.insert_one(chat_doc)
    return {"chat_id": str(result.inserted_id)}

@app.get("/chats")
def list_chats():
    chats = list(chats_collection.find({}, {"_id": 1, "title": 1, "created_at": 1}))
    for chat in chats:
        chat["_id"] = str(chat["_id"])
    return {"chats": chats}

@app.delete("/chats/{chat_id}")
def delete_chat(chat_id: str):
    result = chats_collection.delete_one({"_id": ObjectId(chat_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"success": True}

@app.get("/chats/{chat_id}/messages")
def get_chat_messages(chat_id: str):
    chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")
    return {"messages": chat.get("messages", [])}

@app.post("/chats/{chat_id}/messages")
def add_message(chat_id: str, req: MessageRequest):
    chat = chats_collection.find_one({"_id": ObjectId(chat_id)})
    if not chat:
        raise HTTPException(status_code=404, detail="Chat not found")

    query = req.message

    # Retrieve relevant resources
    scores, indices = retrieve_relevant_resources(
        query=query,
        embeddings=embeddings,
        model=embedding_model,
        n_resources_to_return=5
    )

    # Check for relevance based on the top score
    top_score = scores[0].item() if len(scores) > 0 else 0

    if top_score < RELEVANCE_THRESHOLD:
        answer = "I'm sorry, but that question doesn't seem to be relevant to the provided text on human nutrition. Please ask something else."
    else:
        # Generate answer using the retrieved context
        answer = generate_answer_with_llama2_ollama(
            query=query,
            indices=indices,
            pages_and_chunks=pages_and_chunks,
            model_name="llama2"
        )

    # Add user message
    user_msg = {"role": "user", "content": query}
    bot_msg = {"role": "bot", "content": answer}
    # Update chat with messages
    chats_collection.update_one(
        {"_id": ObjectId(chat_id)},
        {"$push": {"messages": {"$each": [user_msg, bot_msg]}}}
    )
    # If the chat title is still 'New Chat', update it to a summary
    if chat.get("title", "New Chat") == "New Chat":
        summary = query[:40] + ("..." if len(query) > 40 else "")
        chats_collection.update_one(
            {"_id": ObjectId(chat_id)},
            {"$set": {"title": summary}}
        )
    return {"answer": answer} 