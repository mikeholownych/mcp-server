from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os

app = FastAPI()

class ApprovalRequest(BaseModel):
    enhancement_id: str
    approver_email: str

# A simple in-memory store for human-approved enhancements
approved_enhancements = set()

@app.post("/api/approve-enhancement")
async def approve_enhancement(request: ApprovalRequest):
    # Here you would typically validate the requester and ensure that the enhancement_id exists.
    # Adding the enhancement_id to a list of approved enhancements
    approved_enhancements.add(request.enhancement_id)
    return {"status": "Approved"}

# Function to check if a change is risky

def is_risky_change(files_changed):
    risky_files = ['Dockerfile', 'prod_config.yml', 'core_backend.py']
    return any(file in risky_files for file in files_changed)

# Function to create a draft PR

def create_draft_pr(changed_files):
    # Here we would typically integrate with the GitHub API to create a draft PR
    pass

# Function to send notification for manual approval

def send_approval_notification(enhancement_id):
    # Here we would integrate with an email/Slack API
    pass