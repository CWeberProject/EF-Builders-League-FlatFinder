import os
import sys
import time
from pyngrok import ngrok
import uvicorn
import threading
import signal
from scraper.utils.logging_config import logger

def start_ngrok():
    """Start ngrok tunnel and return the public URL."""
    try:
        # Start ngrok tunnel
        tunnel = ngrok.connect(8000)
        logger.info(f"Ngrok tunnel established at: {tunnel.public_url}")
        return tunnel
    except Exception as e:
        logger.error(f"Failed to establish ngrok tunnel: {e}")
        sys.exit(1)

def start_fastapi():
    """Start the FastAPI server."""
    try:
        import scraper.server
        uvicorn.run(
            "scraper.server:app",
            host="0.0.0.0",
            port=8000,
            reload=False
        )
    except Exception as e:
        logger.error(f"Failed to start FastAPI server: {e}")
        sys.exit(1)

def cleanup(tunnel):
    """Cleanup resources before exit."""
    logger.info("Shutting down server...")
    try:
        ngrok.disconnect(tunnel.public_url)
        ngrok.kill()
    except:
        pass

def main():
    # Start ngrok tunnel
    tunnel = start_ngrok()
    
    # Register cleanup handler
    def signal_handler(signum, frame):
        cleanup(tunnel)
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        # Print access information
        print("\n=== Craigslist Scraper API ===")
        print(f"Public URL: {tunnel.public_url}")
        print("API Documentation: {}/docs".format(tunnel.public_url))
        print("\nPress Ctrl+C to stop the server\n")

        # Start FastAPI server
        start_fastapi()
    except KeyboardInterrupt:
        cleanup(tunnel)
        sys.exit(0)
    except Exception as e:
        logger.error(f"Server error: {e}")
        cleanup(tunnel)
        sys.exit(1)

if __name__ == "__main__":
    main()