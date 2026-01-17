from typing import Any, Dict, Tuple
import requests

from app.core.config import (
    BASE_URL, CREATE_PATH,
    GET_ONE_PATH_TEMPLATE, UPDATE_PATH_TEMPLATE, DELETE_PATH_TEMPLATE,
    RETRY_NOTION_PATH_TEMPLATE,
)
from app.schemas.agent import EventDraft

def _json_or_text(resp: requests.Response) -> Dict[str, Any]:
    try:
        return resp.json()
    except Exception:
        return {"_non_json": resp.text}

def create_event(payload: EventDraft, idempotency_key: str) -> Tuple[int, Dict[str, Any]]:
    url = f"{BASE_URL}{CREATE_PATH}"
    headers = {"Content-Type": "application/json", "Idempotency-Key": idempotency_key}
    resp = requests.post(url, json=payload.model_dump(), headers=headers, timeout=20)
    return resp.status_code, _json_or_text(resp)

def get_event(event_id: int) -> Tuple[int, Dict[str, Any]]:
    url = f"{BASE_URL}{GET_ONE_PATH_TEMPLATE.format(id=event_id)}"
    resp = requests.get(url, timeout=20)
    return resp.status_code, _json_or_text(resp)

def update_event(event_id: int, payload: EventDraft, idempotency_key: str) -> Tuple[int, Dict[str, Any]]:
    url = f"{BASE_URL}{UPDATE_PATH_TEMPLATE.format(id=event_id)}"
    headers = {"Content-Type": "application/json", "Idempotency-Key": idempotency_key}
    # 若你後端是 PATCH：把 put 改成 patch
    resp = requests.put(url, json=payload.model_dump(), headers=headers, timeout=20)
    return resp.status_code, _json_or_text(resp)

def delete_event(event_id: int, idempotency_key: str) -> Tuple[int, Dict[str, Any]]:
    url = f"{BASE_URL}{DELETE_PATH_TEMPLATE.format(id=event_id)}"
    headers = {"Idempotency-Key": idempotency_key}
    resp = requests.delete(url, headers=headers, timeout=20)
    return resp.status_code, _json_or_text(resp)

def retry_notion_sync(event_id: int, idempotency_key: str) -> Tuple[int, Dict[str, Any]]:
    url = f"{BASE_URL}{RETRY_NOTION_PATH_TEMPLATE.format(id=event_id)}"
    headers = {"Idempotency-Key": idempotency_key}
    resp = requests.post(url, headers=headers, timeout=20)
    return resp.status_code, _json_or_text(resp)