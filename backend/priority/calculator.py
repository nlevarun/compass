"""
Advanced Revenue-weighted priority scoring for roadmap items.

Priority Score = (Frequency × Revenue Weight × Sentiment Boost × Advanced Factors) / Effort

Components:
- Frequency: Number of requests (normalized)
- Revenue Weight: Total customer revenue requesting feature
- Sentiment Boost: Multiplier based on average sentiment (1.0 to 1.5)
- Effort: Estimated effort (inverse relationship)

Advanced Factors:
- Churn risk correlation
- Customer LTV weighting
- Request velocity (trending up/down)
- Customer segment importance
- Competitive pressure
- Technical complexity
"""

import sys
import os
import math
from typing import List, Dict, Tuple, Optional
from datetime import datetime, timedelta
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class PriorityCalculator:
    """
    Advanced priority calculator with multiple scoring factors.

    Enhanced Formula:
        Priority = (
            frequency_score ×
            revenue_weight ×
            sentiment_boost ×
            ltv_multiplier ×
            churn_risk_factor ×
            velocity_factor ×
            segment_weight ×
            competitive_pressure
        ) / (effort_factor × complexity_factor)

    Where:
        - frequency_score: Normalized request count (0-1)
        - revenue_weight: Log-scaled revenue impact (0-1)
        - sentiment_boost: 1.0 to 1.5 based on sentiment
        - ltv_multiplier: Customer lifetime value weighting
        - churn_risk_factor: Urgency from at-risk customers
        - velocity_factor: Request trending (up = urgent)
        - segment_weight: Importance of customer segment
        - competitive_pressure: Mentions of competitors
        - effort_factor: Development effort
        - complexity_factor: Technical complexity
    """

    def __init__(
        self,
        max_revenue: float = 10_000_000,
        enable_advanced_factors: bool = True
    ):
        """
        Initialize calculator.

        Args:
            max_revenue: Maximum expected customer revenue (for normalization)
            enable_advanced_factors: Whether to use advanced scoring factors
        """
        self.max_revenue = max_revenue
        self.enable_advanced_factors = enable_advanced_factors

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

    def calculate_ltv_multiplier(self, avg_customer_ltv: float) -> float:
        """
        Calculate LTV (Lifetime Value) multiplier.

        Higher LTV customers = higher priority (1.0 to 1.5)
        """
        if avg_customer_ltv <= 0:
            return 1.0

        # Log scale LTV
        # $10k LTV -> 1.0, $100k LTV -> 1.25, $500k+ LTV -> 1.5
        log_ltv = math.log(avg_customer_ltv + 1)
        log_base = math.log(10_000)  # $10k baseline
        log_max = math.log(500_000)  # $500k max

        multiplier = 1.0 + 0.5 * min((log_ltv - log_base) / (log_max - log_base), 1.0)
        return max(1.0, min(1.5, multiplier))

    def calculate_churn_risk_factor(
        self,
        churn_risk_score: float,
        total_revenue: float
    ) -> float:
        """
        Calculate churn risk urgency factor.

        High churn risk + high revenue = very urgent (up to 2.0x multiplier)

        Args:
            churn_risk_score: Average churn risk (0 to 1)
            total_revenue: Total revenue at risk

        Returns:
            Multiplier (1.0 to 2.0)
        """
        if churn_risk_score <= 0:
            return 1.0

        # Base multiplier from churn risk
        base_multiplier = 1.0 + churn_risk_score

        # Increase if high revenue at risk
        if total_revenue > 5_000_000:
            revenue_factor = 1.2
        elif total_revenue > 2_000_000:
            revenue_factor = 1.1
        else:
            revenue_factor = 1.0

        multiplier = base_multiplier * revenue_factor
        return min(multiplier, 2.0)  # Cap at 2.0x

    def calculate_velocity_factor(
        self,
        recent_request_count: int,
        historical_request_count: int,
        time_period_days: int = 30
    ) -> float:
        """
        Calculate request velocity factor (trending).

        Growing requests = more urgent (up to 1.5x)
        Declining requests = less urgent (down to 0.8x)

        Args:
            recent_request_count: Requests in recent period
            historical_request_count: Requests in earlier period
            time_period_days: Length of each period

        Returns:
            Multiplier (0.8 to 1.5)
        """
        if historical_request_count == 0:
            return 1.0

        # Calculate growth rate
        growth_rate = (recent_request_count - historical_request_count) / historical_request_count

        # Map growth rate to multiplier
        # +100% growth -> 1.5x
        # 0% growth -> 1.0x
        # -50% decline -> 0.8x
        if growth_rate > 0:
            # Growing: 1.0 to 1.5
            multiplier = 1.0 + min(growth_rate, 1.0) * 0.5
        else:
            # Declining: 1.0 to 0.8
            multiplier = 1.0 + max(growth_rate, -0.5) * 0.4

        return max(0.8, min(1.5, multiplier))

    def calculate_segment_weight(self, segment_importance: str) -> float:
        """
        Calculate customer segment importance weight.

        Args:
            segment_importance: "critical", "high", "medium", "low"

        Returns:
            Weight multiplier (0.7 to 1.3)
        """
        weights = {
            "critical": 1.3,
            "high": 1.15,
            "medium": 1.0,
            "low": 0.7,
            None: 1.0
        }
        return weights.get(segment_importance, 1.0)

    def calculate_competitive_pressure(self, competitor_mentions: int) -> float:
        """
        Calculate competitive pressure factor.

        Mentions of competitors in feedback = higher urgency

        Args:
            competitor_mentions: Number of times competitors mentioned

        Returns:
            Multiplier (1.0 to 1.4)
        """
        if competitor_mentions == 0:
            return 1.0

        # Log scale: 1 mention -> 1.1x, 5+ mentions -> 1.4x
        multiplier = 1.0 + min(math.log(competitor_mentions + 1) / 5, 0.4)
        return min(multiplier, 1.4)

    def calculate_complexity_factor(self, technical_complexity: int) -> float:
        """
        Calculate technical complexity factor.

        Higher complexity = lower priority (risk and time)

        Args:
            technical_complexity: Scale 1 (simple) to 5 (very complex)

        Returns:
            Factor (1.0 to 2.0)
        """
        if technical_complexity <= 0:
            return 1.0

        # Map complexity to factor
        # 1 (simple) -> 1.0x
        # 3 (moderate) -> 1.5x
        # 5 (complex) -> 2.0x
        factor = 1.0 + (technical_complexity - 1) * 0.25
        return min(max(factor, 1.0), 2.0)

    def calculate_priority_score(
        self,
        request_count: int,
        total_revenue: float,
        avg_sentiment: float,
        estimated_effort: str = "medium",
        max_count: int = 100,
        # Advanced factors (optional)
        avg_customer_ltv: float = 0.0,
        churn_risk_score: float = 0.0,
        recent_request_count: Optional[int] = None,
        historical_request_count: Optional[int] = None,
        segment_importance: str = "medium",
        competitor_mentions: int = 0,
        technical_complexity: int = 3
    ) -> float:
        """
        Calculate overall priority score with advanced factors.

        Args:
            request_count: Number of requests for this feature
            total_revenue: Total revenue from customers requesting feature
            avg_sentiment: Average sentiment score (-1 to 1)
            estimated_effort: "small", "medium", or "large"
            max_count: Maximum request count (for normalization)
            avg_customer_ltv: Average customer lifetime value
            churn_risk_score: Average churn risk (0 to 1)
            recent_request_count: Requests in recent 30 days
            historical_request_count: Requests in prior 30 days
            segment_importance: Customer segment weight
            competitor_mentions: Number of competitor mentions
            technical_complexity: Technical complexity (1-5)

        Returns:
            Priority score (higher = more important)
        """
        # Base factors
        frequency = self.calculate_frequency_score(request_count, max_count)
        revenue_weight = self.calculate_revenue_weight(total_revenue)
        sentiment_boost = self.calculate_sentiment_boost(avg_sentiment)
        effort_factor = self.get_effort_factor(estimated_effort)

        # Advanced factors (if enabled)
        if self.enable_advanced_factors:
            ltv_multiplier = self.calculate_ltv_multiplier(avg_customer_ltv)
            churn_risk_factor = self.calculate_churn_risk_factor(churn_risk_score, total_revenue)

            # Velocity factor (if data provided)
            if recent_request_count is not None and historical_request_count is not None:
                velocity_factor = self.calculate_velocity_factor(
                    recent_request_count, historical_request_count
                )
            else:
                velocity_factor = 1.0

            segment_weight = self.calculate_segment_weight(segment_importance)
            competitive_pressure = self.calculate_competitive_pressure(competitor_mentions)
            complexity_factor = self.calculate_complexity_factor(technical_complexity)
        else:
            # Use neutral values if advanced factors disabled
            ltv_multiplier = 1.0
            churn_risk_factor = 1.0
            velocity_factor = 1.0
            segment_weight = 1.0
            competitive_pressure = 1.0
            complexity_factor = 1.0

        # Calculate priority with all factors
        priority = (
            frequency *
            revenue_weight *
            sentiment_boost *
            ltv_multiplier *
            churn_risk_factor *
            velocity_factor *
            segment_weight *
            competitive_pressure
        ) / (effort_factor * complexity_factor)

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


