from datetime import datetime
from typing import Optional


def missing_time(start: Optional[str], end: Optional[str]) -> bool:
    """
    Returns True when either start/end is missing or unparsable.
    Keeps planner/validator logic simple before hitting backend.
    """
    if not start or not end:
        return True

    try:
        # fromisoformat tolerates "YYYY-MM-DDTHH:MM:SS" without timezone
        datetime.fromisoformat(start)
        datetime.fromisoformat(end)
        return False
    except Exception:
        return True
