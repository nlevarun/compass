# API Usage Examples

Complete examples for using the advanced prioritization API endpoints.

## Base URL
```
http://localhost:8000
```

---

## 1. Predict Revenue Impact

Predict how much MRR will increase if you build a feature.

### Request
```bash
curl -X POST http://localhost:8000/api/roadmap/predict-impact \
  -H "Content-Type: application/json" \
  -d '{
    "request_count": 25,
    "impacted_revenue": 1500000,
    "avg_sentiment": -0.3,
    "effort": "medium",
    "feedback_volume_current": 200
  }'
```

### Response
```json
{
  "status": "success",
  "prediction": {
    "predicted_revenue_increase": 37375.0,
    "confidence_score": 0.65,
    "impact_range": {
      "min": 24294,
      "max": 50456
    },
    "prediction_method": "heuristic",
    "explanation": "Building this feature is expected to increase MRR by $37,375. Moderate request volume (25 requests) shows interest. Significant revenue at stake ($1,500,000). Negative sentiment suggests this is a pain point - addressing it may prevent churn. Prediction based on heuristics. Add historical data to improve accuracy.",
    "factors": [
      {
        "name": "Request Volume",
        "value": 25,
        "weight": "high",
        "impact": "positive"
      },
      {
        "name": "Impacted Revenue",
        "value": "$1,500,000",
        "weight": "high",
        "impact": "positive"
      },
      {
        "name": "Customer Sentiment",
        "value": "-0.30",
        "weight": "medium",
        "impact": "urgent"
      },
      {
        "name": "Development Effort",
        "value": "medium",
        "weight": "medium",
        "impact": "neutral"
      }
    ]
  },
  "elapsed_time": 0.015
}
```

### Use Case
- **Before sprint planning**: Estimate ROI of each feature
- **Quarterly planning**: Predict total MRR impact of roadmap
- **Stakeholder reports**: Show data-driven impact projections

---

## 2. Custom Scoring Formula

Calculate priority using ICE, RICE, WSJF, or custom formulas.

### Example 1: RICE Formula
```bash
curl -X POST http://localhost:8000/api/priority/custom-score \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "(request_count * (revenue / 1000000) * confidence) / effort",
    "variables": {
      "request_count": 25,
      "revenue": 1500000,
      "confidence": 0.7,
      "effort": 2
    }
  }'
```

### Response
```json
{
  "status": "success",
  "result": {
    "score": 13.12,
    "raw_score": 13.125,
    "formula": "(request_count * (revenue / 1000000) * confidence) / effort",
    "variables_used": {
      "request_count": 25,
      "revenue": 1500000,
      "confidence": 0.7,
      "effort": 2
    },
    "calculation_breakdown": [
      {
        "step": "Variable: request_count",
        "value": 25,
        "description": "Number of customer requests"
      },
      {
        "step": "Variable: revenue",
        "value": 1500000,
        "description": "Total revenue from requesting customers"
      },
      {
        "step": "Formula evaluation",
        "value": "(request_count * (revenue / 1000000) * confidence) / effort",
        "description": "Computing final score"
      }
    ]
  },
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": [
      "Formula divides by effort. Ensure effort is never 0."
    ],
    "used_variables": [
      "request_count",
      "revenue",
      "confidence",
      "effort"
    ]
  },
  "elapsed_time": 0.003
}
```

### Example 2: Churn Prevention Formula
```bash
curl -X POST http://localhost:8000/api/priority/custom-score \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "churn_risk * revenue / 1000000 * (4 - effort)",
    "variables": {
      "churn_risk": 0.8,
      "revenue": 2000000,
      "effort": 2
    }
  }'
```

### Example 3: Custom Weighted Formula
```bash
curl -X POST http://localhost:8000/api/priority/custom-score \
  -H "Content-Type: application/json" \
  -d '{
    "formula": "(revenue / 1000000 * 0.5) + (request_count * 0.3) + (churn_risk * 10 * 0.2)",
    "variables": {
      "revenue": 3000000,
      "request_count": 30,
      "churn_risk": 0.6
    }
  }'
```

### Use Case
- **Team prefers ICE/RICE**: Use preset formulas
- **Custom prioritization logic**: Define your own formula
- **A/B testing**: Compare different formulas to see which performs best

