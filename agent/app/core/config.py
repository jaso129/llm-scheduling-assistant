import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("AGENT_BASE_URL")

CREATE_PATH = os.getenv("AGENT_CREATE_PATH", "/api/events")
GET_ONE_PATH_TEMPLATE = os.getenv("AGENT_GET_ONE_PATH_TEMPLATE", "/api/events/{id}")
UPDATE_PATH_TEMPLATE = os.getenv("AGENT_UPDATE_PATH_TEMPLATE", "/api/events/{id}")
DELETE_PATH_TEMPLATE = os.getenv("AGENT_DELETE_PATH_TEMPLATE", "/api/events/{id}")
RETRY_NOTION_PATH_TEMPLATE = os.getenv("AGENT_RETRY_NOTION_PATH_TEMPLATE", "/api/events/{id}/sync/notion")

MODEL = os.getenv("AGENT_MODEL", "gpt-4o-mini-2024-07-18")
TZ = os.getenv("AGENT_TZ", "Asia/Taipei")
TODAY = os.getenv("AGENT_TODAY", "2026-01-14")

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")