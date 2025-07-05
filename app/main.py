from fastapi import FastAPI
from app.routes.api import router

app = FastAPI(
    title="MCP Content Processor",
    description="Ethical AI Insider - Platform & Pillar Optimized Content Engine",
    version="1.1.0"
)

app.include_router(router, prefix="/api")

@app.get("/", tags=["Health"])
def health_check():
    """
    Health check endpoint for uptime monitoring.
    """
    return {"status": "ok"}
