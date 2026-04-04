# Railway Deployment Fix - Uvicorn Not Found

## Problem
The Railway deployment was failing with the error:
```
The executable `uvicorn` could not be found
```

## Root Cause
Two issues were identified:

### 1. Incorrect Dependency Location in pyproject.toml
The dependencies were incorrectly placed under `[tool.hatch.build.targets.wheel]` instead of `[project]`. This meant they were only used during wheel building, not during installation.

**Before:**
```toml
[project]
name = "donut-backend"
version = "0.1.0"
description = "Donut AI - Executive Function Co-Pilot Backend"
requires-python = ">=3.11"

[tool.hatch.build.targets.wheel]
packages = ["app"]
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    ...
]
```

### 2. Installing Only Dev Dependencies in Dockerfile
The Dockerfile was running `pip install -e .[dev]` which only installs the optional dev dependencies (pytest, mypy, ruff, etc.) and not the main application dependencies.

**Before:**
```dockerfile
RUN pip install --upgrade pip && \
    pip install -e .[dev]
```

## Solution

### 1. Fixed pyproject.toml
Moved dependencies to the correct location under `[project]`:

```toml
[project]
name = "donut-backend"
version = "0.1.0"
description = "Donut AI - Executive Function Co-Pilot Backend"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "groq>=0.4.0",
    ...
]

[tool.hatch.build.targets.wheel]
packages = ["app"]
```

### 2. Fixed Dockerfile
Changed to install the main package with its dependencies:

```dockerfile
RUN pip install --upgrade pip && \
    pip install -e .
```

## Files Modified
- `backend/pyproject.toml` - Moved dependencies to correct section
- `Dockerfile` - Changed pip install command

## Testing
After these changes, the Docker build should:
1. Install all runtime dependencies (fastapi, uvicorn, groq, etc.)
2. Successfully start the container with `uvicorn`
3. The application should be accessible on port 8000

## For Local Development
If you want to install dev dependencies locally, use:
```bash
pip install -e .[dev]
```

This will install both the main dependencies and the dev tools (pytest, mypy, ruff, pre-commit).