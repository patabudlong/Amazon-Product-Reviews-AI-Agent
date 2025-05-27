import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_and_start():
    print("Testing imports before starting server...")
    
    try:
        # Test imports
        from app.models.schemas import ReviewRequest, ProductReport
        print("✓ Schemas OK")
        
        from app.services.scraper import AmazonReviewsScraper
        print("✓ Scraper OK")
        
        from app.services.sentiment_analyzer_simple import SentimentAnalyzer
        print("✓ Sentiment Analyzer OK")
        
        from app.services.report_generator import ReportGenerator
        print("✓ Report Generator OK")
        
        print("All imports successful! Starting server...")
        
        # Start server
        import uvicorn
        from app.main import app
        uvicorn.run(app, host="0.0.0.0", port=8000, reload=False)
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_and_start() 