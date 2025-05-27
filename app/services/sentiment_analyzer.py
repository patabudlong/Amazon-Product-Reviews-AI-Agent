from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
from textblob import TextBlob
import torch
from typing import List, Dict
from app.models.schemas import Review, SentimentResult, ReviewAnalysis
import re
import os

class SentimentAnalyzer:
    def __init__(self):
        # Set environment variable to avoid tokenizer parallelism warning
        os.environ["TOKENIZERS_PARALLELISM"] = "false"
        
        # Initialize BERT-based sentiment analyzer with explicit device setting
        model_name = "cardiffnlp/twitter-roberta-base-sentiment-latest"
        
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            
            # Force CPU usage to avoid multiprocessing issues on Windows
            device = -1  # Always use CPU for now
            
            self.sentiment_pipeline = pipeline(
                "sentiment-analysis",
                model=self.model,
                tokenizer=self.tokenizer,
                device=device,
                return_all_scores=False
            )
        except Exception as e:
            print(f"Warning: Could not load transformer model: {e}")
            print("Falling back to TextBlob only")
            self.sentiment_pipeline = None

    def analyze_review(self, review: Review) -> ReviewAnalysis:
        """Analyze sentiment of a single review"""
        # Combine title and content for analysis
        text = f"{review.title} {review.content}"
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        # Get sentiment using available methods
        if self.sentiment_pipeline:
            try:
                sentiment_result = self._get_transformer_sentiment(cleaned_text)
            except Exception as e:
                print(f"Transformer sentiment failed: {e}, falling back to TextBlob")
                sentiment_result = None
        else:
            sentiment_result = None
        
        # Get TextBlob sentiment
        textblob_sentiment = self._get_textblob_sentiment(cleaned_text)
        
        # Combine results or use TextBlob as fallback
        if sentiment_result:
            final_sentiment = self._combine_sentiments(sentiment_result, textblob_sentiment)
        else:
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
        
        # Simple keyword extraction (you can enhance this with more sophisticated NLP)
        key_phrases = self._extract_phrases_from_texts(filtered_reviews)
        return key_phrases[:10]  # Return top 10 phrases

    def _clean_text(self, text: str) -> str:
        """Clean and preprocess text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s.,!?-]', '', text)
        return text.strip()

    def _get_transformer_sentiment(self, text: str) -> Dict:
        """Get sentiment using transformer model"""
        # Truncate text if too long
        max_length = 512
        if len(text) > max_length:
            text = text[:max_length]
        
        # Use the pipeline with error handling
        try:
            result = self.sentiment_pipeline(text)[0]
        except Exception as e:
            raise Exception(f"Transformer sentiment analysis failed: {e}")
        
        # Map labels to our format
        label_mapping = {
            'LABEL_0': 'negative',
            'LABEL_1': 'neutral', 
            'LABEL_2': 'positive',
            'NEGATIVE': 'negative',
            'NEUTRAL': 'neutral',
            'POSITIVE': 'positive'
        }
        
        sentiment = label_mapping.get(result['label'], result['label'].lower())
        
        return {
            'sentiment': sentiment,
            'confidence': result['score']
        }

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
        
        return {
            'sentiment': sentiment,
            'confidence': abs(polarity),
            'compound_score': polarity
        }

    def _combine_sentiments(self, transformer_result: Dict, textblob_result: Dict) -> SentimentResult:
        """Combine results from different sentiment analyzers"""
        # Use transformer result as primary, TextBlob as secondary
        sentiment = transformer_result['sentiment']
        confidence = transformer_result['confidence']
        compound_score = textblob_result.get('compound_score', 0.0)
        
        # Adjust confidence based on agreement
        if transformer_result['sentiment'] == textblob_result['sentiment']:
            confidence = min(confidence * 1.1, 1.0)  # Boost confidence if they agree
        
        return SentimentResult(
            sentiment=sentiment,
            confidence=confidence,
            compound_score=compound_score
        )

    def _extract_phrases_from_texts(self, texts: List[str]) -> List[str]:
        """Extract common phrases from texts"""
        from collections import Counter
        import nltk
        
        try:
            nltk.download('punkt', quiet=True)
            nltk.download('stopwords', quiet=True)
            from nltk.corpus import stopwords
            from nltk.tokenize import word_tokenize
            
            stop_words = set(stopwords.words('english'))
        except:
            stop_words = set(['the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'])
        
        # Extract phrases (2-3 word combinations)
        phrases = []
        for text in texts:
            words = text.lower().split()
            words = [word for word in words if word not in stop_words and len(word) > 2]
            
            # Extract 2-word phrases
            for i in range(len(words) - 1):
                phrase = f"{words[i]} {words[i+1]}"
                phrases.append(phrase)
            
            # Extract 3-word phrases
            for i in range(len(words) - 2):
                phrase = f"{words[i]} {words[i+1]} {words[i+2]}"
                phrases.append(phrase)
        
        # Count and return most common phrases
        phrase_counts = Counter(phrases)
        return [phrase for phrase, count in phrase_counts.most_common(20) if count > 1] 