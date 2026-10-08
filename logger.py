import json
import time
import asyncio
import httpx
from config import LOCAL_LOG_PATH, LOG_SHIP_URL, LOG_SHIP_TOKEN

_client = httpx.AsyncClient(timeout=5.0)


def _write_local(entry: dict):
    with open(LOCAL_LOG_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")


async def _ship(entry: dict):
    if not LOG_SHIP_URL:
        return
    try:
        await _client.post(
            LOG_SHIP_URL,
            json=entry,
            headers={"Authorization": f"Bearer {LOG_SHIP_TOKEN}"},
        )
    except Exception:
        pass  # never let log shipping break the proxy itself


def log_event(session_id: str, direction: str, payload: dict):
    entry = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "session_id": session_id,
        "direction": direction,   # "inbound" or "outbound"
        "raw_payload": payload,
    }
    _write_local(entry)
    asyncio.create_task(_ship(entry))   # fire-and-forget, non-blocking