"""
Revenue Impact Prediction Model

Predicts revenue impact of building features based on historical data.
Uses ML when sufficient data exists, falls back to heuristics otherwise.

Formula:
    Predicted Impact = Base Impact × Confidence Multiplier

Where:
    - Base Impact: Estimated from similar past features or heuristics
    - Confidence: Based on data quality and historical accuracy
"""

import sys
import os
import json
import pickle
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta

# Try to import numpy, but make it optional
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False
    np = None

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class ImpactPredictor:
    """
    Predict revenue impact of roadmap items using ML and heuristics.

    Uses historical data:
    - Past features shipped
    - Feedback volume before/after
    - Revenue changes post-launch
    - Customer retention metrics
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize impact predictor.

        Args:
            model_path: Path to saved ML model (optional)
        """
        self.model = None
        self.model_trained = False
        self.historical_data = []
        self.feature_importance = {}

        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    def add_historical_data(
        self,
        feature_title: str,
        feedback_volume_before: int,
        feedback_volume_after: int,
        request_count: int,
        impacted_revenue: float,
        avg_sentiment: float,
        effort: str,
        actual_revenue_increase: float,
        shipped_date: datetime
    ):
        """
        Add historical data point for training.

        Args:
            feature_title: Name of the feature
            feedback_volume_before: Total feedback 30 days before launch
            feedback_volume_after: Total feedback 30 days after launch
            request_count: Number of requests for this feature
            impacted_revenue: Total revenue from requesting customers
            avg_sentiment: Average sentiment of feedback
            effort: Estimated effort (small/medium/large)
            actual_revenue_increase: Actual MRR increase post-launch
            shipped_date: When feature was shipped
        """
        self.historical_data.append({
            'feature_title': feature_title,
            'feedback_volume_before': feedback_volume_before,
            'feedback_volume_after': feedback_volume_after,
            'request_count': request_count,
            'impacted_revenue': impacted_revenue,
            'avg_sentiment': avg_sentiment,
            'effort': effort,
            'actual_revenue_increase': actual_revenue_increase,
            'shipped_date': shipped_date,
            # Derived features
            'feedback_reduction_ratio': feedback_volume_after / max(feedback_volume_before, 1),
            'revenue_per_request': impacted_revenue / max(request_count, 1),
            'effort_numeric': {'small': 1, 'medium': 2, 'large': 3}.get(effort, 2)
        })

    def train_model(self, min_data_points: int = 10) -> bool:
        """
        Train ML model on historical data.

        Returns:
            True if model trained successfully, False if insufficient data
        """
        if not NUMPY_AVAILABLE:
            print("NumPy not available. Install with: pip install numpy")
            return False

        if len(self.historical_data) < min_data_points:
            print(f"Insufficient data for ML training: {len(self.historical_data)} < {min_data_points}")
            return False

        try:
            from sklearn.ensemble import RandomForestRegressor
            from sklearn.model_selection import train_test_split
            from sklearn.metrics import mean_absolute_error, r2_score

            # Prepare features
            X = []
            y = []

            for data in self.historical_data:
                features = [
                    data['request_count'],
                    data['impacted_revenue'],
                    data['avg_sentiment'],
                    data['effort_numeric'],
                    data['feedback_volume_before'],
                    data['revenue_per_request'],
                    data['feedback_reduction_ratio']
                ]
                X.append(features)
                y.append(data['actual_revenue_increase'])

            X = np.array(X)
            y = np.array(y)

            # Train model
            self.model = RandomForestRegressor(
                n_estimators=100,
                max_depth=10,
                min_samples_split=5,
                random_state=42
            )

            # If we have enough data, validate
            if len(X) >= 20:
                X_train, X_test, y_train, y_test = train_test_split(
                    X, y, test_size=0.2, random_state=42
                )
                self.model.fit(X_train, y_train)

                # Evaluate
                y_pred = self.model.predict(X_test)
                mae = mean_absolute_error(y_test, y_pred)
                r2 = r2_score(y_test, y_pred)

                print(f"Model trained - MAE: ${mae:,.2f}, R²: {r2:.3f}")
            else:
                # Train on all data if we have limited samples
                self.model.fit(X, y)
                print(f"Model trained on {len(X)} samples")

            # Feature importance
            feature_names = [
                'request_count', 'impacted_revenue', 'avg_sentiment',
                'effort', 'feedback_volume', 'revenue_per_request',
                'feedback_reduction'
            ]
            self.feature_importance = dict(zip(
                feature_names,
                self.model.feature_importances_
            ))

            self.model_trained = True
            return True

        except ImportError:
            print("scikit-learn not available. Install with: pip install scikit-learn")
            return False
        except Exception as e:
            print(f"Error training model: {e}")
            return False

    def predict_impact(
        self,
        request_count: int,
        impacted_revenue: float,
        avg_sentiment: float,
        effort: str,
        feedback_volume_current: int = 0
    ) -> Dict:
        """
        Predict revenue impact of building a feature.

        Args:
            request_count: Number of requests for this feature
            impacted_revenue: Total revenue from requesting customers
            avg_sentiment: Average sentiment of feedback
            effort: Estimated effort (small/medium/large)
            feedback_volume_current: Current total feedback volume

        Returns:
            Dictionary with prediction and confidence
        """
        # Try ML prediction first
        if self.model_trained and self.model:
            predicted_impact = self._predict_ml(
                request_count, impacted_revenue, avg_sentiment,
                effort, feedback_volume_current
            )
            confidence = self._calculate_confidence_ml()
            method = 'machine_learning'
        else:
            # Fall back to heuristics
            predicted_impact = self._predict_heuristic(
                request_count, impacted_revenue, avg_sentiment, effort
            )
            confidence = self._calculate_confidence_heuristic(
                request_count, impacted_revenue
            )
            method = 'heuristic'

        # Calculate impact range
        impact_range = self._calculate_impact_range(predicted_impact, confidence)

        # Generate explanation
        explanation = self._generate_explanation(
            predicted_impact, request_count, impacted_revenue,
            avg_sentiment, effort, method
        )

        return {
            'predicted_revenue_increase': round(predicted_impact, 2),
            'confidence_score': round(confidence, 3),
            'impact_range': {
                'min': round(impact_range[0], 2),
                'max': round(impact_range[1], 2)
            },
            'prediction_method': method,
            'explanation': explanation,
            'factors': self._get_contributing_factors(
                request_count, impacted_revenue, avg_sentiment, effort
            )
        }

    def _predict_ml(
        self,
        request_count: int,
        impacted_revenue: float,
        avg_sentiment: float,
        effort: str,
        feedback_volume: int
    ) -> float:
        """Use ML model to predict impact."""
        if not NUMPY_AVAILABLE:
            # Fallback to heuristics if numpy not available
            return self._predict_heuristic(
                request_count, impacted_revenue, avg_sentiment, effort
            )

        effort_numeric = {'small': 1, 'medium': 2, 'large': 3}.get(effort, 2)
        revenue_per_request = impacted_revenue / max(request_count, 1)
        feedback_reduction = 0.7  # Assume typical reduction

        features = np.array([[
            request_count,
            impacted_revenue,
            avg_sentiment,
            effort_numeric,
            feedback_volume,
            revenue_per_request,
            feedback_reduction
        ]])

        prediction = self.model.predict(features)[0]

        # Ensure non-negative
        return max(prediction, 0)

    def _predict_heuristic(
        self,
        request_count: int,
        impacted_revenue: float,
        avg_sentiment: float,
        effort: str
    ) -> float:
        """
        Use heuristics to predict impact when no ML model available.

        Heuristic formula:
            Impact = (Base Impact × Sentiment Multiplier) / Effort Factor

        Where:
            - Base Impact = 2-5% of impacted revenue + $500 per request
            - Sentiment Multiplier = 0.8 to 1.3
            - Effort Factor = 1.0 (small), 1.5 (medium), 2.0 (large)
        """
        # Base impact: percentage of revenue at risk + per-request value
        revenue_percentage = 0.03  # Assume 3% of revenue impact
        per_request_value = 500  # $500 MRR per request (conservative)

        base_impact = (impacted_revenue * revenue_percentage) + (request_count * per_request_value)

        # Sentiment multiplier (very negative reduces impact estimate)
        # -1 -> 0.8, 0 -> 1.05, +1 -> 1.3
        sentiment_multiplier = 1.05 + (avg_sentiment * 0.25)
        sentiment_multiplier = max(0.8, min(1.3, sentiment_multiplier))

        # Effort factor (larger effort = delayed returns = lower immediate impact)
        effort_factor = {'small': 1.0, 'medium': 1.5, 'large': 2.0}.get(effort, 1.5)

        predicted_impact = (base_impact * sentiment_multiplier) / effort_factor

        return predicted_impact

    def _calculate_confidence_ml(self) -> float:
        """Calculate confidence for ML predictions."""
        if not self.historical_data:
            return 0.5

        # Confidence based on amount of historical data
        data_points = len(self.historical_data)

        # Scale confidence: 10 points = 0.6, 50+ points = 0.9
        if data_points < 10:
            confidence = 0.5
        elif data_points < 50:
            confidence = 0.5 + (data_points - 10) * 0.01  # 0.5 to 0.9
        else:
            confidence = 0.9

        return min(confidence, 0.95)  # Cap at 0.95

    def _calculate_confidence_heuristic(
        self,
        request_count: int,
        impacted_revenue: float
    ) -> float:
        """Calculate confidence for heuristic predictions."""
        # Lower confidence for heuristics
        base_confidence = 0.4

        # Increase confidence with more data points
        if request_count > 20:
            base_confidence += 0.15
        elif request_count > 10:
            base_confidence += 0.1

        if impacted_revenue > 1_000_000:
            base_confidence += 0.1
        elif impacted_revenue > 500_000:
            base_confidence += 0.05

        return min(base_confidence, 0.7)  # Cap at 0.7 for heuristics

    def _calculate_impact_range(
        self,
        predicted_impact: float,
        confidence: float
    ) -> Tuple[float, float]:
        """Calculate min/max impact range based on confidence."""
        # Lower confidence = wider range
        range_factor = 1 - confidence

        min_impact = predicted_impact * (1 - range_factor)
        max_impact = predicted_impact * (1 + range_factor)

        return (max(min_impact, 0), max_impact)

    def _generate_explanation(
        self,
        predicted_impact: float,
        request_count: int,
        impacted_revenue: float,
        avg_sentiment: float,
        effort: str,
        method: str
    ) -> str:
        """Generate human-readable explanation of prediction."""
        explanations = []

        explanations.append(
            f"Building this feature is expected to increase MRR by ${predicted_impact:,.0f}."
        )

        if request_count > 30:
            explanations.append(
                f"High request volume ({request_count} requests) indicates strong demand."
            )
        elif request_count > 15:
            explanations.append(
                f"Moderate request volume ({request_count} requests) shows interest."
            )

        if impacted_revenue > 2_000_000:
            explanations.append(
                f"High-value customers (${impacted_revenue:,.0f} total revenue) are requesting this."
            )
        elif impacted_revenue > 500_000:
            explanations.append(
                f"Significant revenue at stake (${impacted_revenue:,.0f})."
            )

        if avg_sentiment < -0.3:
            explanations.append(
                "Negative sentiment suggests this is a pain point - addressing it may prevent churn."
            )
        elif avg_sentiment > 0.3:
            explanations.append(
                "Positive sentiment indicates customers are eager for this feature."
            )

        if method == 'heuristic':
            explanations.append(
                "Prediction based on heuristics. Add historical data to improve accuracy."
            )

        return " ".join(explanations)

    def _get_contributing_factors(
        self,
        request_count: int,
        impacted_revenue: float,
        avg_sentiment: float,
        effort: str
    ) -> List[Dict]:
        """Get weighted contributing factors."""
        factors = []

        # Request volume factor
        if request_count > 20:
            weight = 'high'
            impact = 'positive'
        elif request_count > 10:
            weight = 'medium'
            impact = 'positive'
        else:
            weight = 'low'
            impact = 'neutral'

        factors.append({
            'name': 'Request Volume',
            'value': request_count,
            'weight': weight,
            'impact': impact
        })

        # Revenue factor
        if impacted_revenue > 1_000_000:
            weight = 'high'
            impact = 'positive'
        elif impacted_revenue > 500_000:
            weight = 'medium'
            impact = 'positive'
        else:
            weight = 'low'
            impact = 'neutral'

        factors.append({
            'name': 'Impacted Revenue',
            'value': f"${impacted_revenue:,.0f}",
            'weight': weight,
            'impact': impact
        })

        # Sentiment factor
        if avg_sentiment < -0.2:
            weight = 'medium'
            impact = 'urgent'
        elif avg_sentiment > 0.2:
            weight = 'medium'
            impact = 'positive'
        else:
            weight = 'low'
            impact = 'neutral'

        factors.append({
            'name': 'Customer Sentiment',
            'value': f"{avg_sentiment:+.2f}",
            'weight': weight,
            'impact': impact
        })

        # Effort factor
        effort_impact = {'small': 'positive', 'medium': 'neutral', 'large': 'negative'}
        factors.append({
            'name': 'Development Effort',
            'value': effort,
            'weight': 'medium',
            'impact': effort_impact.get(effort, 'neutral')
        })

        return factors

    def save_model(self, path: str):
        """Save trained model to disk."""
        if not self.model_trained:
            raise ValueError("No trained model to save")

        model_data = {
            'model': self.model,
            'historical_data': self.historical_data,
            'feature_importance': self.feature_importance,
            'trained_at': datetime.utcnow().isoformat()
        }

        with open(path, 'wb') as f:
            pickle.dump(model_data, f)

        print(f"Model saved to {path}")

    def load_model(self, path: str):
        """Load trained model from disk."""
        with open(path, 'rb') as f:
            model_data = pickle.load(f)

        self.model = model_data['model']
        self.historical_data = model_data.get('historical_data', [])
        self.feature_importance = model_data.get('feature_importance', {})
        self.model_trained = True

        print(f"Model loaded from {path}")


