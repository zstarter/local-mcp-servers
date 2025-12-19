from pathlib import Path
import getpass, json, os, sys, shutil, subprocess

HOME = Path.home()
KIRO_DIR = HOME / ".kiro" / "settings"
KIRO_DIR.mkdir(parents=True, exist_ok=True)

INSTALL_DIR = Path(__file__).resolve().parent
TEMPLATE = INSTALL_DIR / "mcp.json.template"
TARGET = KIRO_DIR / "mcp.json"

def detect_python_command():
    """Detect the correct Python command to use"""
    # First, try to use the same Python that's running this script
    current_python = sys.executable
    if current_python and Path(current_python).exists():
        return current_python
    
    # Fallback: check common Python commands
    for cmd in ["python3", "python"]:
        if shutil.which(cmd):
            try:
                # Verify it's Python 3.6+
                result = subprocess.run([cmd, "-c", "import sys; exit(0 if sys.version_info >= (3, 6) else 1)"], 
                                      capture_output=True, timeout=5)
                if result.returncode == 0:
                    return cmd
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue
    
    # Last resort: return python and hope for the best
    return "python"

def ask(prompt, secret=False):
    if secret:
        return getpass.getpass(f"{prompt}: ")
    return input(f"{prompt}: ").strip()

# Detect Python command
python_cmd = detect_python_command()
print(f"🐍 Detected Python command: {python_cmd}")

print("🔧 Configuring MCP servers for Jira and Sumo Logic...")
print(f"📁 Install directory: {INSTALL_DIR}")
print(f"📄 Target config: {TARGET}")
print()

values = {
    "PYTHON_CMD": python_cmd,
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
