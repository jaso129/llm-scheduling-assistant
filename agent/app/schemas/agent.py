from typing import Optional, Any, Dict, Literal, List
from pydantic import BaseModel, Field

class EventDraft(BaseModel):
    title: Optional[str] = Field(None, description="short event title")
    notes: Optional[str] = Field("", description="optional notes")
    startDate: Optional[str] = Field(None, description="ISO-8601 local datetime")
    endDate: Optional[str] = Field(None, description="ISO-8601 local datetime")

ActionType = Literal[
    "create_event",
    "get_event",
    "update_event",
    "delete_event",
    "retry_notion_sync",
    "none"
]

class AgentPlan(BaseModel):
    action: ActionType = "none"
    event_id: Optional[int] = None
    event: Optional[EventDraft] = None
    need_clarification: bool = False
    questions: Optional[List[str]] = None

class AgentRunRequest(BaseModel):
    user_text: str
    confirm: bool = False

    # client 可補
    event_id: Optional[int] = None
    title: Optional[str] = None
    notes: Optional[str] = None
    startDate: Optional[str] = None
    endDate: Optional[str] = None

    idempotency_key: Optional[str] = None

class AgentRunResponse(BaseModel):
    trace_id: str
    action: ActionType
    need_clarification: bool
    questions: Optional[List[str]] = None

    draft: Optional[EventDraft] = None

    backend_status_code: Optional[int] = None
    backend_response: Optional[Dict[str, Any]] = None