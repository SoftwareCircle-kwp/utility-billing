# 🧰 Daily Workflow Cheat Sheet — Utility Billing Project

## Start your day
```bash
# 1) Go to project
cd ~/projects/work/utility-billing

# 2) Activate env (Git Bash)
source .venv/Scripts/activate

# 3) Sync exact deps from lock (safe no-op if already synced)
uv sync
```

## Open tools
```bash
#Launch JupyterLab in browser
jupyter lab

# OR open VS Code workspace (remembers .venv)
code .
```
## Manage Dependencies
```bash
# Add package (updates pyproject + uv.lock + installs)
uv add pandas matplotlib

# Remove package
uv remove pandas

# Upgrade everything to latest allowed
uv lock --upgrade
uv sync
```
## Reset environment
```bash
# Recreate clean env if things get weird
rm -rf .venv
uv venv
source .venv/Scripts/activate
uv sync
```

## Kernel Sanity Check
```bash
# In a Jupyter notebook cell:
import sys
sys.executable
# Expect: ...utility-billing/.venv/Scripts/python.exe

# From terminal
jupyter kernelspec list
```

## VS Code workflow
```bash
# 1) Kernel picker (top-right in .ipynb) → Python (utility-billing)
# 2) Interpreter: Ctrl+Shift+P → Python: Select Interpreter → .venv
# 3) Terminal: Ctrl+\``. If not auto-activated, run source .venv/Scripts/activate`
```

## Git workflow
```bash
git status
git add -A
git commit -m "Work on notebooks"
git push
# Commit pyproject.toml and uv.lock
# Do not commit .venv/ (it's ignored by .gitignore)

```

## Quick one-liners
```bash
python -V
python -c "import sys; print(sys.executable)"
python -m jupyter lab
```

## Troubleshooting
```bash
# Notebook can’t find package: uv sync or uv add <pkg>
# Wrong Python path in notebook: re-select kernel → Python (utility-billing)
# jupyter: command not found: venv not active → source .venv/Scripts/activate
# VS Code PowerShell activation warning: optional fix:
```
```Powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```





