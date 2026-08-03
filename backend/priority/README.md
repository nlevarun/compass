# Advanced Priority System Documentation

## Overview

Compass's advanced priority system combines multiple sophisticated scoring factors to prioritize roadmap items based on revenue impact, customer sentiment, churn risk, and competitive pressure.

## Architecture

### Core Modules

1. **calculator.py** - Enhanced priority calculator with advanced factors
2. **impact_predictor.py** - ML-based revenue impact prediction
3. **custom_scoring.py** - Custom formula engine (ICE, RICE, WSJF, custom)

---

## Priority Calculator (`calculator.py`)

### Enhanced Scoring Formula

```
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
```

### Scoring Factors

#### 1. Frequency Score (0-1)
- **Purpose**: Normalize request volume
- **Formula**: `log(count + 1) / log(max_count + 1)`
- **Why log scale**: Prevents very popular features from completely dominating

#### 2. Revenue Weight (0-1)
- **Purpose**: Weight by customer revenue
- **Formula**: `log(revenue + 1) / log(max_revenue + 1)`
- **Example**: $1M revenue → 0.75, $10M revenue → 1.0

#### 3. Sentiment Boost (1.0-1.5)
- **Purpose**: Account for customer emotion
- **Mapping**:
  - Very negative (-1.0) → 1.0x
  - Neutral (0) → 1.25x
  - Very positive (+1.0) → 1.5x
- **Insight**: Negative sentiment = pain point (still prioritize)

#### 4. LTV Multiplier (1.0-1.5)
- **Purpose**: Weight high-lifetime-value customers
- **Formula**: Log-scaled based on customer LTV
- **Example**:
  - $10k LTV → 1.0x
  - $100k LTV → 1.25x
  - $500k+ LTV → 1.5x

#### 5. Churn Risk Factor (1.0-2.0)
- **Purpose**: Urgent features from at-risk customers
- **Formula**: `(1 + churn_risk) × revenue_factor`
- **Example**:
  - 60% churn risk + $5M revenue → 1.8x urgency
  - Low churn + low revenue → 1.0x

#### 6. Velocity Factor (0.8-1.5)
- **Purpose**: Trending features (growing vs declining)
- **Formula**: Based on request growth rate
- **Example**:
  - +100% growth in last 30 days → 1.5x
  - -50% decline → 0.8x

#### 7. Segment Weight (0.7-1.3)
- **Purpose**: Customer segment importance
- **Mapping**:
  - Critical segment → 1.3x
  - High → 1.15x
  - Medium → 1.0x
  - Low → 0.7x

#### 8. Competitive Pressure (1.0-1.4)
- **Purpose**: Urgency from competitor mentions
- **Formula**: `1.0 + min(log(mentions + 1) / 5, 0.4)`
- **Example**: 5+ competitor mentions → 1.4x

#### 9. Effort Factor (1.0-3.0)
- **Purpose**: Development effort
- **Mapping**:
  - Small → 1.0x (quick win)
  - Medium → 2.0x
  - Large → 3.0x

#### 10. Complexity Factor (1.0-2.0)
- **Purpose**: Technical risk and difficulty
- **Formula**: `1.0 + (complexity - 1) × 0.25`
- **Scale**: 1 (simple) to 5 (very complex)

### Usage Example

```python
from priority.calculator import PriorityCalculator

calculator = PriorityCalculator(enable_advanced_factors=True)

score = calculator.calculate_priority_score(
    request_count=45,
    total_revenue=8_500_000,
    avg_sentiment=-0.4,
    estimated_effort='medium',
    max_count=100,
    # Advanced factors
    avg_customer_ltv=150_000,
    churn_risk_score=0.7,
    recent_request_count=20,
    historical_request_count=10,
    segment_importance='critical',
    competitor_mentions=5,
    technical_complexity=3
)

print(f"Priority Score: {score}")  # e.g., 85.3
```

### Priority Explanations

