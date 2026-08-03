# Quick Start Guide: Advanced Prioritization

## 🚀 Getting Started

### 1. Basic Priority Calculation

```python
from priority.calculator import PriorityCalculator

calculator = PriorityCalculator()

score = calculator.calculate_priority_score(
    request_count=25,
    total_revenue=1_500_000,
    avg_sentiment=-0.3,
    estimated_effort='medium',
    max_count=100
)

print(f"Priority: {score}")  # e.g., 45.2
```

### 2. Advanced Priority with All Factors

```python
calculator = PriorityCalculator(enable_advanced_factors=True)

score = calculator.calculate_priority_score(
    request_count=25,
    total_revenue=1_500_000,
    avg_sentiment=-0.3,
    estimated_effort='medium',
    max_count=100,
    # Advanced factors
    avg_customer_ltv=150_000,
    churn_risk_score=0.7,
    recent_request_count=15,
    historical_request_count=10,
    segment_importance='critical',
    competitor_mentions=3,
    technical_complexity=4
)

print(f"Advanced Priority: {score}")  # e.g., 78.5
```

### 3. Predict Revenue Impact

```python
from priority.impact_predictor import ImpactPredictor

predictor = ImpactPredictor()

prediction = predictor.predict_impact(
    request_count=25,
    impacted_revenue=1_500_000,
    avg_sentiment=-0.3,
    effort='medium'
)

print(f"Expected MRR increase: ${prediction['predicted_revenue_increase']:,.0f}")
print(f"Confidence: {prediction['confidence_score']:.0%}")
print(f"Explanation: {prediction['explanation']}")
```

### 4. Custom Scoring Formula

```python
from priority.custom_scoring import CustomScoringEngine

engine = CustomScoringEngine()

# Use RICE framework
rice = engine.get_preset_formula('rice')
result = engine.calculate_score(
    formula=rice['formula'],
    variables={
        'request_count': 25,
        'revenue': 1_500_000,
        'confidence': 0.7,
        'effort': 2
    }
)

print(f"RICE Score: {result['score']}")
```

### 5. Identify At-Risk Customers

```python
from priority.calculator import identify_at_risk_customers

at_risk = identify_at_risk_customers(
    feedback_items=all_feedback,  # List of feedback dicts
    revenue_threshold=100_000,
    sentiment_threshold=-0.3
)

for customer in at_risk:
    print(f"{customer['customer_name']}: Risk {customer['risk_score']:.0%}")
    print(f"  Revenue: ${customer['customer_revenue']:,}")
    print(f"  Sentiment: {customer['avg_sentiment']:+.2f}")
```

---

## 🌐 API Usage

### Predict Impact
```bash
curl -X POST http://localhost:8000/api/roadmap/predict-impact \
  -H "Content-Type: application/json" \
  -d '{
    "request_count": 25,
    "impacted_revenue": 1500000,
    "avg_sentiment": -0.3,
    "effort": "medium"
  }'
```

### Custom Score
```bash
curl -X POST http://localhost:8000/api/priority/custom-score \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "(request_count * revenue / 1000000) / effort",
    "variables": {
      "request_count": 30,
      "revenue": 2000000,
      "effort": 2
    }
  }'
```

### At-Risk Customers
```bash
curl http://localhost:8000/api/priority/at-risk-customers?revenue_threshold=100000
```

### Priority Explanation
```bash
curl http://localhost:8000/api/roadmap/1/explanation
```

### List Preset Formulas
```bash
curl http://localhost:8000/api/priority/formulas/presets
```

---

## 📊 Common Formulas

### ICE (Impact × Confidence × Ease)
```
(revenue / 1000000) * confidence * (4 - effort)
```
**Best for**: Early-stage products, quick wins

### RICE (Reach × Impact × Confidence / Effort)
```
(request_count * (revenue / 1000000) * confidence) / effort
```
**Best for**: Growth stage, maximizing reach

### WSJF (Weighted Shortest Job First)
```
((revenue / 1000000) + (churn_risk * 10) + (velocity * 2)) / effort
```
**Best for**: Enterprise SaaS, preventing churn

### Churn Prevention
```
churn_risk * revenue / 1000000 * (4 - effort)
```
**Best for**: High churn businesses, retention focus

### Revenue-Weighted (Compass Default)
```
(log(request_count + 1) * log(revenue + 1) * (1.25 + sentiment * 0.25)) / effort
```
**Best for**: Balanced approach, reduces outlier bias

---

## 🎯 Decision Tree: Which Formula?

