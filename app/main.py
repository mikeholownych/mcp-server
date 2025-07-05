from fastapi import FastAPI, HTTPException, Request
import os
import httpx

app = FastAPI()

NOTION_API_URL = "https://api.notion.com/v1/pages"
AIRTABLE_API_URL = "https://api.airtable.com/v0/appId/Table"
NOTION_API_TOKEN = os.getenv("NOTION_API_TOKEN")
AIRTABLE_API_TOKEN = os.getenv("AIRTABLE_API_TOKEN")

headers_notion = {
    "Authorization": f"Bearer {NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-05-13"
}

headers_airtable = {
    "Authorization": f"Bearer {AIRTABLE_API_TOKEN}",
    "Content-Type": "application/json"
}

@app.post("/api/webhook/notion")
async def webhook_notion(request: Request):
    if not NOTION_API_TOKEN:
        raise HTTPException(status_code=500, detail="Notion API token not configured.")
    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(NOTION_API_URL, headers=headers_notion, json=data)
            response.raise_for_status()
        return {"message": "Notion updated successfully", "status": response.status_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/webhook/airtable")
async def webhook_airtable(request: Request):
    if not AIRTABLE_API_TOKEN:
        raise HTTPException(status_code=500, detail="Airtable API token not configured.")
    try:
        data = await request.json()
        async with httpx.AsyncClient() as client:
            response = await client.post(AIRTABLE_API_URL, headers=headers_airtable, json=data)
            response.raise_for_status()
        return {"message": "Airtable updated successfully", "status": response.status_code}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
