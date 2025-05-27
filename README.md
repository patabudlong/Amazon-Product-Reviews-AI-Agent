# Amazon Product Reviews AI Agent - Analyzer

An AI-powered FastAPI application that scrapes Amazon product reviews and generates comprehensive sentiment analysis reports using advanced NLP techniques.

## 🚀 Features

- **Product Review Scraping**: Automatically finds and scrapes Amazon product reviews
- **Advanced Sentiment Analysis**: Uses transformer models (RoBERTa) with TextBlob fallback
- **Comprehensive Reports**: Generates detailed analysis including:
  - Sentiment distribution (positive/negative/neutral)
  - Average ratings and statistics
  - Key praises and complaints extraction
  - Executive summary with recommendations
- **RESTful API**: Clean FastAPI interface with automatic documentation
- **Robust Error Handling**: Graceful fallbacks and detailed error reporting
- **Cross-platform Support**: Handles multiprocessing issues on different operating systems

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **NLP**: Transformers (HuggingFace), TextBlob, NLTK
- **Web Scraping**: BeautifulSoup, aiohttp/requests
- **Data Processing**: Pydantic for data validation
- **Server**: Uvicorn ASGI server

## 📋 Prerequisites

- Python 3.8 or higher
- pip package manager
- Internet connection for model downloads and scraping

## 🔧 Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd amazon-review-analyzer
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables** (optional)
   ```bash
   # Create .env file for scraping API (if using external service)
   SCRAPING_API_KEY=your_api_key_here
   SCRAPING_API_URL=your_api_url_here
   ```

## 🚀 Quick Start

### Option 1: Simple Start (Recommended)

bash
python simple_start.py

### Option 2: Standard Start
bash
python run.py


### Option 3: Direct Start
bash
python start_server.py


The server will start on `http://localhost:8000`

## 📖 API Usage

### Interactive Documentation
Visit `http://localhost:8000/docs` for Swagger UI documentation

### Main Endpoints

#### 1. Analyze Product Reviews

http
POST /analyze-product
Content-Type: application/json
{
"product_name": "Kindle Paperwhite",
"max_reviews": 50
}


**Response:**
```
json
{
"product_name": "Kindle Paperwhite",
"total_reviews": 50,
"average_rating": 4.2,
"sentiment_distribution": {
"positive": {"count": 30, "percentage": 60.0},
"negative": {"count": 15, "percentage": 30.0},
"neutral": {"count": 5, "percentage": 10.0}
},
"main_praises": [
"Excellent Display Quality",
"Long Battery Life",
"Waterproof Design"
],
"main_complaints": [
"Slow Performance",
"Unresponsive Touch Screen",
"Limited Storage"
],
"summary": "Based on analysis of 50 reviews, the Kindle Paperwhite receives an average rating of 4.2/5 stars...",
"generated_at": "2024-01-15T10:30:00"
}
```

#### 2. Health Check
http
GET /health


#### 3. Service Status
http
GET /debug


## 🧪 Testing

### Test Imports
bash
python test_imports.py


### Test API Endpoints

bash

Test simple endpoint
curl http://localhost:8000/test-simple

Test health check
curl http://localhost:8000/health

Test product analysis
curl -X POST "http://localhost:8000/analyze-product" \
-H "Content-Type: application/json" \
-d '{"product_name": "Kindle Paperwhite", "max_reviews": 10}'

## 📁 Project Structure
```
amazon-review-ai-agent/
├── app/
│ ├── main.py # FastAPI application
│ ├── models/
│ │ └── schemas.py # Pydantic data models
│ └── services/
│ ├── scraper.py # Amazon review scraper
│ ├── sentiment_analyzer.py # Advanced sentiment analysis
│ ├── sentiment_analyzer_simple.py # Lightweight fallback
│ └── report_generator.py # Report generation logic
├── run.py # Standard server launcher
├── start_server.py # Alternative launcher
├── simple_start.py # Recommended launcher with testing
├── test_imports.py # Import validation script
├── requirements.txt # Python dependencies
└── README.md # This file
```

## 🔧 Configuration

### Environment Variables
- `SCRAPING_API_KEY`: API key for external scraping service (optional)
- `SCRAPING_API_URL`: URL for external scraping service (optional)
- `TOKENIZERS_PARALLELISM`: Set to "false" to avoid multiprocessing issues
- `OMP_NUM_THREADS`: Set to "1" for stability

### Model Configuration
The application automatically downloads required NLP models:
- `cardiffnlp/twitter-roberta-base-sentiment-latest` for sentiment analysis
- NLTK data for text processing

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Test all imports first
   python test_imports.py
   ```

2. **Multiprocessing Issues on Windows**
   - Use `simple_start.py` instead of `run.py`
   - Ensure `multiprocessing.freeze_support()` is called

3. **Model Download Issues**
   - Ensure stable internet connection
   - Models are downloaded automatically on first run

4. **Memory Issues**
   - Reduce `max_reviews` parameter
   - Use simple sentiment analyzer fallback

### Debug Information

bash
Check service status
curl http://localhost:8000/debug


## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the BSD 2-Clause "Simplified" License - see the LICENSE file for details.

## 🙏 Acknowledgments

- HuggingFace Transformers for state-of-the-art NLP models
- FastAPI for the excellent web framework
- TextBlob for sentiment analysis fallback
- BeautifulSoup for web scraping capabilities

## 📞 Support

For support, please open an issue in the GitHub repository or contact me: peregrino.tabudlong@gmail.com

---

**Note**: This application includes mock data for demonstration purposes. 
In production, implement proper Amazon scraping with respect to their robots.txt and terms of service.
