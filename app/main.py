from fastapi import FastAPI, Request
from app.routes.api import router

app = FastAPI(title="MCP Content Processor")
app.include_router(router, prefix="/api")

@app.get("/")
def health_check():
    return {"status": "ok"}
