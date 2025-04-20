from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, HttpUrl
from scraper.core.scraper import CraigslistScraper
from scraper.utils.logging_config import logger

# Request/Response Models
class ScrapeRequest(BaseModel):
    urls: List[HttpUrl]
    max_retries: Optional[int] = 3

class ScrapeResult(BaseModel):
    url: HttpUrl
    data: dict
    success: bool

class ScrapeResponse(BaseModel):
    results: List[ScrapeResult]
    errors: List[str]

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime

# Initialize FastAPI app
app = FastAPI(
    title="Craigslist Scraper API",
    description="API for scraping Craigslist housing listings",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Modify in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize scraper instance
scraper = CraigslistScraper()

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Check if the API is healthy."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow()
    }

@app.post("/scrape", response_model=ScrapeResponse)
async def scrape_urls(request: ScrapeRequest):
    """Scrape provided Craigslist URLs."""
    results = []
    errors = []

    try:
        # Update max retries if specified
        if request.max_retries != scraper.max_retries:
            scraper.max_retries = request.max_retries

        # Process each URL
        for url in request.urls:
            logger.info(f"Processing URL: {url}")
            try:
                data = scraper.scrape(str(url))
                results.append(
                    ScrapeResult(
                        url=url,
                        data=data if data else {},
                        success=bool(data)
                    )
                )
                if not data:
                    errors.append(f"No data obtained for URL: {url}")
            except Exception as e:
                logger.error(f"Error scraping URL {url}: {str(e)}")
                errors.append(f"Failed to scrape {url}: {str(e)}")
                results.append(
                    ScrapeResult(
                        url=url,
                        data={},
                        success=False
                    )
                )

        return {
            "results": results,
            "errors": errors
        }

    except Exception as e:
        logger.error(f"Scraping process failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Scraping process failed: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)