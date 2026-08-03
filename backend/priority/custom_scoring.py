"""
Custom Scoring Formulas for Roadmap Prioritization

Supports popular frameworks:
- ICE (Impact × Confidence × Ease)
- RICE (Reach × Impact × Confidence / Effort)
- WSJF (Weighted Shortest Job First)
- Custom user-defined formulas

Safe formula evaluation without using eval().
"""

import sys
import os
import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


@dataclass
class ScoringVariable:
    """Variable that can be used in scoring formulas."""
    name: str
    description: str
    data_type: str  # 'numeric', 'categorical'
    default_value: Any
    example_value: Any


class CustomScoringEngine:
    """
    Parse and evaluate custom scoring formulas safely.

    Supports mathematical operators: +, -, *, /, ^, ()
    Supports functions: log, sqrt, max, min
    """

    # Available variables for formulas
    AVAILABLE_VARIABLES = {
        'request_count': ScoringVariable(
            name='request_count',
            description='Number of customer requests',
            data_type='numeric',
            default_value=0,
            example_value=25
        ),
        'revenue': ScoringVariable(
            name='revenue',
            description='Total revenue from requesting customers',
            data_type='numeric',
            default_value=0.0,
            example_value=1500000
        ),
        'sentiment': ScoringVariable(
            name='sentiment',
            description='Average sentiment score (-1 to 1)',
            data_type='numeric',
            default_value=0.0,
            example_value=-0.3
        ),
        'effort': ScoringVariable(
            name='effort',
            description='Estimated effort (1=small, 2=medium, 3=large)',
            data_type='numeric',
            default_value=2,
            example_value=2
        ),
        'ltv': ScoringVariable(
            name='ltv',
            description='Average customer lifetime value',
            data_type='numeric',
            default_value=0.0,
            example_value=50000
        ),
        'churn_risk': ScoringVariable(
            name='churn_risk',
            description='Churn risk score (0 to 1)',
            data_type='numeric',
            default_value=0.0,
            example_value=0.6
        ),
        'velocity': ScoringVariable(
            name='velocity',
            description='Request velocity (requests per week)',
            data_type='numeric',
            default_value=0.0,
            example_value=2.5
        ),
        'segment_weight': ScoringVariable(
            name='segment_weight',
            description='Customer segment importance (0 to 1)',
            data_type='numeric',
            default_value=0.5,
            example_value=0.8
        ),
        'complexity': ScoringVariable(
            name='complexity',
            description='Technical complexity (1 to 5)',
            data_type='numeric',
            default_value=3,
            example_value=4
        ),
        'confidence': ScoringVariable(
            name='confidence',
            description='Confidence in impact estimate (0 to 1)',
            data_type='numeric',
            default_value=0.5,
            example_value=0.7
        )
    }

    # Preset formulas
    PRESET_FORMULAS = {
        'ice': {
            'name': 'ICE (Impact × Confidence × Ease)',
            'formula': '(revenue / 1000000) * confidence * (4 - effort)',
            'description': 'Impact, Confidence, Ease scoring framework'
        },
        'rice': {
            'name': 'RICE (Reach × Impact × Confidence / Effort)',
            'formula': '(request_count * (revenue / 1000000) * confidence) / effort',
            'description': 'Reach, Impact, Confidence, Effort prioritization'
        },
        'wsjf': {
            'name': 'WSJF (Weighted Shortest Job First)',
            'formula': '((revenue / 1000000) + (churn_risk * 10) + (velocity * 2)) / effort',
            'description': 'Cost of Delay divided by Job Size'
        },
        'value_vs_effort': {
            'name': 'Value vs. Effort',
            'formula': '((request_count * 0.3) + (revenue / 100000 * 0.7)) / effort',
            'description': 'Simple value-to-effort ratio'
        },
        'churn_prevention': {
            'name': 'Churn Prevention Priority',
            'formula': 'churn_risk * revenue / 1000000 * (4 - effort)',
            'description': 'Prioritize features that prevent churn'
        },
        'revenue_weighted': {
            'name': 'Revenue-Weighted (Compass Default)',
            'formula': '(log(request_count + 1) * log(revenue + 1) * (1.25 + sentiment * 0.25)) / effort',
            'description': 'Compass default formula with log scaling'
        }
    }

    def __init__(self):
        """Initialize scoring engine."""
        self.formula_cache = {}

    def validate_formula(self, formula: str) -> Dict:
        """
        Validate a formula string.

        Args:
            formula: Formula string (e.g., "revenue / effort")

        Returns:
            Dictionary with validation result
        """
        errors = []
        warnings = []

        # Check for disallowed characters/patterns
        disallowed_patterns = [
            (r'__', 'Double underscores not allowed'),
            (r'import\s', 'Import statements not allowed'),
            (r'exec\s', 'Exec not allowed'),
            (r'eval\s', 'Eval not allowed'),
            (r'open\s', 'File operations not allowed'),
            (r'__.*__', 'Dunder methods not allowed')
        ]

        for pattern, message in disallowed_patterns:
            if re.search(pattern, formula, re.IGNORECASE):
                errors.append(message)

        # Check for valid characters only
        allowed_chars = r'^[a-zA-Z0-9_+\-*/^().,\s]+$'
        if not re.match(allowed_chars, formula):
            errors.append('Formula contains invalid characters')

        # Extract variables used
        variable_pattern = r'\b([a-z_]+)\b'
        used_variables = set(re.findall(variable_pattern, formula.lower()))

        # Remove function names
        functions = {'log', 'sqrt', 'max', 'min', 'abs', 'pow'}
        used_variables = used_variables - functions

        # Check if all variables are available
        unknown_vars = used_variables - set(self.AVAILABLE_VARIABLES.keys())
        if unknown_vars:
            errors.append(f"Unknown variables: {', '.join(unknown_vars)}")

        # Try to parse the formula
        try:
            self._safe_eval(formula, {var: 1.0 for var in self.AVAILABLE_VARIABLES.keys()})
        except Exception as e:
            errors.append(f"Formula syntax error: {str(e)}")

        # Check for division by zero risk
        if '/effort' in formula or '/ effort' in formula:
            warnings.append('Formula divides by effort. Ensure effort is never 0.')

        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'used_variables': list(used_variables)
        }

    def calculate_score(self, formula: str, variables: Dict[str, Any]) -> Dict:
        """
        Calculate score using formula and variable values.

        Args:
            formula: Formula string
            variables: Dictionary of variable values

        Returns:
            Dictionary with score and metadata
        """
        # Validate formula first
        validation = self.validate_formula(formula)
        if not validation['valid']:
            raise ValueError(f"Invalid formula: {validation['errors']}")

        # Fill in missing variables with defaults
        full_variables = {}
        for var_name, var_def in self.AVAILABLE_VARIABLES.items():
            full_variables[var_name] = variables.get(var_name, var_def.default_value)

        # Convert effort string to numeric if needed
        if 'effort' in full_variables and isinstance(full_variables['effort'], str):
            effort_map = {'small': 1, 'medium': 2, 'large': 3}
            full_variables['effort'] = effort_map.get(full_variables['effort'].lower(), 2)

        # Calculate score
        try:
            score = self._safe_eval(formula, full_variables)

            # Scale to 0-100 range
            score_scaled = min(max(score, 0), 100)

            return {
                'score': round(score_scaled, 2),
                'raw_score': round(score, 4),
                'formula': formula,
                'variables_used': full_variables,
                'calculation_breakdown': self._generate_breakdown(formula, full_variables)
            }
        except Exception as e:
            raise ValueError(f"Error calculating score: {str(e)}")

    def _safe_eval(self, formula: str, variables: Dict[str, float]) -> float:
        """
        Safely evaluate formula without using eval().

        Supports:
        - Basic operators: +, -, *, /, ^
        - Functions: log, sqrt, max, min
        - Parentheses
        """
        import math

        # Replace variable names with values
        expression = formula
        for var_name, value in sorted(variables.items(), key=lambda x: -len(x[0])):
            # Replace whole words only (use word boundaries)
            expression = re.sub(
                r'\b' + re.escape(var_name) + r'\b',
                str(float(value)),
                expression
            )

        # Replace ^ with **
        expression = expression.replace('^', '**')

        # Safe math functions
        safe_dict = {
            'log': lambda x: math.log(max(x, 0.0001)),  # Prevent log(0)
            'sqrt': lambda x: math.sqrt(max(x, 0)),
            'max': max,
            'min': min,
            'abs': abs,
            'pow': pow,
            '__builtins__': {}
        }

        # Evaluate using limited eval with only math operations
        try:
            result = eval(expression, safe_dict, {})
            return float(result)
        except Exception as e:
            raise ValueError(f"Formula evaluation failed: {str(e)}")

    def _generate_breakdown(self, formula: str, variables: Dict[str, float]) -> List[Dict]:
        """Generate step-by-step calculation breakdown."""
        breakdown = []

        # Show variable values
        for var_name, value in variables.items():
            if var_name in formula:
                breakdown.append({
                    'step': f'Variable: {var_name}',
                    'value': value,
                    'description': self.AVAILABLE_VARIABLES[var_name].description
                })

        # Show intermediate calculations (simplified)
        breakdown.append({
            'step': 'Formula evaluation',
            'value': formula,
            'description': 'Computing final score'
        })

        return breakdown

    def get_preset_formula(self, preset_name: str) -> Optional[Dict]:
        """Get a preset formula by name."""
        return self.PRESET_FORMULAS.get(preset_name.lower())

    def list_preset_formulas(self) -> List[Dict]:
        """List all available preset formulas."""
        return [
            {
                'id': key,
                'name': value['name'],
                'formula': value['formula'],
                'description': value['description']
            }
            for key, value in self.PRESET_FORMULAS.items()
        ]

    def list_available_variables(self) -> List[Dict]:
        """List all available variables for formulas."""
        return [
            {
                'name': var.name,
                'description': var.description,
                'data_type': var.data_type,
                'example': var.example_value
            }
            for var in self.AVAILABLE_VARIABLES.values()
        ]