---

## 3. Identify At-Risk Customers

Find high-value customers likely to churn based on feedback patterns.

### Request
```bash
curl http://localhost:8000/api/priority/at-risk-customers?revenue_threshold=100000&sentiment_threshold=-0.3&recent_days=30
```

### Response
```json
{
  "status": "success",
  "at_risk_customers": [
    {
      "customer_name": "Acme Corporation",
      "customer_revenue": 2500000,
      "risk_score": 0.85,
      "total_feedback": 12,
      "recent_feedback": 6,
      "avg_sentiment": -0.6,
      "risk_factors": [
        "High-value customer ($2,500,000 revenue)",
        "Very negative sentiment (-0.60)",
        "Recent feedback spike (6 in last 30 days)"
      ]
    },
    {
      "customer_name": "TechCorp Inc",
      "customer_revenue": 1200000,
      "risk_score": 0.75,
      "total_feedback": 8,
      "recent_feedback": 4,
      "avg_sentiment": -0.5,
      "risk_factors": [
        "High-value customer ($1,200,000 revenue)",
        "Very negative sentiment (-0.50)",
        "Frequent complaints (8 total)"
      ]
    }
  ],
  "total_count": 2,
  "parameters": {
    "revenue_threshold": 100000,
    "sentiment_threshold": -0.3,
    "recent_days": 30
  },
  "elapsed_time": 0.12
}
```

### Use Case
- **Weekly review**: Check for new at-risk customers
- **Customer success**: Proactive outreach to at-risk accounts
- **Prioritization**: Urgent features from at-risk high-value customers

---

## 4. Priority Explanation

Get detailed explanation of why a roadmap item has its priority score.

### Request
```bash
curl http://localhost:8000/api/roadmap/1/explanation
```

### Response
```json
{
  "status": "success",
  "roadmap_item": {
    "id": 1,
    "title": "Mobile App Performance Improvements",
    "rank": 1,
    "priority_score": 85.3
  },
  "explanation": {
    "priority_score": 85.3,
    "priority_level": "HIGH",
    "summary": "This feature has HIGH priority (score: 85.3). Critical factors: Churn Prevention, Critical Revenue Impact. Urgent due to: Pain Point, Churn Prevention.",
    "contributing_factors": [
      {
        "factor": "High Demand",
        "value": "45 requests",
        "impact": "positive",
        "weight": "high",
        "description": "Many customers are asking for this feature"
      },
      {
        "factor": "Critical Revenue Impact",
        "value": "$8,500,000",
        "impact": "positive",
        "weight": "critical",
        "description": "High-value customers are requesting this"
      },
      {
        "factor": "Pain Point",
        "value": "-0.40 sentiment",
        "impact": "urgent",
        "weight": "high",
        "description": "Negative sentiment suggests customers are frustrated"
      },
      {
        "factor": "Churn Prevention",
        "value": "70.0% risk",
        "impact": "urgent",
        "weight": "critical",
        "description": "At-risk customers need this to stay"
      }
    ],
    "confidence": "high"
  }
}
```

### Use Case
- **Stakeholder presentations**: Justify priority decisions
- **Team alignment**: Ensure everyone understands priorities
- **Transparency**: Show data-driven approach to customers

---

## 5. List Preset Formulas

Get all available prioritization formulas.

### Request
```bash
curl http://localhost:8000/api/priority/formulas/presets
```

### Response
```json
{
  "status": "success",
  "presets": [
    {
      "id": "ice",
      "name": "ICE (Impact × Confidence × Ease)",
      "formula": "(revenue / 1000000) * confidence * (4 - effort)",
      "description": "Impact, Confidence, Ease scoring framework"
    },
    {
      "id": "rice",
      "name": "RICE (Reach × Impact × Confidence / Effort)",
      "formula": "(request_count * (revenue / 1000000) * confidence) / effort",
      "description": "Reach, Impact, Confidence, Effort prioritization"
    },
    {
      "id": "wsjf",
      "name": "WSJF (Weighted Shortest Job First)",
      "formula": "((revenue / 1000000) + (churn_risk * 10) + (velocity * 2)) / effort",
      "description": "Cost of Delay divided by Job Size"
    },
    {
      "id": "value_vs_effort",
      "name": "Value vs. Effort",
      "formula": "((request_count * 0.3) + (revenue / 100000 * 0.7)) / effort",
      "description": "Simple value-to-effort ratio"
    },
    {
      "id": "churn_prevention",
      "name": "Churn Prevention Priority",
      "formula": "churn_risk * revenue / 1000000 * (4 - effort)",
      "description": "Prioritize features that prevent churn"
    },
    {
      "id": "revenue_weighted",
      "name": "Revenue-Weighted (Compass Default)",
      "formula": "(log(request_count + 1) * log(revenue + 1) * (1.25 + sentiment * 0.25)) / effort",
      "description": "Compass default formula with log scaling"
    }
  ],
  "count": 6
}
```

