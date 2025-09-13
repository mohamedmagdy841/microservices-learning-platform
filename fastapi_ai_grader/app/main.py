from fastapi import FastAPI
from .consumers import start_consumer
import threading

app = FastAPI(title="AI Quiz Grader Service")

@app.get("/")
def root():
    return {"status": "AI Grader is running"}
