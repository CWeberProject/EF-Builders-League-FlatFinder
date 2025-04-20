import uvicorn
from scraper.utils.logging_config import logger

def start_fastapi():
    """Start the FastAPI server."""
    try:
        uvicorn.run(
            "scraper.server:app",
            host="0.0.0.0",
            port=8000,
            reload=False
        )
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        exit(1)

if __name__ == "__main__":
    print("\n=== Craigslist Scraper API ===")
    print("Server starting on port 8000")
    print("API Documentation: http://localhost:8000/docs\n")
    start_fastapi()