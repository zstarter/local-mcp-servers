import asyncio
import os
import subprocess
import time
import requests
import json
import sys
from requests.auth import HTTPBasicAuth
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

app = Server("jira_mcp_server")


def install_mcp_config():
    config_path = os.path.expanduser("~/.kiro/settings/mcp.json")
    os.makedirs(os.path.dirname(config_path), exist_ok=True)

    script_path = os.path.abspath(__file__)

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception:
            config = {"mcpServers": {}}
    else:
        config = {"mcpServers": {}}

    server_config = {
        "command": "python3",
        "args": [script_path],
        "cwd": os.path.dirname(script_path),
        "disabled": False,
        "autoApprove": [
            "create_jira_ticket",
            "get_jira_ticket",
            "list_projects",
            "search_jira",
            "add_jira_comment",
        ],
    }

    config.setdefault("mcpServers", {})
    config["mcpServers"]["jira"] = server_config

    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)


def get_credentials():
    username = os.environ.get("JIRA_USERNAME")
    jira_token = os.environ.get("JIRA_TOKEN")

    if username and jira_token:
        return username, jira_token

    try:
        cred_path = os.path.join(os.environ.get("HOME", ""), ".hooks", "credentials")
        with open(cred_path, "r") as f:
            jira_token = f.read().strip()

        process = subprocess.Popen(
            ["git", "config", "user.email"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        time.sleep(1)
        stdout, _ = process.communicate()
        username = stdout.strip()

        if not username:
            raise Exception("No username found from git config user.email")

        return username, jira_token

    except Exception as e:
        raise Exception(f"Unable to get Jira credentials: {str(e)}")


def make_adf_description(text: str) -> dict:
    return {
        "type": "doc",
        "version": 1,
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    }
                ],
            }
        ],
    }


def resolve_account_id(auth: HTTPBasicAuth, email: str | None) -> str | None:
    if not email:
        return None

    url = "https://infor.atlassian.net/rest/api/3/user/search"
    params = {"query": email, "maxResults": 1}
    try:
        r = requests.get(url, auth=auth, params=params)
        if r.status_code != 200:
            return None
        users = r.json()
        if not users:
            return None
        return users[0].get("accountId")
    except Exception:
        return None


def get_current_user_account_id(auth: HTTPBasicAuth) -> str | None:
    url = "https://infor.atlassian.net/rest/api/3/myself"
    try:
        r = requests.get(url, auth=auth)
        if r.status_code != 200:
            return None
        data = r.json()
        return data.get("accountId")
    except Exception:
        return None


@app.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="get_jira_ticket",
            description="Get details of a Jira ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                },
                "required": ["issue_key"],
            },
        ),
        Tool(
            name="search_jira",
            description="Search Jira using JQL",
            inputSchema={
                "type": "object",
                "properties": {
                    "jql": {"type": "string"},
                    "maxResults": {"type": "integer", "default": 10},
                },
                "required": ["jql"],
            },
        ),
        Tool(
            name="list_projects",
            description="Lists all Jira project keys available",
            inputSchema={"type": "object", "properties": {}},
        ),
        Tool(
            name="create_jira_ticket",
            description="Create a new Jira ticket and optionally assign it",
            inputSchema={
                "type": "object",
                "properties": {
                    "project_key": {
                        "type": "string",
                        "description": "Project key (defaults to JIRA_DEFAULT_PROJECT env)",
                    },
                    "summary": {"type": "string"},
                    "description": {"type": "string"},
                    "issue_type": {"type": "string", "default": "Task"},
                    "assignee_email": {"type": "string"},
                    "assignee_account_id": {"type": "string"},
                    "assign_to_current_user": {"type": "boolean", "default": False},
                },
                "required": ["summary", "description"],
            },
        ),
        Tool(
            name="add_jira_comment",
            description="Add a comment to an existing Jira ticket",
            inputSchema={
                "type": "object",
                "properties": {
                    "issue_key": {"type": "string"},
                    "comment": {"type": "string"},
                },
                "required": ["issue_key", "comment"],
            },
        ),
    ]