```python
from priority.calculator import generate_priority_explanation

explanation = generate_priority_explanation(item_dict, score, calculator)

# Returns:
{
    'priority_score': 85.3,
    'priority_level': 'HIGH',
    'summary': 'This feature has HIGH priority (score: 85.3). Critical factors: Churn Prevention, Critical Revenue Impact.',
    'contributing_factors': [
        {
            'factor': 'High Demand',
            'value': '45 requests',
            'impact': 'positive',
            'weight': 'high',
            'description': 'Many customers are asking for this feature'
        },
        # ... more factors
    ],
    'confidence': 'high'
}
```

### At-Risk Customer Detection

```python
from priority.calculator import identify_at_risk_customers

at_risk = identify_at_risk_customers(
    feedback_items=feedback_list,
    revenue_threshold=100_000,
    sentiment_threshold=-0.3,
    recent_days=30
)

# Returns:
[
    {
        'customer_name': 'Acme Corp',
        'customer_revenue': 2_500_000,
        'risk_score': 0.85,
        'total_feedback': 12,
        'recent_feedback': 6,
        'avg_sentiment': -0.6,
        'risk_factors': [
            'High-value customer ($2,500,000 revenue)',
            'Very negative sentiment (-0.60)',
            'Recent feedback spike (6 in last 30 days)'
        ]
    }
]
```

---

## Impact Predictor (`impact_predictor.py`)

### Purpose

Predict revenue impact: **"If we build this feature, expect $X MRR increase"**

### Prediction Methods

1. **Machine Learning** (when sufficient historical data)
   - RandomForestRegressor
   - Trained on past feature outcomes
   - Features: request count, revenue, sentiment, effort, feedback volume
   - Confidence increases with more data

2. **Heuristics** (fallback when no ML model)
   - Formula: `(Base Impact × Sentiment Multiplier) / Effort Factor`
   - Base Impact: 3% of revenue + $500 per request
   - Conservative estimates

### Usage Example

```python
from priority.impact_predictor import ImpactPredictor

predictor = ImpactPredictor()

# Add historical data (after features ship)
predictor.add_historical_data(
    feature_title="Mobile App Performance",
    feedback_volume_before=100,
    feedback_volume_after=30,
    request_count=45,
    impacted_revenue=8_500_000,
    avg_sentiment=-0.4,
    effort='medium',
    actual_revenue_increase=85_000,
    shipped_date=datetime(2026, 6, 1)
)

# Train ML model (needs 10+ data points)
predictor.train_model()

# Predict impact for new feature
prediction = predictor.predict_impact(
    request_count=25,
    impacted_revenue=1_500_000,
    avg_sentiment=-0.3,
    effort='medium'
)

print(f"Predicted Revenue Increase: ${prediction['predicted_revenue_increase']:,}")
print(f"Confidence: {prediction['confidence_score']:.1%}")
print(f"Range: ${prediction['impact_range']['min']:,} - ${prediction['impact_range']['max']:,}")
```

### Prediction Output

```json
{
    "predicted_revenue_increase": 42500.0,
    "confidence_score": 0.65,
    "impact_range": {
        "min": 14875.0,
        "max": 70125.0
    },
    "prediction_method": "machine_learning",
    "explanation": "Building this feature is expected to increase MRR by $42,500. High request volume (25 requests) indicates strong demand. Significant revenue at stake ($1,500,000). Negative sentiment suggests this is a pain point - addressing it may prevent churn.",
    "factors": [
        {
            "name": "Request Volume",
            "value": 25,
            "weight": "medium",
            "impact": "positive"
        },
        // ... more factors
    ]
}
```

### Training the Model

```python
# Save trained model
predictor.save_model('/path/to/model.pkl')

# Load existing model
predictor = ImpactPredictor(model_path='/path/to/model.pkl')
```

---

## Custom Scoring (`custom_scoring.py`)

### Purpose

Allow users to define their own prioritization formulas using popular frameworks or custom logic.

### Supported Frameworks

#### 1. ICE (Impact × Confidence × Ease)
```
Formula: (revenue / 1000000) * confidence * (4 - effort)
```

#### 2. RICE (Reach × Impact × Confidence / Effort)
```
Formula: (request_count * (revenue / 1000000) * confidence) / effort
```