def generate_priority_explanation(
    item: Dict,
    priority_score: float,
    calculator: PriorityCalculator
) -> Dict:
    """
    Generate detailed explanation of why an item has its priority score.

    Args:
        item: Roadmap item dictionary
        priority_score: Calculated priority score
        calculator: PriorityCalculator instance

    Returns:
        Dictionary with explanation and contributing factors
    """
    factors = []

    # Request count factor
    request_count = item.get('request_count', 0)
    if request_count > 30:
        factors.append({
            'factor': 'High Demand',
            'value': f"{request_count} requests",
            'impact': 'positive',
            'weight': 'high',
            'description': 'Many customers are asking for this feature'
        })
    elif request_count > 15:
        factors.append({
            'factor': 'Moderate Demand',
            'value': f"{request_count} requests",
            'impact': 'positive',
            'weight': 'medium',
            'description': 'Solid customer interest in this feature'
        })

    # Revenue factor
    revenue = item.get('total_revenue', 0)
    if revenue > 5_000_000:
        factors.append({
            'factor': 'Critical Revenue Impact',
            'value': f"${revenue:,.0f}",
            'impact': 'positive',
            'weight': 'critical',
            'description': 'High-value customers are requesting this'
        })
    elif revenue > 1_000_000:
        factors.append({
            'factor': 'Significant Revenue',
            'value': f"${revenue:,.0f}",
            'impact': 'positive',
            'weight': 'high',
            'description': 'Notable revenue opportunity'
        })

    # Sentiment factor
    sentiment = item.get('avg_sentiment', 0)
    if sentiment < -0.3:
        factors.append({
            'factor': 'Pain Point',
            'value': f"{sentiment:+.2f} sentiment",
            'impact': 'urgent',
            'weight': 'high',
            'description': 'Negative sentiment suggests customers are frustrated'
        })
    elif sentiment > 0.3:
        factors.append({
            'factor': 'High Enthusiasm',
            'value': f"{sentiment:+.2f} sentiment",
            'impact': 'positive',
            'weight': 'medium',
            'description': 'Customers are excited about this feature'
        })

    # Churn risk factor
    churn_risk = item.get('churn_risk_score', 0)
    if churn_risk > 0.6:
        factors.append({
            'factor': 'Churn Prevention',
            'value': f"{churn_risk:.1%} risk",
            'impact': 'urgent',
            'weight': 'critical',
            'description': 'At-risk customers need this to stay'
        })

    # Velocity factor
    recent = item.get('recent_request_count', 0)
    historical = item.get('historical_request_count', 0)
    if recent > 0 and historical > 0:
        growth = (recent - historical) / historical
        if growth > 0.5:
            factors.append({
                'factor': 'Growing Demand',
                'value': f"+{growth:.0%} trend",
                'impact': 'positive',
                'weight': 'high',
                'description': 'Requests are increasing rapidly'
            })
        elif growth < -0.3:
            factors.append({
                'factor': 'Declining Interest',
                'value': f"{growth:.0%} trend",
                'impact': 'negative',
                'weight': 'medium',
                'description': 'Requests are decreasing over time'
            })

    # Competitive pressure
    competitor_mentions = item.get('competitor_mentions', 0)
    if competitor_mentions > 3:
        factors.append({
            'factor': 'Competitive Threat',
            'value': f"{competitor_mentions} mentions",
            'impact': 'urgent',
            'weight': 'high',
            'description': 'Customers are comparing to competitors'
        })

    # Effort factor
    effort = item.get('estimated_effort', 'medium')
    if effort == 'small':
        factors.append({
            'factor': 'Quick Win',
            'value': 'Small effort',
            'impact': 'positive',
            'weight': 'medium',
            'description': 'Easy to implement, high ROI'
        })
    elif effort == 'large':
        factors.append({
            'factor': 'Large Investment',
            'value': 'Large effort',
            'impact': 'negative',
            'weight': 'medium',
            'description': 'Requires significant development time'
        })

    # Complexity factor
    complexity = item.get('technical_complexity', 3)
    if complexity >= 4:
        factors.append({
            'factor': 'Technical Complexity',
            'value': f"Complexity {complexity}/5",
            'impact': 'negative',
            'weight': 'medium',
            'description': 'Complex implementation with technical challenges'
        })

    # Generate summary explanation
    priority_level = "CRITICAL" if priority_score > 80 else \
                    "HIGH" if priority_score > 60 else \
                    "MEDIUM" if priority_score > 30 else "LOW"

    explanation = f"This feature has {priority_level} priority (score: {priority_score:.1f}). "

    critical_factors = [f for f in factors if f['weight'] == 'critical']
    if critical_factors:
        explanation += "Critical factors: " + ", ".join(f['factor'] for f in critical_factors) + ". "

    urgent_factors = [f for f in factors if f['impact'] == 'urgent']
    if urgent_factors:
        explanation += "Urgent due to: " + ", ".join(f['factor'] for f in urgent_factors) + ". "

    return {
        'priority_score': priority_score,
        'priority_level': priority_level,
        'summary': explanation.strip(),
        'contributing_factors': factors,
        'confidence': 'high' if len(factors) >= 4 else 'medium' if len(factors) >= 2 else 'low'
    }


