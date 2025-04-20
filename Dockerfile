# Base image
FROM python:3.11-slim

# Chrome/Chromium installation
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
    && pip install gunicorn

# Application code
COPY scraper /app/scraper
COPY start_server_prod.py /app/
WORKDIR /app

# Environment setup
ENV PYTHONUNBUFFERED=1
ENV CHROME_PATH=/usr/bin/google-chrome
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver
ENV GUNICORN_CMD_ARGS="--workers 1 --timeout 180"



# Run with Gunicorn
CMD gunicorn -k uvicorn.workers.UvicornWorker scraper.server:app --bind "0.0.0.0:$PORT"