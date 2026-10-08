import asyncio
import json
import sys
import uuid
from config import TARGET_CMD, TARGET_ARGS
# from filters import evaluate
from logger import log_event

SESSION_ID = str(uuid.uuid4())


def make_rejection(original: dict, decision) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": original.get("id"),
        "error": {
            "code": -32001,
            "message": f"Blocked by proxy filter: {decision.matched_rule}",
        },
    }


async def pump_inbound(reader, writer):
    """Host -> proxy -> target"""
    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            payload = json.loads(line)
            log_event(SESSION_ID, "inbound", payload)
        except json.JSONDecodeError:
            pass  # still forward even if we can't parse it for logging
        writer.write(line)
        await writer.drain()


async def pump_outbound(reader):
    """Target -> proxy -> host"""
    while True:
        line = await reader.readline()
        if not line:
            break
        try:
            payload = json.loads(line)
            log_event(SESSION_ID, "outbound", payload)
        except json.JSONDecodeError:
            pass
        sys.stdout.write(line.decode() if isinstance(line, bytes) else line)
        sys.stdout.flush()


async def stdin_reader():
    loop = asyncio.get_event_loop()
    reader = asyncio.StreamReader()
    protocol = asyncio.StreamReaderProtocol(reader)
    await loop.connect_read_pipe(lambda: protocol, sys.stdin)
    return reader


async def main():
    proc = await asyncio.create_subprocess_exec(
        TARGET_CMD, *TARGET_ARGS,
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
    )
    host_reader = await stdin_reader()

    await asyncio.gather(
        pump_inbound(host_reader, proc.stdin),
        pump_outbound(proc.stdout),
    )


if __name__ == "__main__":
    asyncio.run(main())
