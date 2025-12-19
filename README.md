# MCP Servers (Jira + Sumo)

This repository provides **standalone local MCP servers** for **Amazon Q / Kiro CLI**.

---

## Prerequisites

- Amazon Q / Kiro CLI installed and working
  ```bash
  kiro --version
  ```

- Python 3
  ```bash
  python3 --version
  ```

- Git

- Credentials ready

### Jira
- JIRA_USERNAME
- JIRA_TOKEN
- JIRA_DEFAULT_PROJECT

### Sumo Logic
- SUMO_ACCESS_ID
- SUMO_ACCESS_KEY
- SUMO_DEFAULT_INDEX

Sumo API base is fixed to:
```
https://api.sumologic.com/api
```

---

## Installation

```bash
git clone ssh://git@oxfordssh.awsdev.infor.com:7999/EdwinReginoJr/local-mcp-servers.git
cd local-mcp-servers
./install.sh
```

What this does:
- Creates a local Python virtual environment (.venv)
- Installs required Python packages
- Prompts for credentials
- Generates ~/.kiro/settings/mcp.json from a template

Restart Amazon Q / Kiro CLI after install.

---

## Updating

```bash
git pull
./install.sh
```

---

## Troubleshooting

Preferred:
```bash
rm -rf .venv
./install.sh
```

Last resort (local machine only):
```bash
sudo pip3 install --break-system-packages mcp requests
sudo pip3 install --break-system-packages --ignore-installed typing_extensions
```

If using last resort, update mcp.json to use:
```json
"command": "python3"
```