@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        username, jira_token = get_credentials()
        auth = HTTPBasicAuth(username, jira_token)

        if name == "get_jira_ticket":
            url = f"https://infor.atlassian.net/rest/api/3/issue/{arguments['issue_key']}"
            r = requests.get(url, auth=auth)

            if r.status_code == 200:
                data = r.json()
                fields = data.get("fields", {})
                summary = fields.get("summary", "")
                status = fields.get("status", {}).get("name", "")
                return [
                    TextContent(
                        type="text",
                        text=f"{data.get('key')}: {summary} [{status}]",
                    )
                ]
            return [TextContent(type="text", text=r.text)]

        elif name == "search_jira":
            url = "https://infor.atlassian.net/rest/api/3/search/jql"
            payload = {
                "jql": arguments["jql"],
                "maxResults": arguments.get("maxResults", 10),
                "fields": ["summary", "status"],
            }

            r = requests.post(url, auth=auth, json=payload)

            if r.status_code == 200:
                issues = r.json().get("issues", [])
                if not issues:
                    return [TextContent(type="text", text="No issues found")]

                out = []
                for i in issues:
                    key = i.get("key")
                    fields = i.get("fields", {})
                    summary = fields.get("summary", "")
                    status = fields.get("status", {}).get("name", "")
                    out.append(f"{key}: {summary} [{status}]")

                return [TextContent(type="text", text="\n".join(out))]

            return [TextContent(type="text", text=r.text)]

        elif name == "list_projects":
            r = requests.get(
                "https://infor.atlassian.net/rest/api/3/project/search", auth=auth
            )
            values = r.json().get("values", [])
            return [
                TextContent(
                    type="text",
                    text="\n".join(f"{p['key']} - {p['name']}" for p in values),
                )
            ]

        elif name == "create_jira_ticket":
            project_key = arguments.get("project_key") or os.getenv("JIRA_DEFAULT_PROJECT")
            if not project_key:
                return [
                    TextContent(
                        type="text",
                        text="No Jira project specified. Set project_key or JIRA_DEFAULT_PROJECT.",
                    )
                ]

            create_url = "https://infor.atlassian.net/rest/api/3/issue"
            fields = {
                "project": {"key": project_key},
                "summary": arguments["summary"],
                "description": make_adf_description(arguments["description"]),
                "issuetype": {"name": arguments.get("issue_type", "Task")},
            }

            r = requests.post(create_url, auth=auth, json={"fields": fields})

            if r.status_code not in (200, 201):
                return [TextContent(type="text", text=r.text)]

            issue_key = r.json().get("key")

            assignee_account_id = arguments.get("assignee_account_id")
            assignee_email = arguments.get("assignee_email")
            assign_to_current_user = arguments.get("assign_to_current_user", False)

            if not assignee_account_id and assignee_email:
                assignee_account_id = resolve_account_id(auth, assignee_email)

            if not assignee_account_id and assign_to_current_user:
                assignee_account_id = get_current_user_account_id(auth)

            if assignee_account_id and issue_key:
                requests.put(
                    f"https://infor.atlassian.net/rest/api/3/issue/{issue_key}/assignee",
                    auth=auth,
                    json={"accountId": assignee_account_id},
                )

            return [TextContent(type="text", text=f"Created: {issue_key}")]

        elif name == "add_jira_comment":
            issue_key = arguments["issue_key"]
            comment_text = arguments["comment"]

            url = f"https://infor.atlassian.net/rest/api/3/issue/{issue_key}/comment"
            payload = {"body": make_adf_description(comment_text)}

            r = requests.post(url, auth=auth, json=payload)

            if r.status_code in (200, 201):
                return [
                    TextContent(
                        type="text",
                        text=f"Comment added to {issue_key}",
                    )
                ]

            return [TextContent(type="text", text=r.text)]

        return [TextContent(type="text", text="Unknown tool")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {str(e)}")]


async def main():
    async with stdio_server() as (reader, writer):
        await app.run(reader, writer, app.create_initialization_options())


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--install":
        install_mcp_config()
    else:
        asyncio.run(main())
