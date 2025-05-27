from textblob import TextBlob
from typing import List, Dict
from app.models.schemas import Review, SentimentResult, ReviewAnalysis
import re
from collections import Counter

class SentimentAnalyzer:
    def __init__(self):
        """Simple sentiment analyzer using only TextBlob to avoid multiprocessing issues"""
        print("Initializing simple sentiment analyzer (TextBlob only)")

    def analyze_review(self, review: Review) -> ReviewAnalysis:
        """Analyze sentiment of a single review using TextBlob"""
        # Combine title and content for analysis
        text = f"{review.title} {review.content}"
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Get TextBlob sentiment
        textblob_sentiment = self._get_textblob_sentiment(cleaned_text)
        
        final_sentiment = SentimentResult(
            sentiment=textblob_sentiment['sentiment'],
            confidence=textblob_sentiment['confidence'],
            compound_score=textblob_sentiment.get('compound_score', 0.0)
        )
        
        return ReviewAnalysis(
            review=review,
            sentiment=final_sentiment
        )

    def analyze_reviews_batch(self, reviews: List[Review]) -> List[ReviewAnalysis]:
        """Analyze sentiment for multiple reviews"""
        analyses = []
        for review in reviews:
            analysis = self.analyze_review(review)
            analyses.append(analysis)
        return analyses

    def extract_key_phrases(self, reviews: List[Review], sentiment_type: str) -> List[str]:
        """Extract key phrases from reviews of a specific sentiment"""
        filtered_reviews = []
        
        for review in reviews:
            analysis = self.analyze_review(review)
            if analysis.sentiment.sentiment == sentiment_type:
                filtered_reviews.append(review.content)
        
        # Simple keyword extraction
        key_phrases = self._extract_phrases_from_texts(filtered_reviews)
        return key_phrases[:10]

    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def _get_textblob_sentiment(self, text: str) -> Dict:
        """Get sentiment using TextBlob"""
        blob = TextBlob(text)
        polarity = blob.sentiment.polarity
        
        if polarity > 0.1:
            sentiment = 'positive'
        elif polarity < -0.1:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Convert polarity to confidence score
        confidence = min(abs(polarity) * 2, 1.0)  # Scale to 0-1 range
        
        return {
            'sentiment': sentiment,
            'confidence': confidence,
            'compound_score': polarity
        }

    def _extract_phrases_from_texts(self, texts: List[str]) -> List[str]:
        """Extract common phrases from texts"""
        stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'was', 'are', 'were', 'this', 'that', 'it', 'very', 'really', 'quite'])
        
        phrases = []
        for text in texts:
            words = text.lower().split()
            words = [word.strip('.,!?') for word in words if word.strip('.,!?') not in stop_words and len(word) > 2]
            
            # Extract 2-word phrases
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                phrases.append(phrase)
        
        # Count and return most common phrases
        phrase_counts = Counter(phrases)
        return [phrase for phrase, count in phrase_counts.most_common(20) if count > 1] 