#### 3. WSJF (Weighted Shortest Job First)
```
Formula: ((revenue / 1000000) + (churn_risk * 10) + (velocity * 2)) / effort
```

#### 4. Value vs. Effort
```
Formula: ((request_count * 0.3) + (revenue / 100000 * 0.7)) / effort
```

#### 5. Churn Prevention Priority
```
Formula: churn_risk * revenue / 1000000 * (4 - effort)
```

#### 6. Revenue-Weighted (Compass Default)
```
Formula: (log(request_count + 1) * log(revenue + 1) * (1.25 + sentiment * 0.25)) / effort
```

### Available Variables

| Variable | Description | Type | Example |
|----------|-------------|------|---------|
| `request_count` | Number of customer requests | numeric | 25 |
| `revenue` | Total revenue from requesters | numeric | 1,500,000 |
| `sentiment` | Average sentiment (-1 to 1) | numeric | -0.3 |
| `effort` | Effort estimate (1-3) | numeric | 2 |
| `ltv` | Average customer LTV | numeric | 50,000 |
| `churn_risk` | Churn risk score (0-1) | numeric | 0.6 |
| `velocity` | Request velocity (per week) | numeric | 2.5 |
| `segment_weight` | Segment importance (0-1) | numeric | 0.8 |
| `complexity` | Technical complexity (1-5) | numeric | 4 |
| `confidence` | Confidence in estimate (0-1) | numeric | 0.7 |

### Supported Operations

- **Operators**: `+`, `-`, `*`, `/`, `^` (power)
- **Functions**: `log()`, `sqrt()`, `max()`, `min()`, `abs()`, `pow()`
- **Parentheses**: For grouping

### Usage Example

```python
from priority.custom_scoring import CustomScoringEngine

engine = CustomScoringEngine()

# Use preset formula
ice_formula = engine.get_preset_formula('ice')
print(ice_formula['formula'])
# "(revenue / 1000000) * confidence * (4 - effort)"

# Calculate score
result = engine.calculate_score(
    formula=ice_formula['formula'],
    variables={
        'revenue': 1_500_000,
        'confidence': 0.7,
        'effort': 2
    }
)

print(f"ICE Score: {result['score']}")
# ICE Score: 72.5

# Custom formula
custom_formula = "(request_count * revenue / 1000000) / effort + churn_risk * 10"

# Validate first
validation = engine.validate_formula(custom_formula)
if validation['valid']:
    result = engine.calculate_score(custom_formula, {
        'request_count': 30,
        'revenue': 2_000_000,
        'effort': 2,
        'churn_risk': 0.6
    })
    print(f"Custom Score: {result['score']}")
```

### Formula Validation

```python
validation = engine.validate_formula("revenue / effort")

# Returns:
{
    'valid': True,
    'errors': [],
    'warnings': ['Formula divides by effort. Ensure effort is never 0.'],
    'used_variables': ['revenue', 'effort']
}
```

### Comparing Formulas

```python
from priority.custom_scoring import compare_formulas

test_cases = [
    {
        'name': 'High revenue, low effort',
        'request_count': 40,
        'revenue': 5_000_000,
        'effort': 1,
        'confidence': 0.8,
        'churn_risk': 0.3
    },
    {
        'name': 'Medium revenue, high churn',
        'request_count': 20,
        'revenue': 1_000_000,
        'effort': 2,
        'confidence': 0.6,
        'churn_risk': 0.8
    }
]

formulas = [
    engine.get_preset_formula('rice')['formula'],
    engine.get_preset_formula('wsjf')['formula'],
    engine.get_preset_formula('churn_prevention')['formula']
]

comparison = compare_formulas(formulas, test_cases)

# See which formula ranks items differently
```

---

## API Endpoints

### 1. Predict Impact
```http
POST /api/roadmap/predict-impact
Content-Type: application/json

{
    "request_count": 25,
    "impacted_revenue": 1500000,
    "avg_sentiment": -0.3,
    "effort": "medium",
    "feedback_volume_current": 200
}
```