```
Are you dealing with high churn?
├─ YES → Use "Churn Prevention" or "WSJF"
└─ NO
   └─ Do you have clear confidence estimates?
      ├─ YES → Use "RICE" or "ICE"
      └─ NO → Use "Revenue-Weighted" (default)
```

---

## 🔧 Tips & Tricks

### 1. Adjust for Your Scale
If your revenue is in millions, use:
```
revenue / 1000000
```

If in thousands:
```
revenue / 1000
```

### 2. Weight Multiple Factors
```python
# Custom formula: 40% revenue, 30% requests, 30% churn
formula = "(revenue / 1000000 * 0.4) + (request_count * 0.3) + (churn_risk * 10 * 0.3)"
```

### 3. Quick Wins Bias
```python
# Heavily favor small effort
formula = "revenue / (effort ^ 2)"  # Small effort gets 4x boost
```

### 4. Customer Count vs Revenue
```python
# If you value customer count more than revenue
formula = "(request_count * 0.7) + (revenue / 100000 * 0.3)"
```

---

## 🚨 Common Mistakes

### ❌ DON'T: Divide by request_count or revenue
```python
# Bad: Division by zero risk
formula = "revenue / request_count"
```

### ✅ DO: Add 1 to prevent division by zero
```python
# Good: Safe from zero
formula = "revenue / (request_count + 1)"
```

### ❌ DON'T: Ignore effort
```python
# Bad: No effort consideration
formula = "revenue * request_count"
```

### ✅ DO: Always factor in effort
```python
# Good: Balanced with effort
formula = "(revenue * request_count) / effort"
```

---

## 📈 Training ML Model

### Step 1: Collect Historical Data
After shipping features, record:
- Feature title
- Feedback volume before/after launch
- Request count
- Revenue from requesters
- Actual MRR increase

### Step 2: Add to Predictor
```python
predictor = ImpactPredictor()

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
```

### Step 3: Train (after 10+ features)
```python
if predictor.train_model():
    print("ML model trained!")
    predictor.save_model('model.pkl')
```

### Step 4: Use ML Predictions
```python
# Automatically uses ML if available
prediction = predictor.predict_impact(...)
print(f"Method: {prediction['prediction_method']}")  # 'machine_learning'
```

---

## 🎓 Example Scenarios

### Scenario 1: Early Startup (Limited Data)
```python
# Use simple value vs effort
formula = "(request_count + (revenue / 100000)) / effort"
```

### Scenario 2: Enterprise SaaS (Revenue Focus)
```python
# Use revenue-weighted with LTV
calculator = PriorityCalculator(enable_advanced_factors=True)
# Provide LTV and churn risk data
```

### Scenario 3: High Churn Rate
```python
# Monitor at-risk customers daily
at_risk = identify_at_risk_customers(feedback, revenue_threshold=50_000)

# Use churn prevention formula
formula = "churn_risk * revenue / 1000000 * (4 - effort)"
```

### Scenario 4: Product-Market Fit Stage
```python
# Focus on reach and impact
formula = engine.get_preset_formula('rice')['formula']
```

---

## 🔍 Debugging

### Check Formula Validity
```python
validation = engine.validate_formula("your_formula")
print(validation['errors'])
print(validation['warnings'])
print(validation['used_variables'])
```

### Test with Sample Data
```python
result = engine.calculate_score(
    formula="your_formula",
    variables={'request_count': 10, 'revenue': 100000, 'effort': 2}
)
print(result['calculation_breakdown'])
```

### Compare Results
```python
formulas = ['formula1', 'formula2', 'formula3']
test_cases = [{'request_count': 10, 'revenue': 100000, ...}]
comparison = compare_formulas(formulas, test_cases)
```

---

## 📚 Further Reading

- Full documentation: `backend/priority/README.md`
- API reference: OpenAPI docs at `/docs`
- Examples: Each module has test code at bottom of file

---

## 🆘 Need Help?

1. Check formula validation errors
2. Verify variable names match available list
3. Ensure effort is never 0
4. Use log() for large numbers (revenue, request_count)
5. Start with preset formulas, then customize

---

## 🎉 Success Metrics

Track these to measure effectiveness:

1. **Prediction Accuracy**: Compare predicted vs actual MRR increase
2. **Churn Prevention**: At-risk customers retained after addressing their features
3. **Revenue Impact**: MRR growth from prioritized features
4. **Formula Effectiveness**: Which formula produces best outcomes for your business

---

**Pro Tip**: Start simple with default formula. Add complexity as you collect more data and understand your patterns better.
