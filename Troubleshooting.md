# 🛠️ Troubleshooting Quick Hits — Utility Billing Project

Common issues & fixes for Jupyter, VS Code, and `uv` workflows.

---

## 🔎 Environment Issues

### 1. Wrong Python showing up
```bash
python -c "import sys; print(sys.executable)"
# Expected: .../utility-billing/.venv/Scripts/python.exe
# If not:
source .venv/Scripts/activate
# In VS Code: Ctrl+Shift+P → Python: Select Interpreter → .venv
```

### 2. Jupyter says "command not found"
```bash
# Cause: venv not active.
# Fix:
source .venv/Scripts/activate
```

### 3. Notebook can't find a package
```bash
# Cause: Package not installed in this venv.
# Fix:
uv sync                 # ensure lock is applied
uv add <package_name>   # if missing
```

### 4. Kernel missing from JupyterLab
```bash
# Cause: ipykernel not registered.
# Fix:
source .venv/Scripts/activate
python -m ipykernel install --user \
  --name utility-billing \
  --display-name "Python (utility-billing)"
```

### 5. Kernel stuck on wrong interpreter in VS Code
```bash
# Fix:
# Top-right kernel picker → Python (utility-billing)
# Or: Ctrl+Shift+P → Python: Select Interpreter → .venv
```

## 💻 VS Code Issues
### 6. PowerShell activatiron error
```lua
Activate.ps1 cannot be loaded because running scripts is disabled...
```
```bash
#Harmless, but fix with:
```
```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

### 7. Ruff warning in bottom-right corner
```bash
# Fix: add a Ruff section to pyproject.toml
[tool.ruff]
line-length = 100
```

## 🔄 Dependency Issues
### 8. Resetting the environment
```bash
rm -rf .venv
uv venv
source .venv/Scripts/activate
uv sync
```

### 9. Forcing Updates
```bash
uv lock --upgrade
uv sync
```

### 10. Checking what's installed
```bash
uv pip list
```