### Use Case
- **Onboarding**: Help teams choose a formula
- **Documentation**: Show available options
- **Experimentation**: Try different frameworks

---

## 6. List Formula Variables

Get all variables available for use in formulas.

### Request
```bash
curl http://localhost:8000/api/priority/formulas/variables
```

### Response
```json
{
  "status": "success",
  "variables": [
    {
      "name": "request_count",
      "description": "Number of customer requests",
      "data_type": "numeric",
      "example": 25
    },
    {
      "name": "revenue",
      "description": "Total revenue from requesting customers",
      "data_type": "numeric",
      "example": 1500000
    },
    {
      "name": "sentiment",
      "description": "Average sentiment score (-1 to 1)",
      "data_type": "numeric",
      "example": -0.3
    },
    {
      "name": "effort",
      "description": "Estimated effort (1=small, 2=medium, 3=large)",
      "data_type": "numeric",
      "example": 2
    },
    {
      "name": "ltv",
      "description": "Average customer lifetime value",
      "data_type": "numeric",
      "example": 50000
    },
    {
      "name": "churn_risk",
      "description": "Churn risk score (0 to 1)",
      "data_type": "numeric",
      "example": 0.6
    },
    {
      "name": "velocity",
      "description": "Request velocity (requests per week)",
      "data_type": "numeric",
      "example": 2.5
    },
    {
      "name": "segment_weight",
      "description": "Customer segment importance (0 to 1)",
      "data_type": "numeric",
      "example": 0.8
    },
    {
      "name": "complexity",
      "description": "Technical complexity (1 to 5)",
      "data_type": "numeric",
      "example": 4
    },
    {
      "name": "confidence",
      "description": "Confidence in impact estimate (0 to 1)",
      "data_type": "numeric",
      "example": 0.7
    }
  ],
  "count": 10
}
```

### Use Case
- **Formula building**: Know what variables you can use
- **Documentation**: Understand data types
- **Validation**: Check variable names before using

---

## 7. Validate Formula

Validate a custom formula before using it.

### Request
```bash
curl -X POST "http://localhost:8000/api/priority/formulas/validate?formula=revenue%20%2F%20effort"
```

### Response (Valid)
```json
{
  "status": "success",
  "validation": {
    "valid": true,
    "errors": [],
    "warnings": [
      "Formula divides by effort. Ensure effort is never 0."
    ],
    "used_variables": [
      "revenue",
      "effort"
    ]
  }
}
```

### Response (Invalid)
```bash
curl -X POST "http://localhost:8000/api/priority/formulas/validate?formula=revenue%20%2F%20unknown_var"
```

```json
{
  "status": "success",
  "validation": {
    "valid": false,
    "errors": [
      "Unknown variables: unknown_var"
    ],
    "warnings": [],
    "used_variables": [
      "revenue",
      "unknown_var"
    ]
  }
}
```

### Use Case
- **Before saving**: Validate user-entered formulas
- **API integration**: Check formula syntax
- **Error prevention**: Catch issues before execution

---

## 8. Compare Formulas

Compare multiple formulas across test cases to see which ranks features best for your business.

