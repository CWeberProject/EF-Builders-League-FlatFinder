# Ngrok Removal Plan for Production

## Current Analysis
- Ngrok is primarily used in `start_server.py`
- Used for development to expose local server
- No direct ngrok usage in main server code
- Listed as dependency in requirements.txt

## Implementation Plan

### 1. Create Development/Production Split
Create two server start files:
- `start_server_dev.py` (existing `start_server.py` renamed)
  - Keeps ngrok functionality for local development
  - Includes tunnel setup and cleanup
- `start_server_prod.py` (new file)
  - Simplified version without ngrok
  - Only runs uvicorn server
  - Used by Render deployment

### 2. Update Requirements
Create two requirement files:
- `requirements.txt` (production)
  - Remove pyngrok
  - Keep core dependencies
- `requirements-dev.txt`
  - Include pyngrok
  - Import base requirements

### 3. Update Render Configuration
Modify `render.yaml` to:
- Use `start_server_prod.py` as start command
- Use production requirements.txt

### 4. Code Changes Required
1. Rename current `start_server.py` to `start_server_dev.py`
2. Create new `start_server_prod.py` with minimal configuration
3. Split requirements into prod/dev files
4. Update documentation to reflect the changes

This approach maintains development functionality while optimizing the production deployment.