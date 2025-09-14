from fastapi import FastAPI
from .routes import router

app = FastAPI(title="Payment Worker Service")
app.include_router(router, prefix="/payments", tags=["payments"])

@app.get("/")
def root():
    return {"status": "Payment Service is running"} 
