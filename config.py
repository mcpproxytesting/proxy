import os

TARGET_CMD = os.environ.get("TARGET_CMD", "python")
TARGET_ARGS = os.environ.get("TARGET_ARGS", "../Testing-MCP/server.py").split()
LOCAL_LOG_PATH = os.environ.get("LOCAL_LOG_PATH", "./logs/proxy.jsonl")
LOG_SHIP_URL = os.environ.get("LOG_SHIP_URL", "")
LOG_SHIP_TOKEN = os.environ.get("LOG_SHIP_TOKEN", "")
