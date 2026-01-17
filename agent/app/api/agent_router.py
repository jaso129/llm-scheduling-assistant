from fastapi import APIRouter, Header
from typing import Optional

from app.schemas.agent import AgentRunRequest, AgentRunResponse
from app.services.agent_service import run_agent

router = APIRouter()

@router.post("/agent/run", response_model=AgentRunResponse)
def agent_run(req: AgentRunRequest, x_request_id: Optional[str] = Header(default=None)):
    return run_agent(req, x_request_id)