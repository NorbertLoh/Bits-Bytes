from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn
from rag_pipeline import run_rag_pipeline

app = FastAPI(title="RAG Pipeline API")

# Pydantic model for request body
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
async def ask_question(request: QuestionRequest):
    """
    Endpoint to ask a question to the RAG pipeline.
    """
    try:
        answer = run_rag_pipeline(request.question)
        return {"question": request.question, "answer": answer}
    except Exception as e:
        # Basic error handling
        return {"error": str(e), "message": "An error occurred while processing your request."}, 500