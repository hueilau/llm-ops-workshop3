# Importing Necessary Libraries
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from transformers import pipeline
import uvicorn

# Creating the FastAPI Application
app = FastAPI()

# Initializing the Question-Answering Pipeline
try:
    qa_pipeline = pipeline("question-answering", model="distilbert-base-uncased-distilled-squad")
except Exception as e:
    # Handle model loading errors
    qa_pipeline = None
    print(f"Error loading QA pipeline: {e}")


# Defining Data Models
class ChatRequest(BaseModel):
    question: str
    context: str

class ChatResponse(BaseModel):
    answer: str

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "FastAPI QA Service"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to FastAPI Question-Answering Service"}

# Creating the /chat endpoint
@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if qa_pipeline is None:
        raise HTTPException(status_code=503, detail="Question-Answering model is not available.")
    try:
        result = qa_pipeline(question=request.question, context=request.context)
        return ChatResponse(answer=result['answer'])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Running the app server
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)