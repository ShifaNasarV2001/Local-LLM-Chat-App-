from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import ollama

app = FastAPI()

# Allow CORS for local development (adjust origins as needed)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Message(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[Message]
    model: str
    temperature: float = 0.7
    max_tokens: int = 512
    top_k: int = 40
    top_p: float = 0.9
    repeat_penalty: float = 1.1

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: ChatRequest):
    # Prepare options for ollama
    options = {
        "temperature": request.temperature,
        "num_predict": request.max_tokens,
        "top_k": request.top_k,
        "top_p": request.top_p,
        "repeat_penalty": request.repeat_penalty,
    }
    # Call ollama model
    response_text = ""
    stream = ollama.chat(
        model=request.model,
        messages=[msg.dict() for msg in request.messages],
        stream=True,
        options=options
    )
    for chunk in stream:
        response_text += chunk['message']['content']
    return {"response": response_text} 