### Request
```bash
curl -X POST http://localhost:8000/api/priority/formulas/compare \
  -H "Content-Type: application/json" \
  -d '{
    "formulas": [
      "(request_count * (revenue / 1000000) * confidence) / effort",
      "((revenue / 1000000) + (churn_risk * 10) + (velocity * 2)) / effort",
      "churn_risk * revenue / 1000000 * (4 - effort)"
    ],
    "test_cases": [
      {
        "name": "High revenue, low effort",
        "request_count": 40,
        "revenue": 5000000,
        "effort": 1,
        "confidence": 0.8,
        "churn_risk": 0.3,
        "velocity": 1.5
      },
      {
        "name": "Medium revenue, high churn risk",
        "request_count": 20,
        "revenue": 1000000,
        "effort": 2,
        "confidence": 0.6,
        "churn_risk": 0.8,
        "velocity": 2.0
      },
      {
        "name": "Low revenue, many requests",
        "request_count": 60,
        "revenue": 500000,
        "effort": 2,
        "confidence": 0.5,
        "churn_risk": 0.2,
        "velocity": 3.0
      }
    ]
  }'
```

### Response
```json
{
  "status": "success",
  "comparison": {
    "Formula 1": [
      {
        "case": "High revenue, low effort",
        "score": 100.0,
        "success": true
      },
      {
        "case": "Medium revenue, high churn risk",
        "score": 6.0,
        "success": true
      },
      {
        "case": "Low revenue, many requests",
        "score": 7.5,
        "success": true
      }
    ],
    "Formula 2": [
      {
        "case": "High revenue, low effort",
        "score": 8.0,
        "success": true
      },
      {
        "case": "Medium revenue, high churn risk",
        "score": 4.5,
        "success": true
      },
      {
        "case": "Low revenue, many requests",
        "score": 1.25,
        "success": true
      }
    ],
    "Formula 3": [
      {
        "case": "High revenue, low effort",
        "score": 4.5,
        "success": true
      },
      {
        "case": "Medium revenue, high churn risk",
        "score": 1.6,
        "success": true
      },
      {
        "case": "Low revenue, many requests",
        "score": 0.2,
        "success": true
      }
    ]
  },
  "formulas_count": 3,
  "test_cases_count": 3,
  "elapsed_time": 0.008
}
```

### Use Case
- **A/B testing**: See which formula performs best
- **Team decision**: Choose between ICE, RICE, WSJF
- **Optimization**: Find best formula for your business model

---

## Common Patterns

### Pattern 1: Complete Feature Evaluation
```bash
# Step 1: Predict impact
curl -X POST http://localhost:8000/api/roadmap/predict-impact -d '{...}'

# Step 2: Calculate priority with custom formula
curl -X POST http://localhost:8000/api/priority/custom-score -d '{...}'

# Step 3: Get explanation
curl http://localhost:8000/api/roadmap/1/explanation
```

### Pattern 2: Weekly At-Risk Review
```bash
# Every Monday: Check at-risk customers
curl http://localhost:8000/api/priority/at-risk-customers?revenue_threshold=50000

# Review their requested features
# Prioritize urgent items
```

### Pattern 3: Formula Experimentation
```bash
# Step 1: List presets
curl http://localhost:8000/api/priority/formulas/presets

# Step 2: Compare 3 formulas
curl -X POST http://localhost:8000/api/priority/formulas/compare -d '{...}'

# Step 3: Choose winner and use it
curl -X POST http://localhost:8000/api/priority/custom-score -d '{...}'
```

---

## Error Handling

### Invalid Formula
```json
{
  "detail": "Invalid formula: Import statements not allowed"
}
```

### Missing Variables
```json
{
  "detail": "Invalid formula: Unknown variables: invalid_var"
}
```

### Not Found
```json
{
  "detail": "Roadmap item not found"
}
```

---

## Rate Limits

Currently no rate limits. In production, recommend:
- 100 requests/minute per API key
- 1000 requests/day per API key

---

## Authentication

Currently no authentication required. In production, add:
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  http://localhost:8000/api/roadmap/predict-impact
```

---

## Best Practices

1. **Validate formulas** before using them in production
2. **Compare formulas** with your actual data to find best fit
3. **Check at-risk customers** weekly
4. **Get explanations** for transparency with stakeholders
5. **Track prediction accuracy** to improve ML model

---

## Need Help?

- Full docs: `/backend/priority/README.md`
- Quick start: `/backend/priority/QUICK_START.md`
- API playground: `http://localhost:8000/docs` (FastAPI auto-docs)
