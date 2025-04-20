# Docker Implementation Plan

## Overview
Convert the application to use Docker for containerization, focusing on proper browser installation and configuration for production deployment on Render.

## Changes Required

### 1. Dockerfile Structure
```dockerfile
# Base image
FROM python:3.11-slim

# Chrome/Chromium installation
# Using Chrome for Testing for lighter weight
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    xvfb \
    ca-certificates \
    fonts-liberation \
    && wget -qO- https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/chrome.gpg] https://dl.google.com/linux/chrome/deb/ stable main" > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable chromium-driver \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && pip install gunicorn  # Add gunicorn explicitly

# Application code
COPY scraper /app/scraper
COPY start_server_prod.py /app/
WORKDIR /app

# Environment setup
ENV PYTHONUNBUFFERED=1
ENV PORT=8000
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

# Run with Gunicorn
CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "scraper.server:app", "--bind", "0.0.0.0:${PORT}"]
```

### 2. Requirements Updates
- Add gunicorn to requirements.txt
- Remove render.yaml as we'll use Docker instead

### 3. Browser Configuration Updates
Update browser_config.py to:
- Use environment variables for Chrome/ChromeDriver paths
- Configure Chrome for container environment

### 4. Docker Ignore File
Create .dockerignore to exclude unnecessary files:
```
.git
.gitignore
.env
*.pyc
__pycache__
.pytest_cache
.coverage
htmlcov
venv
.venv
.ngrok
*.log
```

### 5. Render Configuration
Deploy as a Web Service using Docker:
- Choose "Deploy from Dockerfile"
- Set environment variables if needed
- Configure health check endpoint

## Implementation Steps

1. Create Dockerfile as specified above
2. Create .dockerignore file
3. Update browser_config.py for containerized environment
4. Update requirements.txt
5. Remove render.yaml
6. Test Docker build and run locally
7. Configure Render deployment

## Testing Plan

1. Local Docker Testing:
```bash
docker build -t scraper .
docker run -p 8000:8000 scraper
```

2. Verify:
- Server starts correctly
- Browser initializes properly
- Scraping works as expected
- Virtual display functions

## Deployment Instructions

1. Push code to repository
2. On Render:
   - Create new Web Service
   - Select "Deploy from Dockerfile"
   - Configure environment variables if needed
   - Deploy