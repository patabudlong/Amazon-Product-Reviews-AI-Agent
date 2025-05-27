from typing import List
from datetime import datetime
import statistics
from collections import Counter
from app.models.schemas import Review, ReviewAnalysis, ProductReport

class ReportGenerator:
    def __init__(self):
        # Import the simple version to avoid multiprocessing issues
        try:
            from app.services.sentiment_analyzer_simple import SentimentAnalyzer
            self.sentiment_analyzer = SentimentAnalyzer()
            print("Using simple sentiment analyzer")
        except Exception as e:
            print(f"Error initializing sentiment analyzer: {e}")
            raise

    def generate_report(self, product_name: str, reviews: List[Review]) -> ProductReport:
        """Generate comprehensive product report"""
        
        # Analyze all reviews
        analyses = self.sentiment_analyzer.analyze_reviews_batch(reviews)
        
        # Calculate basic statistics
        total_reviews = len(reviews)
        average_rating = statistics.mean([review.rating for review in reviews]) if reviews else 0
        
        # Calculate sentiment distribution
        sentiment_distribution = self._calculate_sentiment_distribution(analyses)
        
        # Extract main praises and complaints
        main_praises = self._extract_praises(analyses)
        main_complaints = self._extract_complaints(analyses)
        
        # Generate summary
        summary = self._generate_summary(
            product_name, total_reviews, average_rating, 
            sentiment_distribution, main_praises, main_complaints
        )
        
        return ProductReport(
            product_name=product_name,
            total_reviews=total_reviews,
            average_rating=round(average_rating, 2),
            sentiment_distribution=sentiment_distribution,
            main_praises=main_praises,
            main_complaints=main_complaints,
            summary=summary,
            generated_at=datetime.now()
        )

    def _calculate_sentiment_distribution(self, analyses: List[ReviewAnalysis]) -> dict:
        """Calculate distribution of sentiments"""
        sentiments = [analysis.sentiment.sentiment for analysis in analyses]
        sentiment_counts = Counter(sentiments)
        total = len(sentiments)
        
        distribution = {}
        for sentiment in ['positive', 'negative', 'neutral']:
            count = sentiment_counts.get(sentiment, 0)
            distribution[sentiment] = {
                'count': count,
                'percentage': round((count / total) * 100, 1) if total > 0 else 0
            }
        
        return distribution

    def _extract_praises(self, analyses: List[ReviewAnalysis]) -> List[str]:
        """Extract main praises from positive reviews"""
        positive_reviews = [
            analysis.review for analysis in analyses 
            if analysis.sentiment.sentiment == 'positive'
        ]
        
        if not positive_reviews:
            return []
        
        # Extract key phrases from positive reviews
        praises = self.sentiment_analyzer.extract_key_phrases(positive_reviews, 'positive')
        
        # Filter and clean praises
        cleaned_praises = []
        for praise in praises:
            if len(praise.split()) >= 2 and len(praise) > 5:
                cleaned_praises.append(praise.title())
        
        return cleaned_praises[:8]  # Return top 8 praises

    def _extract_complaints(self, analyses: List[ReviewAnalysis]) -> List[str]:
        """Extract main complaints from negative reviews"""
        negative_reviews = [
            analysis.review for analysis in analyses 
            if analysis.sentiment.sentiment == 'negative'
        ]
        
        if not negative_reviews:
            return []
        
        # Extract key phrases from negative reviews
        complaints = self.sentiment_analyzer.extract_key_phrases(negative_reviews, 'negative')
        
        # Filter and clean complaints
        cleaned_complaints = []
        for complaint in complaints:
            if len(complaint.split()) >= 2 and len(complaint) > 5:
                cleaned_complaints.append(complaint.title())
        
        return cleaned_complaints[:8]  # Return top 8 complaints

    def _generate_summary(self, product_name: str, total_reviews: int, 
                         average_rating: float, sentiment_distribution: dict,
                         main_praises: List[str], main_complaints: List[str]) -> str:
        """Generate a comprehensive summary"""
        
        # Determine overall sentiment
        positive_pct = sentiment_distribution['positive']['percentage']
        negative_pct = sentiment_distribution['negative']['percentage']
        
        if positive_pct > 60:
            overall_sentiment = "overwhelmingly positive"
        elif positive_pct > 40:
            overall_sentiment = "generally positive"
        elif negative_pct > 60:
            overall_sentiment = "overwhelmingly negative"
        elif negative_pct > 40:
            overall_sentiment = "generally negative"
        else:
            overall_sentiment = "mixed"
        
        summary_parts = []
        
        # Opening statement
        summary_parts.append(
            f"Based on analysis of {total_reviews} reviews, the {product_name} "
            f"receives an average rating of {average_rating:.1f}/5 stars with "
            f"{overall_sentiment} customer feedback."
        )
        
        # Sentiment breakdown
        summary_parts.append(
            f"The sentiment distribution shows {positive_pct}% positive, "
            f"{negative_pct}% negative, and {sentiment_distribution['neutral']['percentage']}% neutral reviews."
        )
        
        # Main praises
        if main_praises:
            praises_text = ", ".join(main_praises[:3])
            summary_parts.append(f"Customers particularly praise: {praises_text}.")
        
        # Main complaints
        if main_complaints:
            complaints_text = ", ".join(main_complaints[:3])
            summary_parts.append(f"Common concerns include: {complaints_text}.")
        
        # Recommendation
        if average_rating >= 4.0 and positive_pct > 60:
            summary_parts.append("Overall, this product is highly recommended by customers.")
        elif average_rating >= 3.5 and positive_pct > 50:
            summary_parts.append("This product generally meets customer expectations.")
        elif average_rating >= 3.0:
            summary_parts.append("This product has mixed reviews and may require careful consideration.")
        else:
            summary_parts.append("This product has significant customer satisfaction issues.")
        
        return " ".join(summary_parts) 