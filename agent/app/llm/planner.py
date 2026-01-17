from openai import OpenAI
from app.core.config import MODEL, TZ, TODAY, OPENAI_API_KEY
from app.schemas.agent import AgentPlan
import os

_client = OpenAI(api_key=OPENAI_API_KEY)

def make_plan(user_text: str) -> AgentPlan:
    system = (
        "You are an assistant that chooses the correct backend tool (action) and arguments.\n"
        f"Timezone: {TZ}. Today is {TODAY}.\n\n"
        "Available actions:\n"
        "1) create_event: create a new event.\n"
        "2) get_event: get a single event by event_id.\n"
        "3) update_event: update an existing event by event_id.\n"
        "4) delete_event: delete an event by event_id.\n"
        "5) retry_notion_sync: retry syncing an existing event to Notion by event_id.\n"
        "6) none: if no backend action is needed.\n\n"
        "Rules:\n"
        "- If action requires event_id and user didn't provide it, set need_clarification=true and ask for event_id.\n"
        "- For create/update, output an 'event' object with fields: title, notes, startDate, endDate.\n"
        "- Datetimes must be ISO-8601 local datetime: YYYY-MM-DDTHH:MM:SS.\n"
        "- If start/end time is missing or ambiguous for create/update, set need_clarification=true and set startDate/endDate to null.\n"
        "- Output JSON only.\n"
    )
    print("[LLM] calling OpenAI...")
    resp = _client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
        text_format=AgentPlan,
    )
    print("[LLM] OpenAI returned, response_id =", getattr(resp, "id", None))
    return resp.output_parsed