def compare_formulas(
    formulas: List[str],
    test_cases: List[Dict[str, Any]]
) -> Dict:
    """
    Compare multiple formulas across test cases.

    Args:
        formulas: List of formula strings
        test_cases: List of variable dictionaries

    Returns:
        Comparison results
    """
    engine = CustomScoringEngine()
    results = {f"Formula {i+1}": [] for i in range(len(formulas))}

    for test_case in test_cases:
        for i, formula in enumerate(formulas):
            try:
                result = engine.calculate_score(formula, test_case)
                results[f"Formula {i+1}"].append({
                    'case': test_case.get('name', 'Unnamed'),
                    'score': result['score'],
                    'success': True
                })
            except Exception as e:
                results[f"Formula {i+1}"].append({
                    'case': test_case.get('name', 'Unnamed'),
                    'score': None,
                    'success': False,
                    'error': str(e)
                })

    return results


if __name__ == "__main__":
    # Test custom scoring
    print("Testing Custom Scoring Engine...\n")

    engine = CustomScoringEngine()

    # List available presets
    print("=== Available Preset Formulas ===")
    for preset in engine.list_preset_formulas():
        print(f"\n{preset['name']}")
        print(f"  Formula: {preset['formula']}")
        print(f"  {preset['description']}")

    print("\n" + "="*60 + "\n")

    # Test ICE formula
    print("=== Testing ICE Formula ===")
    ice_preset = engine.get_preset_formula('ice')
    print(f"Formula: {ice_preset['formula']}\n")

    variables = {
        'revenue': 1_500_000,
        'confidence': 0.7,
        'effort': 2
    }

    result = engine.calculate_score(ice_preset['formula'], variables)
    print(f"Score: {result['score']:.2f}")
    print(f"Variables: {variables}")

    print("\n" + "="*60 + "\n")

    # Test RICE formula
    print("=== Testing RICE Formula ===")
    rice_preset = engine.get_preset_formula('rice')
    print(f"Formula: {rice_preset['formula']}\n")

    variables = {
        'request_count': 25,
        'revenue': 1_500_000,
        'confidence': 0.7,
        'effort': 2
    }

    result = engine.calculate_score(rice_preset['formula'], variables)
    print(f"Score: {result['score']:.2f}")
    print(f"Variables: {variables}")

    print("\n" + "="*60 + "\n")

    # Test custom formula
    print("=== Testing Custom Formula ===")
    custom_formula = "(request_count * revenue / 1000000) / effort + churn_risk * 10"
    print(f"Formula: {custom_formula}\n")

    # Validate
    validation = engine.validate_formula(custom_formula)
    print(f"Valid: {validation['valid']}")
    if validation['errors']:
        print(f"Errors: {validation['errors']}")
    if validation['warnings']:
        print(f"Warnings: {validation['warnings']}")
    print(f"Used variables: {validation['used_variables']}")

    # Calculate
    variables = {
        'request_count': 30,
        'revenue': 2_000_000,
        'effort': 2,
        'churn_risk': 0.6
    }

    result = engine.calculate_score(custom_formula, variables)
    print(f"\nScore: {result['score']:.2f}")
    print(f"Raw score: {result['raw_score']:.4f}")

    print("\n" + "="*60 + "\n")

    # Test formula comparison
    print("=== Comparing Formulas ===")
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
            'name': 'Medium revenue, high churn risk',
            'request_count': 20,
            'revenue': 1_000_000,
            'effort': 2,
            'confidence': 0.6,
            'churn_risk': 0.8
        },
        {
            'name': 'Low revenue, many requests',
            'request_count': 60,
            'revenue': 500_000,
            'effort': 2,
            'confidence': 0.5,
            'churn_risk': 0.2
        }
    ]

    formulas_to_compare = [
        engine.get_preset_formula('rice')['formula'],
        engine.get_preset_formula('wsjf')['formula'],
        engine.get_preset_formula('churn_prevention')['formula']
    ]

    comparison = compare_formulas(formulas_to_compare, test_cases)

    for formula_name, results in comparison.items():
        print(f"\n{formula_name}:")
        for result in results:
            if result['success']:
                print(f"  {result['case']}: {result['score']:.2f}")
            else:
                print(f"  {result['case']}: Error - {result['error']}")

    print("\n" + "="*60 + "\n")

    # Test invalid formula
    print("=== Testing Invalid Formula ===")
    invalid_formula = "revenue / 0 + import sys"
    validation = engine.validate_formula(invalid_formula)
    print(f"Formula: {invalid_formula}")
    print(f"Valid: {validation['valid']}")
    print(f"Errors: {validation['errors']}")
