import os
import json
import requests
from typing import Optional
from pydantic import BaseModel, Field
from openai import OpenAI
from dotenv import load_dotenv
load_dotenv()

# ====== 你的後端設定 ======
BASE_URL = os.getenv("AGENT_BASE_URL")
CREATE_PATH = os.getenv("AGENT_CREATE_PATH", "/api/events")
RETRY_NOTION_PATH_TEMPLATE = os.getenv("AGENT_RETRY_NOTION_PATH_TEMPLATE", "/api/events/{id}/sync/notion")

# ====== LLM 設定 ======
MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini-2024-07-18")  # 便宜、穩定 [oai_citation:1‡OpenAI 平台](https://platform.openai.com/docs/pricing?utm_source=chatgpt.com)
TZ = "Asia/Taipei"
TODAY = "2025-12-26"  # 你目前時間軸（台北）

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class EventDraft(BaseModel):
    title: str = Field(..., description="short event title")
    notes: Optional[str] = Field("", description="optional notes")
    startDate: Optional[str] = Field(None, description="ISO-8601 local datetime like 2025-12-26T19:00:00")
    endDate: Optional[str] = Field(None, description="ISO-8601 local datetime like 2025-12-26T20:00:00")

def llm_extract_event(user_text: str) -> EventDraft:
    system = (
        "You extract scheduling info and output JSON for an API.\n"
        f"Timezone: {TZ}. Today is {TODAY}.\n"
        "Return ISO-8601 local datetimes: YYYY-MM-DDTHH:MM:SS.\n"
        "If start/end time is ambiguous or missing, set startDate/endDate to null.\n"
        "JSON only."
    )
    resp = client.responses.parse(
        model=MODEL,
        input=[
            {"role": "system", "content": system},
            {"role": "user", "content": user_text},
        ],
        text_format=EventDraft,  # Structured Outputs via schema [oai_citation:2‡OpenAI 平台](https://platform.openai.com/docs/guides/structured-outputs)
    )
    return resp.output_parsed

def post_json(url: str, payload: dict) -> requests.Response:
    return requests.post(url, json=payload, timeout=20)

def retry_notion(event_id: int) -> requests.Response:
    url = f"{BASE_URL}{RETRY_NOTION_PATH_TEMPLATE.format(id=event_id)}"
    return requests.post(url, timeout=20)

def should_retry(status: Optional[str]) -> bool:
    return (status or "").upper() == "FAILED"

def parse_create_response(resp: requests.Response) -> dict:
    # 你之前用過多種 DTO 命名，這裡先直接回傳 json 讓你看清楚
    try:
        return resp.json()
    except Exception:
        return {"_non_json": resp.text}

def main():
    print(f"🧠 LLM CLI Agent ready  BASE_URL={BASE_URL}  CREATE_PATH={CREATE_PATH}  MODEL={MODEL}")
    user_text = input("\n> 未來的計劃？\n> ").strip()

    draft = llm_extract_event(user_text)
    payload = draft.model_dump()

    print("\n🔎 LLM parsed payload (將送往後端):")
    print(json.dumps(payload, ensure_ascii=False, indent=2))

    # 若 LLM 無法確定時間，就讓你手動補（避免亂寫進 DB）
    if payload["startDate"] is None:
        payload["startDate"] = input("startDate 缺失，請補 (YYYY-MM-DDTHH:MM:SS): ").strip()
    if payload["endDate"] is None:
        payload["endDate"] = input("endDate 缺失，請補 (YYYY-MM-DDTHH:MM:SS): ").strip()

    ok = input("\n要送出建立事件嗎？(y/n): ").strip().lower()
    if ok not in ("y", "yes"):
        print("👌 已取消（沒有呼叫後端）")
        return

    create_url = f"{BASE_URL}{CREATE_PATH}"
    resp = post_json(create_url, payload)
    print(f"\n📌 POST {create_url} -> HTTP {resp.status_code}")
    data = parse_create_response(resp)
    print("↩︎ response:", json.dumps(data, ensure_ascii=False, indent=2))

    if resp.status_code >= 400:
        return

    event_id = data.get("eventId") or data.get("id") or data.get("event_id")
    try:
        event_id = int(event_id) if event_id is not None else None
    except Exception:
        event_id = None

    notion_status = data.get("notionSyncStatus") or data.get("notion_status")
    if event_id and should_retry(notion_status):
        ans = input("\n⚠️ Notion FAILED，要不要 retry？(y/n): ").strip().lower()
        if ans in ("y", "yes"):
            r = retry_notion(event_id)
            print(f"🔄 Retry -> HTTP {r.status_code}")
            print("↩︎ retry response:", r.text)

if __name__ == "__main__":
    main()