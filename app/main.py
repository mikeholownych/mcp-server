from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict

app = FastAPI()

router = APIRouter()

class EnhancementRequest(BaseModel):
    summary: str
    details: str

# Use dependency injection for a real system; for demo, use a global dict
agent_statuses: Dict[str, Dict[str, str]] = {
    'code': {'status': 'pending', 'log': ''},
    'test': {'status': 'pending', 'log': ''},
    'docs': {'status': 'pending', 'log': ''},
    'secops': {'status': 'pending', 'log': ''}
}

@router.get("/enhancement-log", tags=["Enhancement"])
async def get_enhancement_log():
    """Return latest agent statuses."""
    return agent_statuses

@router.post("/enhancement", tags=["Enhancement"])
async def handle_enhancement(request: EnhancementRequest):
    """
    Simulate internal processing by each agent.
    If secops fails, return success=False.
    """
    for agent in agent_statuses:
        if agent != 'secops':
            agent_statuses[agent]['status'] = 'passed'
            agent_statuses[agent]['log'] = f'Simulated log for {agent} agent. Enhancement: {request.summary}'
        else:
            agent_statuses[agent]['status'] = 'failed'
            agent_statuses[agent]['log'] = f'Simulated log for {agent} agent. Enhancement: {request.summary} [FAILED]'

    all_passed = all(status['status'] == 'passed' for status in agent_statuses.values())
    return {'success': all_passed, 'statuses': agent_statuses}

app.include_router(router, prefix='/api')
