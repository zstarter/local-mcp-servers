#!/usr/bin/env powershell
# PowerShell installation script for Windows

Write-Host "🚀 Installing Local MCP Servers..." -ForegroundColor Green

# Check if Python is available
try {
    $pythonVersion = python --version 2>$null
    Write-Host "✅ Found Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found. Please install Python 3.8+ first." -ForegroundColor Red
    exit 1
}

Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv .venv

Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

Write-Host "⬇️  Installing dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Write-Host "⚙️  Running configuration..." -ForegroundColor Yellow
python install.py

Write-Host "🎉 Installation complete!" -ForegroundColor Green
Write-Host "💡 Please restart Kiro to load the new MCP servers." -ForegroundColor Cyan