def identify_at_risk_customers(
    feedback_items: List[Dict],
    revenue_threshold: float = 100_000,
    sentiment_threshold: float = -0.3,
    recent_days: int = 30
) -> List[Dict]:
    """
    Identify at-risk customers based on feedback patterns.

    At-risk indicators:
    - High revenue customer
    - Negative sentiment
    - Recent feedback spike
    - Multiple complaints about same issue

    Args:
        feedback_items: List of feedback with customer info
        revenue_threshold: Minimum revenue to be considered high-value
        sentiment_threshold: Maximum sentiment to be considered negative
        recent_days: Days to consider "recent"

    Returns:
        List of at-risk customer summaries
    """
    from datetime import datetime, timedelta

    # Group feedback by customer
    customer_feedback = defaultdict(list)
    for item in feedback_items:
        customer_name = item.get('customer_name')
        if customer_name:
            customer_feedback[customer_name].append(item)

    at_risk_customers = []
    cutoff_date = datetime.utcnow() - timedelta(days=recent_days)

    for customer_name, feedback_list in customer_feedback.items():
        # Get customer revenue (use max if multiple values)
        revenues = [f.get('customer_revenue', 0) for f in feedback_list if f.get('customer_revenue')]
        customer_revenue = max(revenues) if revenues else 0

        # Skip low-revenue customers
        if customer_revenue < revenue_threshold:
            continue

        # Calculate metrics
        total_feedback = len(feedback_list)
        recent_feedback = [
            f for f in feedback_list
            if f.get('submitted_at') and f['submitted_at'] >= cutoff_date
        ]
        recent_count = len(recent_feedback)

        sentiments = [f.get('sentiment_score', 0) for f in feedback_list if f.get('sentiment_score') is not None]
        avg_sentiment = sum(sentiments) / len(sentiments) if sentiments else 0

        # Calculate risk score
        risk_score = 0.0

        # High revenue = higher risk weight
        if customer_revenue > 1_000_000:
            risk_score += 0.4
        elif customer_revenue > 500_000:
            risk_score += 0.3
        else:
            risk_score += 0.2

        # Negative sentiment
        if avg_sentiment < -0.5:
            risk_score += 0.4
        elif avg_sentiment < sentiment_threshold:
            risk_score += 0.2

        # Recent feedback spike
        if recent_count >= 5:
            risk_score += 0.3
        elif recent_count >= 3:
            risk_score += 0.2

        # Multiple complaints
        if total_feedback >= 10:
            risk_score += 0.2

        # Consider at-risk if score > 0.6
        if risk_score > 0.6:
            at_risk_customers.append({
                'customer_name': customer_name,
                'customer_revenue': customer_revenue,
                'risk_score': round(risk_score, 2),
                'total_feedback': total_feedback,
                'recent_feedback': recent_count,
                'avg_sentiment': round(avg_sentiment, 2),
                'risk_factors': _get_risk_factors(
                    customer_revenue, avg_sentiment, recent_count, total_feedback
                )
            })

    # Sort by risk score (highest first)
    at_risk_customers.sort(key=lambda x: x['risk_score'], reverse=True)

    return at_risk_customers


def _get_risk_factors(
    revenue: float,
    sentiment: float,
    recent_count: int,
    total_count: int
) -> List[str]:
    """Get list of risk factor descriptions."""
    factors = []

    if revenue > 1_000_000:
        factors.append(f"High-value customer (${revenue:,.0f} revenue)")

    if sentiment < -0.5:
        factors.append(f"Very negative sentiment ({sentiment:+.2f})")
    elif sentiment < -0.3:
        factors.append(f"Negative sentiment ({sentiment:+.2f})")

    if recent_count >= 5:
        factors.append(f"Recent feedback spike ({recent_count} in last 30 days)")

    if total_count >= 10:
        factors.append(f"Frequent complaints ({total_count} total)")

    return factors


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
