import { useState, useEffect } from 'react';
import {
  getAtRiskCustomers,
  getRoadmapExplanation,
  predictImpact,
  calculateCustomScore,
  getFormulaPresets,
  compareFormulas
} from '../services/api';

function PriorityAnalysis() {
  const [activeTab, setActiveTab] = useState('weights');
  const [atRiskCustomers, setAtRiskCustomers] = useState([]);
  const [loading, setLoading] = useState(false);

  // Priority Weights State
  const [weights, setWeights] = useState({
    revenue: 1.0,
    ltv: 1.0,
    frequency: 1.0,
    urgency: 1.0,
    complexity: 100
  });

  // Impact Prediction State
  const [impactForm, setImpactForm] = useState({
    request_count: 10,
    impacted_revenue: 500000,
    avg_sentiment: 0.5,
    effort: 'medium',
    feedback_volume_current: 50
  });
  const [impactResult, setImpactResult] = useState(null);

  // Custom Formula State
  const [customFormula, setCustomFormula] = useState('(impact * reach) / effort');
  const [formulaVariables, setFormulaVariables] = useState({
    impact: 50,
    reach: 100,
    effort: 20
  });
  const [formulaResult, setFormulaResult] = useState(null);
  const [formulaPresets, setFormulaPresets] = useState([]);

  useEffect(() => {
    loadAtRiskCustomers();
    loadFormulaPresets();
  }, []);

  const loadAtRiskCustomers = async () => {
    try {
      const response = await getAtRiskCustomers();
      setAtRiskCustomers(response.data.at_risk_customers || []);
    } catch (error) {
      console.error('Failed to load at-risk customers:', error);
    }
  };

  const loadFormulaPresets = async () => {
    try {
      const response = await getFormulaPresets();
      setFormulaPresets(response.data.presets || []);
    } catch (error) {
      console.error('Failed to load formula presets:', error);
    }
  };

  const calculatePriorityScore = () => {
    const { revenue, ltv, frequency, urgency, complexity } = weights;
    return ((revenue * ltv * frequency * urgency) / complexity).toFixed(2);
  };

  const handleWeightChange = (field, value) => {
    setWeights({ ...weights, [field]: parseFloat(value) });
  };

  const handlePredictImpact = async () => {
    setLoading(true);
    try {
      const response = await predictImpact(impactForm);
      setImpactResult(response.data.prediction);
    } catch (error) {
      console.error('Failed to predict impact:', error);
      alert('Failed to predict impact. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  };

  const handleCalculateCustomScore = async () => {
    setLoading(true);
    try {
      const response = await calculateCustomScore({
        formula: customFormula,
        variables: formulaVariables
      });
      setFormulaResult(response.data.result);
    } catch (error) {
      console.error('Failed to calculate score:', error);
      alert('Invalid formula or variables. Please check your inputs.');
    } finally {
      setLoading(false);
    }
  };

  const applyPresetFormula = (preset) => {
    setCustomFormula(preset.formula);
    setFormulaVariables(preset.default_variables || {});
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Priority Analysis</h2>
        <p className="text-gray-600 mt-1">
          Advanced prioritization tools and insights
        </p>
      </div>

      {/* At-Risk Customers Alert */}
      {atRiskCustomers.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <div className="flex items-start">
            <div className="flex-shrink-0">
              <svg className="w-5 h-5 text-red-600" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-medium text-red-800">
                {atRiskCustomers.length} At-Risk Customer{atRiskCustomers.length !== 1 ? 's' : ''}
              </h3>
              <p className="text-sm text-red-700 mt-1">
                High-value customers showing negative sentiment. Consider prioritizing their requests.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8">
          {[
            { id: 'weights', label: 'Priority Weights', icon: '⚖️' },
            { id: 'impact', label: 'Impact Prediction', icon: '📊' },
            { id: 'formula', label: 'Custom Formula', icon: '🧮' },
            { id: 'customers', label: 'At-Risk Customers', icon: '⚠️' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                py-2 px-1 border-b-2 font-medium text-sm whitespace-nowrap
                ${activeTab === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              <span className="mr-2">{tab.icon}</span>
              {tab.label}
            </button>
          ))}
        </nav>
      </div>

      {/* Tab Content */}
      <div className="mt-6">
        {activeTab === 'weights' && (
          <PriorityWeightsPanel
            weights={weights}
            onWeightChange={handleWeightChange}
            priorityScore={calculatePriorityScore()}
          />
        )}

        {activeTab === 'impact' && (
          <ImpactPredictionPanel
            form={impactForm}
            onFormChange={setImpactForm}
            result={impactResult}
            loading={loading}
            onPredict={handlePredictImpact}
          />
        )}

        {activeTab === 'formula' && (
          <CustomFormulaPanel
            formula={customFormula}
            variables={formulaVariables}
            presets={formulaPresets}
            result={formulaResult}
            loading={loading}
            onFormulaChange={setCustomFormula}
            onVariablesChange={setFormulaVariables}
            onCalculate={handleCalculateCustomScore}
            onApplyPreset={applyPresetFormula}
          />
        )}

        {activeTab === 'customers' && (
          <AtRiskCustomersPanel customers={atRiskCustomers} />
        )}
      </div>
    </div>
  );
}

// Priority Weights Panel
function PriorityWeightsPanel({ weights, onWeightChange, priorityScore }) {
  return (
    <div className="bg-white rounded-lg shadow p-6 space-y-6">
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Priority Formula</h3>
        <div className="bg-gray-50 p-4 rounded-lg font-mono text-sm">
          Priority = (Revenue × LTV × Frequency × Urgency) / (Complexity × 100)
        </div>
      </div>

      <div className="space-y-6">
        {Object.entries(weights).map(([key, value]) => (
          <div key={key}>
            <div className="flex justify-between mb-2">
              <label className="text-sm font-medium text-gray-700 capitalize">
                {key}
              </label>
              <span className="text-sm font-semibold text-primary-600">
                {value.toFixed(2)}
              </span>
            </div>
            <input
              type="range"
              min={key === 'complexity' ? 1 : 0}
              max={key === 'complexity' ? 200 : 2}
              step="0.1"
              value={value}
              onChange={(e) => onWeightChange(key, e.target.value)}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>{key === 'complexity' ? 'Low' : 'Low Impact'}</span>
              <span>{key === 'complexity' ? 'High' : 'High Impact'}</span>
            </div>
          </div>
        ))}
      </div>

      <div className="border-t pt-6">
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
          <h4 className="text-sm font-medium text-primary-900 mb-2">Calculated Priority Score</h4>
          <div className="flex items-baseline">
            <span className="text-4xl font-bold text-primary-600">{priorityScore}</span>
            <span className="ml-2 text-sm text-primary-700">
              {priorityScore >= 60 ? '(High Priority)' : priorityScore >= 30 ? '(Medium Priority)' : '(Low Priority)'}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-900 mb-2">How to Use</h4>
        <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
          <li>Adjust sliders to see how different factors affect priority</li>
          <li>Higher values increase priority (except complexity)</li>
          <li>Use this to understand trade-offs in prioritization</li>
          <li>Compare with system-calculated priorities in the roadmap</li>
        </ul>
      </div>
    </div>
  );
}

// Impact Prediction Panel
function ImpactPredictionPanel({ form, onFormChange, result, loading, onPredict }) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Input Form */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Feature Details</h3>

        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Request Count
            </label>
            <input
              type="number"
              value={form.request_count}
              onChange={(e) => onFormChange({ ...form, request_count: parseInt(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Impacted Revenue ($)
            </label>
            <input
              type="number"
              value={form.impacted_revenue}
              onChange={(e) => onFormChange({ ...form, impacted_revenue: parseFloat(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Average Sentiment (-1 to 1)
            </label>
            <input
              type="number"
              min="-1"
              max="1"
              step="0.1"
              value={form.avg_sentiment}
              onChange={(e) => onFormChange({ ...form, avg_sentiment: parseFloat(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Effort Estimate
            </label>
            <select
              value={form.effort}
              onChange={(e) => onFormChange({ ...form, effort: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            >
              <option value="low">Low (1-2 weeks)</option>
              <option value="medium">Medium (1-2 months)</option>
              <option value="high">High (3+ months)</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Current Feedback Volume
            </label>
            <input
              type="number"
              value={form.feedback_volume_current}
              onChange={(e) => onFormChange({ ...form, feedback_volume_current: parseInt(e.target.value) || 0 })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <button
            onClick={onPredict}
            disabled={loading}
            className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Predicting...' : 'Predict Impact'}
          </button>
        </div>
      </div>

      {/* Results */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Predicted Outcomes</h3>

        {result ? (
          <div className="space-y-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <p className="text-sm font-medium text-green-900 mb-1">Revenue Impact</p>
              <p className="text-2xl font-bold text-green-600">
                ${(result.revenue_impact / 1000).toFixed(0)}K
              </p>
              <p className="text-xs text-green-700 mt-1">
                Confidence: {(result.confidence_interval.lower / 1000).toFixed(0)}K - {(result.confidence_interval.upper / 1000).toFixed(0)}K
              </p>
            </div>

            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <p className="text-sm font-medium text-blue-900 mb-1">Customer Satisfaction</p>
              <div className="flex items-baseline">
                <p className="text-2xl font-bold text-blue-600">
                  {(result.satisfaction_lift * 100).toFixed(1)}%
                </p>
                <span className="ml-2 text-sm text-blue-700">increase</span>
              </div>
            </div>

            <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
              <p className="text-sm font-medium text-purple-900 mb-1">Adoption Rate</p>
              <p className="text-2xl font-bold text-purple-600">
                {(result.adoption_rate * 100).toFixed(0)}%
              </p>
            </div>

            <div className="border-t pt-4">
              <h4 className="text-sm font-medium text-gray-700 mb-2">Contributing Factors</h4>
              <div className="space-y-2">
                {result.factors && result.factors.map((factor, index) => (
                  <div key={index} className="flex justify-between text-sm">
                    <span className="text-gray-600">{factor.name}</span>
                    <span className="font-medium text-gray-900">{factor.weight.toFixed(2)}</span>
                  </div>
                ))}
              </div>
            </div>

            {result.model_used && (
              <div className="bg-gray-50 border border-gray-200 rounded-lg p-3">
                <p className="text-xs text-gray-600">
                  Model: <span className="font-medium">{result.model_used}</span>
                </p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
            <p>Fill in feature details and click "Predict Impact"</p>
          </div>
        )}
      </div>
    </div>
  );
}

// Custom Formula Panel
function CustomFormulaPanel({ formula, variables, presets, result, loading, onFormulaChange, onVariablesChange, onCalculate, onApplyPreset }) {
  const addVariable = () => {
    const varName = prompt('Variable name:');
    if (varName && !variables[varName]) {
      onVariablesChange({ ...variables, [varName]: 0 });
    }
  };

  const updateVariable = (key, value) => {
    onVariablesChange({ ...variables, [key]: parseFloat(value) || 0 });
  };

  const removeVariable = (key) => {
    const newVars = { ...variables };
    delete newVars[key];
    onVariablesChange(newVars);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Formula Builder */}
      <div className="space-y-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Formula Builder</h3>

          {/* Presets */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Quick Start (Presets)
            </label>
            <div className="grid grid-cols-2 gap-2">
              {presets.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => onApplyPreset(preset)}
                  className="px-3 py-2 bg-gray-100 hover:bg-gray-200 rounded-lg text-sm font-medium text-gray-700 transition-colors"
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>

          {/* Formula Input */}
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Custom Formula
            </label>
            <textarea
              value={formula}
              onChange={(e) => onFormulaChange(e.target.value)}
              placeholder="e.g., (impact * reach) / effort"
              rows={3}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent font-mono text-sm"
            />
            <p className="text-xs text-gray-500 mt-1">
              Use operators: +, -, *, /, ( )
            </p>
          </div>

          {/* Variables */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <label className="block text-sm font-medium text-gray-700">
                Variables
              </label>
              <button
                onClick={addVariable}
                className="text-xs text-primary-600 hover:text-primary-700 font-medium"
              >
                + Add Variable
              </button>
            </div>
            <div className="space-y-2">
              {Object.entries(variables).map(([key, value]) => (
                <div key={key} className="flex items-center space-x-2">
                  <input
                    type="text"
                    value={key}
                    disabled
                    className="flex-1 px-3 py-2 border border-gray-300 rounded-lg bg-gray-50 text-sm"
                  />
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => updateVariable(key, e.target.value)}
                    className="w-24 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent text-sm"
                  />
                  <button
                    onClick={() => removeVariable(key)}
                    className="text-red-600 hover:text-red-700"
                  >
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                    </svg>
                  </button>
                </div>
              ))}
              {Object.keys(variables).length === 0 && (
                <p className="text-sm text-gray-500 text-center py-4">
                  No variables defined. Click "+ Add Variable" to start.
                </p>
              )}
            </div>
          </div>

          <button
            onClick={onCalculate}
            disabled={loading || !formula}
            className="w-full mt-4 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors font-medium"
          >
            {loading ? 'Calculating...' : 'Calculate Score'}
          </button>
        </div>

        {/* Help */}
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-blue-900 mb-2">Formula Tips</h4>
          <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside">
            <li>ICE: (Impact * Confidence * Ease)</li>
            <li>RICE: (Reach * Impact * Confidence) / Effort</li>
            <li>WSJF: (Value + Risk + Time) / Effort</li>
            <li>Combine multiple factors for custom scoring</li>
          </ul>
        </div>
      </div>

      {/* Result */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Calculated Score</h3>

        {result ? (
          <div className="space-y-4">
            <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
              <p className="text-sm font-medium text-primary-900 mb-2">Final Score</p>
              <p className="text-5xl font-bold text-primary-600">
                {result.score.toFixed(2)}
              </p>
            </div>

            {result.breakdown && (
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Calculation Breakdown</h4>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <pre className="text-xs font-mono text-gray-800 whitespace-pre-wrap">
                    {result.breakdown}
                  </pre>
                </div>
              </div>
            )}

            {result.interpretation && (
              <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                <p className="text-sm font-medium text-green-900 mb-1">Interpretation</p>
                <p className="text-sm text-green-800">{result.interpretation}</p>
              </div>
            )}
          </div>
        ) : (
          <div className="text-center py-12 text-gray-500">
            <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            <p>Build your formula and calculate the score</p>
          </div>
        )}
      </div>
    </div>
  );
}

// At-Risk Customers Panel
function AtRiskCustomersPanel({ customers }) {
  return (
    <div className="bg-white rounded-lg shadow">
      {customers.length > 0 ? (
        <div className="divide-y divide-gray-200">
          {customers.map((customer, index) => (
            <div key={index} className="p-6 hover:bg-gray-50 transition-colors">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center space-x-3">
                    <h3 className="text-lg font-semibold text-gray-900">
                      {customer.customer_name}
                    </h3>
                    <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-medium rounded-full">
                      At Risk
                    </span>
                  </div>

                  <div className="mt-2 flex flex-wrap gap-4 text-sm">
                    <div className="flex items-center text-gray-600">
                      <span className="mr-1">💰</span>
                      <span className="font-medium">${(customer.revenue / 1000).toFixed(0)}K</span>
                      <span className="ml-1">revenue</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="mr-1">😟</span>
                      <span className="font-medium">{customer.avg_sentiment.toFixed(2)}</span>
                      <span className="ml-1">sentiment</span>
                    </div>
                    <div className="flex items-center text-gray-600">
                      <span className="mr-1">📝</span>
                      <span className="font-medium">{customer.feedback_count}</span>
                      <span className="ml-1">feedback items</span>
                    </div>
                  </div>

                  {customer.risk_factors && customer.risk_factors.length > 0 && (
                    <div className="mt-3">
                      <p className="text-sm font-medium text-gray-700 mb-1">Risk Factors:</p>
                      <div className="flex flex-wrap gap-2">
                        {customer.risk_factors.map((factor, i) => (
                          <span key={i} className="px-2 py-1 bg-orange-100 text-orange-800 text-xs rounded">
                            {factor}
                          </span>
                        ))}
                      </div>
                    </div>
                  )}

                  {customer.recent_feedback && (
                    <div className="mt-3 bg-gray-50 rounded-lg p-3">
                      <p className="text-xs font-medium text-gray-700 mb-1">Recent Feedback:</p>
                      <p className="text-sm text-gray-600 italic">
                        "{customer.recent_feedback}"
                      </p>
                    </div>
                  )}
                </div>

                <div className="ml-4">
                  <div className="text-right">
                    <div className={`
                      text-2xl font-bold
                      ${customer.churn_risk_score >= 0.7 ? 'text-red-600' :
                        customer.churn_risk_score >= 0.4 ? 'text-orange-600' :
                        'text-yellow-600'}
                    `}>
                      {(customer.churn_risk_score * 100).toFixed(0)}%
                    </div>
                    <div className="text-xs text-gray-500">churn risk</div>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="text-center py-12">
          <svg className="w-12 h-12 mx-auto mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <p className="text-gray-500">No at-risk customers detected</p>
          <p className="text-sm text-gray-400 mt-1">
            High-value customers with negative sentiment will appear here
          </p>
        </div>
      )}
    </div>
  );
}

export default PriorityAnalysis;
