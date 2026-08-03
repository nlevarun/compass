"""
Sentiment analysis using ensemble approach (VADER + TextBlob).

VADER: Good for social media and short text
TextBlob: Good for longer, formal text
Ensemble: Average of both for robustness
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
    from textblob import TextBlob
    DEPS_AVAILABLE = True
except ImportError:
    DEPS_AVAILABLE = False
    print("⚠️  Sentiment analysis dependencies not installed. Using simplified analysis.")


class SentimentAnalyzer:
    """Ensemble sentiment analyzer combining VADER and TextBlob."""

    def __init__(self):
        if DEPS_AVAILABLE:
            self.vader = SentimentIntensityAnalyzer()
        else:
            self.vader = None

    def analyze(self, text: str) -> float:
        """
        Analyze sentiment of text.

        Returns:
            Sentiment score from -1.0 (very negative) to 1.0 (very positive)
        """
        if not DEPS_AVAILABLE:
            return self._simple_sentiment(text)

        # VADER sentiment
        vader_scores = self.vader.polarity_scores(text)
        vader_compound = vader_scores["compound"]  # -1 to 1

        # TextBlob sentiment
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity  # -1 to 1

        # Ensemble: average both
        ensemble_score = (vader_compound + textblob_polarity) / 2

        return round(ensemble_score, 3)

    def _simple_sentiment(self, text: str) -> float:
        """Simple fallback sentiment based on keyword matching."""
        positive_words = {
            "good", "great", "excellent", "amazing", "love", "fantastic", "awesome",
            "helpful", "useful", "perfect", "wonderful", "better", "best", "nice",
            "thank", "thanks", "appreciate", "impressed", "happy", "pleased"
        }

        negative_words = {
            "bad", "terrible", "awful", "horrible", "hate", "worst", "poor",
            "slow", "crash", "bug", "broken", "frustrating", "annoying", "disappointed",
            "issue", "problem", "error", "fail", "wrong", "missing", "can't", "cannot",
            "difficult", "hard", "confusing", "unclear", "useless"
        }

        words = text.lower().split()
        positive_count = sum(1 for w in words if any(pw in w for pw in positive_words))
        negative_count = sum(1 for w in words if any(nw in w for nw in negative_words))

        # Calculate score
        total = positive_count + negative_count
        if total == 0:
            return 0.0

        score = (positive_count - negative_count) / total
        return round(score, 3)

    def batch_analyze(self, texts: list) -> list:
        """Analyze sentiment for multiple texts."""
        return [self.analyze(text) for text in texts]


def categorize_sentiment(score: float) -> str:
    """
    Categorize sentiment score into labels.

    Args:
        score: Sentiment score (-1 to 1)

    Returns:
        Category: "Very Negative", "Negative", "Neutral", "Positive", "Very Positive"
    """
    if score <= -0.6:
        return "Very Negative"
    elif score <= -0.2:
        return "Negative"
    elif score <= 0.2:
        return "Neutral"
    elif score <= 0.6:
        return "Positive"
    else:
        return "Very Positive"


if __name__ == "__main__":
    # Test sentiment analysis
    print("Testing sentiment analysis...\n")

    analyzer = SentimentAnalyzer()

    test_texts = [
        "This is amazing! I love the new features.",
        "The app crashes constantly. Very frustrating.",
        "Could you add dark mode support?",
        "Excellent product, but the mobile app is slow.",
        "Terrible experience. Nothing works as expected.",
    ]

    print("Analyzing sentiment...")
    for text in test_texts:
        score = analyzer.analyze(text)
        category = categorize_sentiment(score)
        print(f"  [{category:>15}] {score:+.3f} | \"{text}\"")
