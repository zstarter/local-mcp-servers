#!/usr/bin/env python3
import os
from pathlib import Path

kiro_settings = Path.home() / ".kiro" / "settings"
kiro_settings.mkdir(parents=True, exist_ok=True)

template = Path("mcp.json.template").read_text()
target = kiro_settings / "mcp.json"

if target.exists():
    print("mcp.json already exists, not overwriting.")
else:
    target.write_text(template)
    print("mcp.json created at", target)
