from fastapi import FastAPI
from app.routes.api import router

app = FastAPI(
    title="MCP Content Processor",
    description="Ethical AI Insider - Platform & Pillar Optimized Content Engine"
)

app.include_router(router, prefix="/api")
