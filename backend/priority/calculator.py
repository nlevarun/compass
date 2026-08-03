"""
Revenue-weighted priority scoring for roadmap items.

Priority Score = (Frequency × Revenue Weight × Sentiment Boost) / Effort

Components:
- Frequency: Number of requests (normalized)
- Revenue Weight: Total customer revenue requesting feature
- Sentiment Boost: Multiplier based on average sentiment (1.0 to 1.5)
- Effort: Estimated effort (inverse relationship)
"""

import sys
import os
from typing import List, Dict, Tuple

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PriorityCalculator:
    """
    Calculate priority scores for roadmap items based on feedback clusters.

    Formula:
        Priority = (frequency_score × revenue_weight × sentiment_boost) / effort_factor

    Where:
        - frequency_score: Normalized request count (0-1)
        - revenue_weight: Log-scaled revenue impact (0-1)
        - sentiment_boost: 1.0 to 1.5 based on sentiment
        - effort_factor: 1.0 (small), 2.0 (medium), 3.0 (large)
    """

    def __init__(self, max_revenue: float = 10_000_000):
        """
        Initialize calculator.

        Args:
            max_revenue: Maximum expected customer revenue (for normalization)
        """
        self.max_revenue = max_revenue

    def calculate_frequency_score(self, count: int, max_count: int) -> float:
        """
        Normalize request count to 0-1 scale.

        Uses log scaling to prevent very popular features from dominating.
        """
        if max_count == 0:
            return 0.0

        import math
        # Log scaling to reduce impact of very high counts
        log_count = math.log(count + 1)
        log_max = math.log(max_count + 1)

        return log_count / log_max

    def calculate_revenue_weight(self, total_revenue: float) -> float:
        """
        Calculate revenue weight (0-1 scale).

        Uses log scaling for revenue since it follows power law distribution.
        """
        if total_revenue <= 0:
            return 0.0

        import math
        # Log scaling for revenue
        log_revenue = math.log(total_revenue + 1)
        log_max = math.log(self.max_revenue + 1)

        weight = min(log_revenue / log_max, 1.0)
        return weight

    def calculate_sentiment_boost(self, avg_sentiment: float) -> float:
        """
        Calculate sentiment boost multiplier (1.0 to 1.5).

        Positive sentiment = higher priority (customers are engaged)
        Negative sentiment = still important but slightly lower boost
        """
        # Map sentiment (-1 to 1) to boost (1.0 to 1.5)
        # Neutral (0) -> 1.25
        # Very positive (1) -> 1.5
        # Very negative (-1) -> 1.0
        boost = 1.25 + (avg_sentiment * 0.25)
        return max(1.0, min(1.5, boost))

    def get_effort_factor(self, estimated_effort: str) -> float:
        """
        Get effort factor for normalization.

        Smaller effort = higher priority (easier wins)
        """
        effort_map = {
            "small": 1.0,
            "medium": 2.0,
            "large": 3.0,
            None: 2.0  # Default to medium
        }
        return effort_map.get(estimated_effort, 2.0)

    def calculate_priority_score(
        self,
        request_count: int,
        total_revenue: float,
        avg_sentiment: float,
        estimated_effort: str = "medium",
        max_count: int = 100
    ) -> float:
        """
        Calculate overall priority score.

        Args:
            request_count: Number of requests for this feature
            total_revenue: Total revenue from customers requesting feature
            avg_sentiment: Average sentiment score (-1 to 1)
            estimated_effort: "small", "medium", or "large"
            max_count: Maximum request count (for normalization)

        Returns:
            Priority score (higher = more important)
        """
        frequency = self.calculate_frequency_score(request_count, max_count)
        revenue_weight = self.calculate_revenue_weight(total_revenue)
        sentiment_boost = self.calculate_sentiment_boost(avg_sentiment)
        effort_factor = self.get_effort_factor(estimated_effort)

        # Calculate priority
        priority = (frequency * revenue_weight * sentiment_boost) / effort_factor

        # Scale to 0-100 for readability
        priority_scaled = priority * 100

        return round(priority_scaled, 2)

    def rank_roadmap_items(
        self,
        items: List[Dict]
    ) -> List[Tuple[Dict, int, float]]:
        """
        Rank roadmap items by priority score.

        Args:
            items: List of item dictionaries with keys:
                - request_count
                - total_revenue
                - avg_sentiment
                - estimated_effort (optional)
                - title (optional, for display)

        Returns:
            List of (item, rank, priority_score) tuples, sorted by priority
        """
        # Find max count for normalization
        max_count = max((item.get("request_count", 0) for item in items), default=100)

        # Calculate priorities
        scored_items = []
        for item in items:
            priority = self.calculate_priority_score(
                request_count=item.get("request_count", 0),
                total_revenue=item.get("total_revenue", 0.0),
                avg_sentiment=item.get("avg_sentiment", 0.0),
                estimated_effort=item.get("estimated_effort", "medium"),
                max_count=max_count
            )

            scored_items.append((item, priority))

        # Sort by priority (descending)
        scored_items.sort(key=lambda x: x[1], reverse=True)

        # Add ranks
        ranked_items = [
            (item, rank + 1, priority)
            for rank, (item, priority) in enumerate(scored_items)
        ]

        return ranked_items


