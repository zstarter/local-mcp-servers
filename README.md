# Local MCP Servers (Jira + Sumo)

This package installs local MCP servers for Jira and Sumo Logic for use with Kiro / Amazon Q.

## Installation

### Linux/macOS
```bash
git clone https://github.com/zstarter/local-mcp-servers.git
cd local-mcp-servers
./install.sh
```

### Manual Installation
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Linux/macOS:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run configuration
python install.py
```

## What You'll Need

The installation script will prompt you for:

### Jira Credentials
- **Username**: Your Jira email/username
- **API Token**: Create one at: Jira Settings → Security → API tokens
- **Default Project**: Your project key (e.g., "PROJ", "DEV")

### Sumo Logic Credentials  
- **Access ID**: Found in Sumo Logic → Preferences → My Access Keys
- **Access Key**: Found in Sumo Logic → Preferences → My Access Keys
- **Default Index**: Your default search index

## After Installation

1. **Restart Kiro** to load the new MCP servers
2. The servers will be automatically configured in your MCP settings
3. You can test them using the MCP tools in Kiro

## Available MCP Tools

### Jira Tools
- `mcp_jira_list_projects` - List all available projects
- `mcp_jira_search_jira` - Search tickets using JQL
- `mcp_jira_get_jira_ticket` - Get details of a specific ticket
- `mcp_jira_create_jira_ticket` - Create a new ticket
- `mcp_jira_add_jira_comment` - Add comment to existing ticket

### Sumo Logic Tools
- `mcp_sumologic_sumologic_search_logs` - Search logs with queries

## Troubleshooting

- **Python not found**: Install Python 3.8+ first
- **Permission errors**: Run as administrator/sudo if needed
- **MCP servers not loading**: Check that Kiro was restarted after installation
- **Authentication errors**: Verify your API tokens and credentials are correct
