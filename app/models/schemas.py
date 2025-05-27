from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ReviewRequest(BaseModel):
    product_name: str
    max_reviews: Optional[int] = 100

class Review(BaseModel):
    title: str
    content: str
    rating: int
    date: Optional[str] = None
    verified_purchase: bool = False

class SentimentResult(BaseModel):
    sentiment: str  # positive, negative, neutral
    confidence: float
    compound_score: float

class ReviewAnalysis(BaseModel):
    review: Review
    sentiment: SentimentResult

class ProductReport(BaseModel):
    product_name: str
    total_reviews: int
    average_rating: float
    sentiment_distribution: dict
    main_praises: List[str]
    main_complaints: List[str]
    summary: str
    generated_at: datetime 