#!/usr/bin/env python3

import asyncio
import os
import time
import sys
import requests
from typing import Any, Dict, List

from requests.auth import HTTPBasicAuth
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

SUMO_ACCESS_ID = os.getenv("SUMO_ACCESS_ID")
SUMO_ACCESS_KEY = os.getenv("SUMO_ACCESS_KEY")
SUMO_API_BASE = "https://api.sumologic.com/api"
DEFAULT_INDEX = os.getenv("SUMO_DEFAULT_INDEX")

if not DEFAULT_INDEX:
    raise RuntimeError("SUMO_DEFAULT_INDEX is not set.")

def _check_credentials():
    if not SUMO_ACCESS_ID or not SUMO_ACCESS_KEY:
        raise RuntimeError("SUMO_ACCESS_ID / SUMO_ACCESS_KEY are not set.")

def _auth():
    return HTTPBasicAuth(SUMO_ACCESS_ID, SUMO_ACCESS_KEY)

def start_search_job(query: str, from_time: str, to_time: str) -> str:
    url = f"{SUMO_API_BASE}/v1/search/jobs"
    payload = {
        "query": query,
        "from": from_time,
        "to": to_time,
        "timeZone": "UTC"
    }

    resp = requests.post(
        url,
        json=payload,
        auth=_auth(),
        headers={"Content-Type": "application/json"},
        timeout=30
    )

    if not resp.ok:
        raise RuntimeError(f"Failed to start search job: {resp.status_code} - {resp.text}")

    data = resp.json()
    job_id = data.get("id")
    if not job_id:
        raise RuntimeError(f"Missing 'id' in search job response: {data}")

    return job_id

def wait_for_job_done(job_id: str) -> Dict[str, Any]:
    url = f"{SUMO_API_BASE}/v1/search/jobs/{job_id}"

    for _ in range(60):
        resp = requests.get(url, auth=_auth(), timeout=30)

        if not resp.ok:
            raise RuntimeError(f"Failed to poll job status: {resp.status_code} - {resp.text}")

        data = resp.json()
        state = data.get("state", "")

        if state in {"DONE GATHERING RESULTS", "CANCELLED", "ERROR"}:
            return data

        time.sleep(1)

    raise TimeoutError(f"Timed out waiting for job {job_id}.")

def get_search_messages(job_id: str, limit: int):
    limit = max(1, min(2000, limit))

    url = f"{SUMO_API_BASE}/v1/search/jobs/{job_id}/messages"
    params = {"offset": 0, "limit": limit}

    resp = requests.get(url, params=params, auth=_auth(), timeout=60)

    if not resp.ok:
        raise RuntimeError(f"Failed to fetch messages: {resp.status_code} - {resp.text}")

    return resp.json().get("messages", [])

server = Server("sumologic-mcp")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    return [
        Tool(
            name="sumologic_search_logs",
            description=(
                "Run a Sumo Logic search job and return messages. "
                f"Automatically prefixes '{DEFAULT_INDEX}' to queries."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string"},
                    "from": {"type": "string"},
                    "to": {"type": "string"},
                    "limit": {"type": "integer", "minimum": 1, "maximum": 2000}
                },
                "required": ["query", "from", "to"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]):
    if name != "sumologic_search_logs":
        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    _check_credentials()

    raw_query = arguments.get("query", "").strip()
    from_time = arguments.get("from", "")
    to_time = arguments.get("to", "")
    limit = arguments.get("limit", 200)

    query = f"{DEFAULT_INDEX} {raw_query}"

    job_id = start_search_job(query, from_time, to_time)
    status = wait_for_job_done(job_id)

    if status.get("state") != "DONE GATHERING RESULTS":
        return [TextContent(type="text", text=f"Job ended with state={status.get('state')}")]

    messages = get_search_messages(job_id, limit)

    output_lines = []
    for entry in messages:
        m = entry.get("map", {}) or {}
        ts = m.get("_messagetime", "")
        raw = m.get("_raw", "")
        output_lines.append(f"{ts} | {raw}")

    output = "\n".join(output_lines) if output_lines else "No messages returned."
    return [TextContent(type="text", text=output)]

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options(),
        )

if __name__ == "__main__":
    asyncio.run(main())