**Response:**
```json
{
    "status": "success",
    "prediction": {
        "predicted_revenue_increase": 42500.0,
        "confidence_score": 0.65,
        "impact_range": {"min": 14875, "max": 70125},
        "prediction_method": "heuristic",
        "explanation": "...",
        "factors": [...]
    },
    "elapsed_time": 0.015
}
```

### 2. Custom Score
```http
POST /api/priority/custom-score
Content-Type: application/json

{
    "formula": "(request_count * revenue / 1000000) / effort",
    "variables": {
        "request_count": 30,
        "revenue": 2000000,
        "effort": 2
    }
}
```

### 3. At-Risk Customers
```http
GET /api/priority/at-risk-customers?revenue_threshold=100000&sentiment_threshold=-0.3&recent_days=30
```

**Response:**
```json
{
    "status": "success",
    "at_risk_customers": [
        {
            "customer_name": "Acme Corp",
            "customer_revenue": 2500000,
            "risk_score": 0.85,
            "total_feedback": 12,
            "recent_feedback": 6,
            "avg_sentiment": -0.6,
            "risk_factors": [...]
        }
    ],
    "total_count": 3
}
```

### 4. Priority Explanation
```http
GET /api/roadmap/42/explanation
```

### 5. List Preset Formulas
```http
GET /api/priority/formulas/presets
```

### 6. List Available Variables
```http
GET /api/priority/formulas/variables
```

### 7. Validate Formula
```http
POST /api/priority/formulas/validate?formula=revenue/effort
```

### 8. Compare Formulas
```http
POST /api/priority/formulas/compare
Content-Type: application/json

{
    "formulas": [
        "(revenue / 1000000) * confidence * (4 - effort)",
        "(request_count * revenue) / effort"
    ],
    "test_cases": [
        {"request_count": 40, "revenue": 5000000, "effort": 1, "confidence": 0.8}
    ]
}
```

---

## Best Practices

### 1. Use Advanced Factors for Enterprise
- Enable `enable_advanced_factors=True` for enterprise customers
- Provides more nuanced prioritization
- Requires more data input (LTV, churn risk, etc.)

### 2. Start with Heuristics, Add ML Later
- Impact prediction works immediately with heuristics
- Collect historical data after shipping features
- Train ML model when you have 10+ shipped features

### 3. Choose Right Formula for Your Team
- **Early startup**: Simple value vs. effort
- **Product-market fit**: RICE (reach-focused)
- **Enterprise SaaS**: Revenue-weighted or WSJF
- **High churn**: Churn prevention priority

### 4. Monitor At-Risk Customers
- Check `/api/priority/at-risk-customers` weekly
- Proactively reach out to high-risk customers
- Prioritize features they're requesting

### 5. Use Priority Explanations
- Share explanations with stakeholders
- Helps justify prioritization decisions
- Shows data-driven approach

---

## Competitive Advantage

### What Makes This Special

1. **Revenue-Weighted Prioritization**
   - Most tools only count votes
   - Compass weighs by actual customer revenue
   - Ensures high-value customers are prioritized

2. **ML-Based Impact Prediction**
   - Predicts actual revenue impact of features
   - Learns from your historical data
   - Provides confidence scores

3. **Churn Risk Integration**
   - Identifies at-risk customers automatically
   - Prioritizes features that prevent churn
   - Protects revenue proactively

4. **Custom Formulas**
   - Support for all popular frameworks
   - Create your own prioritization logic
   - No coding required (safe formula engine)

5. **Detailed Explanations**
   - Shows WHY a feature is high priority
   - Lists contributing factors
   - Makes decisions transparent

---

## Testing

Run tests for all modules:

```bash
# Test calculator
python backend/priority/calculator.py

# Test impact predictor
python backend/priority/impact_predictor.py

# Test custom scoring
python backend/priority/custom_scoring.py
```

---

## Future Enhancements

- [ ] A/B test formula effectiveness
- [ ] Auto-suggest best formula based on business model
- [ ] Integrate with CRM for real-time churn data
- [ ] Multi-objective optimization (revenue + NPS + retention)
- [ ] Feature dependency tracking
- [ ] ROI calculation post-launch