def generate_priority_insights(items: List[Tuple[Dict, int, float]]) -> Dict:
    """
    Generate insights about priority distribution.

    Args:
        items: Ranked items from rank_roadmap_items()

    Returns:
        Dictionary of insights
    """
    if not items:
        return {}

    priorities = [priority for _, _, priority in items]

    return {
        "total_items": len(items),
        "highest_priority": max(priorities),
        "lowest_priority": min(priorities),
        "average_priority": round(sum(priorities) / len(priorities), 2),
        "high_priority_count": sum(1 for p in priorities if p > 60),
        "medium_priority_count": sum(1 for p in priorities if 30 <= p <= 60),
        "low_priority_count": sum(1 for p in priorities if p < 30),
    }


if __name__ == "__main__":
    # Test priority calculation
    print("Testing priority calculation...\n")

    calculator = PriorityCalculator()

    # Sample roadmap items
    test_items = [
        {
            "title": "Mobile App Performance",
            "request_count": 45,
            "total_revenue": 8_500_000,
            "avg_sentiment": -0.4,
            "estimated_effort": "medium"
        },
        {
            "title": "Slack Integration",
            "request_count": 32,
            "total_revenue": 3_200_000,
            "avg_sentiment": 0.3,
            "estimated_effort": "small"
        },
        {
            "title": "Advanced Reporting",
            "request_count": 28,
            "total_revenue": 5_100_000,
            "avg_sentiment": 0.5,
            "estimated_effort": "large"
        },
        {
            "title": "SSO Integration",
            "request_count": 18,
            "total_revenue": 6_700_000,
            "avg_sentiment": 0.2,
            "estimated_effort": "medium"
        },
        {
            "title": "Dark Mode",
            "request_count": 52,
            "total_revenue": 1_200_000,
            "avg_sentiment": 0.7,
            "estimated_effort": "small"
        },
    ]

    # Rank items
    ranked = calculator.rank_roadmap_items(test_items)

    print("=== Prioritized Roadmap ===\n")
    for item, rank, priority in ranked:
        print(f"#{rank}. {item['title']}")
        print(f"    Priority Score: {priority:.2f}")
        print(f"    Requests: {item['request_count']} | Revenue: ${item['total_revenue']:,}")
        print(f"    Sentiment: {item['avg_sentiment']:+.2f} | Effort: {item['estimated_effort']}")
        print()

    # Generate insights
    insights = generate_priority_insights(ranked)
    print("=== Priority Insights ===")
    for key, value in insights.items():
        print(f"  {key.replace('_', ' ').title()}: {value}")
