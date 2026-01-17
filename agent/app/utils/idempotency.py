import hashlib
from typing import Optional
from app.core.config import TZ

def build_idempotency_key(user_text: str, action: str, event_id: Optional[int], start: Optional[str], end: Optional[str]) -> str:
    raw = f"{action}|{user_text}|{event_id or ''}|{start or ''}|{end or ''}|{TZ}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()