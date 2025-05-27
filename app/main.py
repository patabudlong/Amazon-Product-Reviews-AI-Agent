from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from app.models.schemas import ReviewRequest, ProductReport
import os
from dotenv import load_dotenv
import sys
import traceback

# Load environment variables
load_dotenv()

# Set environment variables to prevent multiprocessing issues
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"

app = FastAPI(
    title="Amazon Product Review Analyzer",
    description="AI Agent for scraping Amazon reviews and generating sentiment analysis reports",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for services
scraper = None
report_generator = None
initialization_error = None

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup to avoid import-time issues"""
    global scraper, report_generator, initialization_error
    
    try:
        print("Starting service initialization...")
        
        # Import and initialize scraper
        print("Importing scraper...")
        from app.services.scraper import AmazonReviewsScraper
        scraper = AmazonReviewsScraper()
        print("✓ Scraper initialized successfully")
        
        # Import and initialize report generator
        print("Importing report generator...")
        from app.services.report_generator import ReportGenerator
        report_generator = ReportGenerator()
        print("✓ Report generator initialized successfully")
        
        print("🎉 All services initialized successfully!")
        
    except Exception as e:
        error_msg = f"Error initializing services: {str(e)}"
        print(f"❌ {error_msg}")
        traceback.print_exc()
        initialization_error = error_msg
        
        # Don't fail startup completely, but store the error
        print("⚠️ Server will start but services are not available")

@app.get("/")
async def root():
    return {
        "message": "Amazon Product Review Analyzer API",
        "status": "running",
        "services_ready": scraper is not None and report_generator is not None,
        "initialization_error": initialization_error
    }

@app.get("/debug")
async def debug_info():
    """Debug endpoint to check service status"""
    return {
        "scraper_initialized": scraper is not None,
        "report_generator_initialized": report_generator is not None,
        "initialization_error": initialization_error,
        "python_version": sys.version,
        "working_directory": os.getcwd(),
        "python_path": sys.path[:3]  # First 3 entries
    }

@app.post("/analyze-product", response_model=ProductReport)
async def analyze_product(request: ReviewRequest):
    """
    Analyze Amazon product reviews and generate a comprehensive report
    """
    try:
        if initialization_error:
            raise HTTPException(
                status_code=503, 
                detail=f"Services failed to initialize: {initialization_error}"
            )
            
        if not scraper or not report_generator:
            raise HTTPException(
                status_code=503, 
                detail="Services not initialized. Check /debug endpoint for details."
            )
            
        print(f"Starting analysis for: {request.product_name}")
        
        # Scrape reviews
        reviews = await scraper.scrape_reviews(
            product_name=request.product_name,
            max_reviews=request.max_reviews
        )
        
        if not reviews:
            raise HTTPException(
                status_code=404, 
                detail="No reviews found for the specified product"
            )
        
        print(f"Found {len(reviews)} reviews, generating report...")
        
        # Generate report
        report = report_generator.generate_report(
            product_name=request.product_name,
            reviews=reviews
        )
        
        print("Report generated successfully!")
        return report
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_product: {e}")
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "message": "Service is running",
        "services_initialized": scraper is not None and report_generator is not None,
        "initialization_error": initialization_error
    }

@app.get("/test-simple")
async def test_simple():
    """Simple test endpoint that doesn't use heavy services"""
    return {"message": "Simple test successful", "python_version": sys.version} 