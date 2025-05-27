import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    try:
        print("Testing imports...")
        
        print("1. Testing basic imports...")
        from app.models.schemas import ReviewRequest, ProductReport
        print("✓ Schemas imported successfully")
        
        print("2. Testing scraper import...")
        from app.services.scraper import AmazonReviewsScraper
        scraper = AmazonReviewsScraper()
        print("✓ Scraper imported and initialized successfully")
        
        print("3. Testing sentiment analyzer import...")
        from app.services.sentiment_analyzer_simple import SentimentAnalyzer
        analyzer = SentimentAnalyzer()
        print("✓ Sentiment analyzer imported and initialized successfully")
        
        print("4. Testing report generator import...")
        from app.services.report_generator import ReportGenerator
        generator = ReportGenerator()
        print("✓ Report generator imported and initialized successfully")
        
        print("🎉 All imports successful!")
        return True
        
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_imports() 