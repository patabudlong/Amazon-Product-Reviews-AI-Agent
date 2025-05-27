import requests
import asyncio
from bs4 import BeautifulSoup
from typing import List
import os
from urllib.parse import quote
import time
import random
from app.models.schemas import Review

# Try to import aiohttp, fallback to requests if not available
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False
    print("Warning: aiohttp not available, using requests instead")

class AmazonReviewsScraper:
    def __init__(self):
        self.scraping_api_key = os.getenv("SCRAPING_API_KEY")
        self.scraping_api_url = os.getenv("SCRAPING_API_URL")
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    async def search_product(self, product_name: str) -> str:
        """Search for product and return the first product URL"""
        search_url = f"https://www.amazon.com/s?k={quote(product_name)}"
        
        if self.scraping_api_key:
            # Using scraping API service
            params = {
                'api_key': self.scraping_api_key,
                'url': search_url,
                'render_js': 'false'
            }
            
            if AIOHTTP_AVAILABLE:
                async with aiohttp.ClientSession() as session:
                    async with session.get(self.scraping_api_url, params=params) as response:
                        html = await response.text()
            else:
                # Fallback to requests (synchronous)
                response = requests.get(self.scraping_api_url, params=params)
                html = response.text
        else:
            # Direct scraping
            if AIOHTTP_AVAILABLE:
                async with aiohttp.ClientSession() as session:
                    async with session.get(search_url, headers=self.headers) as response:
                        html = await response.text()
            else:
                # Fallback to requests (synchronous)
                response = requests.get(search_url, headers=self.headers)
                html = response.text
        
        soup = BeautifulSoup(html, 'html.parser')
        
        # Find first product link
        product_links = soup.find_all('a', {'class': 's-link-style'})
        if product_links:
            product_path = product_links[0].get('href')
            return f"https://www.amazon.com{product_path}"
        
        raise Exception("Product not found")

    async def scrape_reviews(self, product_name: str, max_reviews: int = 100) -> List[Review]:
        """Scrape reviews for a given product"""
        try:
            # For demo purposes, let's create some mock reviews to test the system
            # In production, you would implement actual scraping
            mock_reviews = self._create_mock_reviews(product_name, max_reviews)
            return mock_reviews
            
        except Exception as e:
            raise Exception(f"Error scraping reviews: {str(e)}")

    def _create_mock_reviews(self, product_name: str, max_reviews: int) -> List[Review]:
        """Create mock reviews for testing purposes"""
        mock_reviews_data = [
            {
                "title": "Great product!",
                "content": "I love this Kindle Paperwhite. The screen is amazing and battery life is excellent. Perfect for reading in any lighting condition.",
                "rating": 5,
                "date": "2024-01-15",
                "verified_purchase": True
            },
            {
                "title": "Good but has issues",
                "content": "The device works well overall but the touch screen can be unresponsive sometimes. Also wish it was faster.",
                "rating": 3,
                "date": "2024-01-10",
                "verified_purchase": True
            },
            {
                "title": "Excellent reading experience",
                "content": "Best e-reader I've ever owned. The display is crisp, easy on the eyes, and the waterproof feature is fantastic.",
                "rating": 5,
                "date": "2024-01-08",
                "verified_purchase": True
            },
            {
                "title": "Disappointing",
                "content": "Expected better performance. The device is slow and the interface is confusing. Battery doesn't last as long as advertised.",
                "rating": 2,
                "date": "2024-01-05",
                "verified_purchase": False
            },
            {
                "title": "Perfect for travel",
                "content": "Lightweight and portable. Great for reading during flights. The backlight is perfect for reading in dark environments.",
                "rating": 4,
                "date": "2024-01-03",
                "verified_purchase": True
            },
            {
                "title": "Value for money",
                "content": "Good device for the price. Storage is adequate and sync with Amazon library works seamlessly.",
                "rating": 4,
                "date": "2024-01-01",
                "verified_purchase": True
            }
        ]
        
        reviews = []
        for i, review_data in enumerate(mock_reviews_data):
            if i >= max_reviews:
                break
            review = Review(**review_data)
            reviews.append(review)
        
        return reviews

    def _extract_asin(self, product_url: str) -> str:
        """Extract ASIN from product URL"""
        import re
        asin_match = re.search(r'/(?:dp|gp/product)/([A-Z0-9]{10})', product_url)
        if asin_match:
            return asin_match.group(1)
        raise Exception("Could not extract ASIN from product URL")

    def _parse_reviews_page(self, html: str) -> List[Review]:
        """Parse reviews from a single page"""
        soup = BeautifulSoup(html, 'html.parser')
        reviews = []
        
        review_elements = soup.find_all('div', {'data-hook': 'review'})
        
        for element in review_elements:
            try:
                # Extract review title
                title_elem = element.find('a', {'data-hook': 'review-title'})
                title = title_elem.get_text(strip=True) if title_elem else ""
                
                # Extract review content
                content_elem = element.find('span', {'data-hook': 'review-body'})
                content = content_elem.get_text(strip=True) if content_elem else ""
                
                # Extract rating
                rating_elem = element.find('i', {'data-hook': 'review-star-rating'})
                rating = 0
                if rating_elem:
                    rating_text = rating_elem.get_text()
                    rating = int(float(rating_text.split()[0]))
                
                # Extract date
                date_elem = element.find('span', {'data-hook': 'review-date'})
                date = date_elem.get_text(strip=True) if date_elem else ""
                
                # Check if verified purchase
                verified_elem = element.find('span', {'data-hook': 'avp-badge'})
                verified_purchase = verified_elem is not None
                
                if title and content:
                    review = Review(
                        title=title,
                        content=content,
                        rating=rating,
                        date=date,
                        verified_purchase=verified_purchase
                    )
                    reviews.append(review)
                    
            except Exception as e:
                continue  # Skip problematic reviews
        
        return reviews 