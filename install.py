from pathlib import Path
import getpass, json, os

HOME = Path.home()
KIRO_DIR = HOME / ".kiro" / "settings"
KIRO_DIR.mkdir(parents=True, exist_ok=True)

INSTALL_DIR = Path(__file__).resolve().parent
TEMPLATE = INSTALL_DIR / "mcp.json.template"
TARGET = KIRO_DIR / "mcp.json"

def ask(prompt, secret=False):
    if secret:
        return getpass.getpass(f"{prompt}: ")
    return input(f"{prompt}: ").strip()

print("🔧 Configuring MCP servers for Jira and Sumo Logic...")
print(f"📁 Install directory: {INSTALL_DIR}")
print(f"📄 Target config: {TARGET}")
print()

values = {
    "INSTALL_DIR": str(INSTALL_DIR).replace("\\", "\\\\"),  # Escape backslashes for Windows
    "JIRA_USERNAME": ask("Jira username"),
    "JIRA_TOKEN": ask("Jira API token", secret=True),
    "JIRA_DEFAULT_PROJECT": ask("Default Jira project key"),
    "SUMO_ACCESS_ID": ask("Sumo Access ID"),
    "SUMO_ACCESS_KEY": ask("Sumo Access Key", secret=True),
    "SUMO_DEFAULT_INDEX": ask("Default Sumo index"),
}

print("\n🔄 Processing template...")
content = TEMPLATE.read_text()
for k, v in values.items():
    content = content.replace(f"{{{{{k}}}}}", v)

TARGET.write_text(content)
print(f"✅ MCP config written to {TARGET}")
print("\n🎉 Installation complete!")
print("💡 Restart Kiro to load the new MCP servers.")
