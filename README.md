# Local MCP Servers (Jira + Sumo)

This package installs local MCP servers for Jira and Sumo Logic for use with Kiro / Amazon Q.

## Installation

```bash
git clone <repo>
cd local-mcp-servers
./install.sh
```

## Environment Variables

Set the following before restarting Kiro:

- LOCAL_MCP_DIR
- JIRA_USERNAME
- JIRA_TOKEN
- JIRA_DEFAULT_PROJECT
- SUMO_ACCESS_ID
- SUMO_ACCESS_KEY
- SUMO_DEFAULT_INDEX

Restart Kiro after setup.