if __name__ == "__main__":
    # Test impact prediction
    print("Testing Impact Predictor...\n")

    predictor = ImpactPredictor()

    # Test with heuristics (no historical data)
    print("=== Heuristic Prediction ===")
    result = predictor.predict_impact(
        request_count=25,
        impacted_revenue=1_500_000,
        avg_sentiment=-0.3,
        effort='medium'
    )

    print(f"Predicted Revenue Increase: ${result['predicted_revenue_increase']:,.2f}")
    print(f"Confidence: {result['confidence_score']:.1%}")
    print(f"Impact Range: ${result['impact_range']['min']:,.0f} - ${result['impact_range']['max']:,.0f}")
    print(f"Method: {result['prediction_method']}")
    print(f"\nExplanation:\n{result['explanation']}")
    print(f"\nContributing Factors:")
    for factor in result['factors']:
        print(f"  - {factor['name']}: {factor['value']} ({factor['weight']} weight, {factor['impact']} impact)")

    print("\n" + "="*60 + "\n")

    # Add historical data
    print("=== Adding Historical Data ===")
    predictor.add_historical_data(
        feature_title="Mobile App Performance",
        feedback_volume_before=100,
        feedback_volume_after=30,
        request_count=45,
        impacted_revenue=8_500_000,
        avg_sentiment=-0.4,
        effort='medium',
        actual_revenue_increase=85_000,
        shipped_date=datetime.utcnow() - timedelta(days=60)
    )

    predictor.add_historical_data(
        feature_title="Slack Integration",
        feedback_volume_before=80,
        feedback_volume_after=25,
        request_count=32,
        impacted_revenue=3_200_000,
        avg_sentiment=0.3,
        effort='small',
        actual_revenue_increase=42_000,
        shipped_date=datetime.utcnow() - timedelta(days=90)
    )

    # Add more historical data points
    for i in range(8):
        predictor.add_historical_data(
            feature_title=f"Feature {i+1}",
            feedback_volume_before=50 + i*10,
            feedback_volume_after=15 + i*3,
            request_count=10 + i*5,
            impacted_revenue=500_000 + i*300_000,
            avg_sentiment=-0.2 + i*0.1,
            effort=['small', 'medium', 'large'][i % 3],
            actual_revenue_increase=10_000 + i*5_000,
            shipped_date=datetime.utcnow() - timedelta(days=30*(i+1))
        )

    print(f"Added {len(predictor.historical_data)} historical data points")

    # Train model
    print("\n=== Training ML Model ===")
    trained = predictor.train_model()

    if trained:
        print("\n=== ML Prediction ===")
        result_ml = predictor.predict_impact(
            request_count=25,
            impacted_revenue=1_500_000,
            avg_sentiment=-0.3,
            effort='medium',
            feedback_volume_current=200
        )

        print(f"Predicted Revenue Increase: ${result_ml['predicted_revenue_increase']:,.2f}")
        print(f"Confidence: {result_ml['confidence_score']:.1%}")
        print(f"Impact Range: ${result_ml['impact_range']['min']:,.0f} - ${result_ml['impact_range']['max']:,.0f}")
        print(f"Method: {result_ml['prediction_method']}")
        print(f"\nExplanation:\n{result_ml['explanation']}")
