# Setup Instructions - Fixing pytest Command Not Found

## Problem
You're getting `zsh: command not found: pytest` because dependencies aren't installed yet.

## Solution

### Step 1: Create Virtual Environment (if not exists)
```bash
cd /Users/defacto092/projects/rdmotorsAPi
python3 -m venv venv
```

### Step 2: Activate Virtual Environment
```bash
source venv/bin/activate
```

You should see `(venv)` in your terminal prompt.

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r rdmotorsAPI/requirements.txt
```

This will install:
- Flask and all dependencies
- pytest and testing tools
- Security packages (Flask-Limiter, bleach)
- API documentation (flask-restx)
- Production server (gunicorn)

### Step 4: Verify Installation
```bash
pytest --version
```

You should see: `pytest 8.3.4`

### Step 5: Run Tests
```bash
pytest -v
```

## Quick One-Liner Setup
```bash
cd /Users/defacto092/projects/rdmotorsAPi && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install --upgrade pip && \
pip install -r rdmotorsAPI/requirements.txt
```

## Troubleshooting

### If venv already exists:
```bash
source venv/bin/activate
pip install -r rdmotorsAPI/requirements.txt
```

### If you get permission errors:
```bash
python3 -m venv venv --without-pip
source venv/bin/activate
curl https://bootstrap.pypa.io/get-pip.py | python
pip install -r rdmotorsAPI/requirements.txt
```

### Alternative: Install globally (not recommended)
```bash
pip3 install -r rdmotorsAPI/requirements.txt
```

## After Setup

Always activate the virtual environment before working:
```bash
source venv/bin/activate
```

Then you can:
- Run tests: `pytest`
- Run server: `python rdmotorsAPI/server.py`
- Install packages: `pip install <package>`
