import { useState, useEffect } from 'react';
import { getStats, syncSources, runClustering, generateRoadmap } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [clustering, setClustering] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await getStats();
      const data = response?.data || {};
      setStats(data);

      // Determine current step based on data
      if ((data.total_feedback || 0) === 0) {
        setCurrentStep(0);
      } else if ((data.total_clusters || 0) === 0) {
        setCurrentStep(1);
      } else if ((data.total_roadmap_items || 0) === 0) {
        setCurrentStep(2);
      } else {
        setCurrentStep(3);
      }
    } catch (error) {
      console.error('Failed to load stats:', error);
      // Set default stats on error
      setStats({
        total_feedback: 0,
        total_clusters: 0,
        total_roadmap_items: 0,
        total_revenue_impact: 0
      });
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncSources();
      await loadStats();
    } catch (error) {
      console.error('Sync failed:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Sync failed. Please check your connection.';
      alert(errorMsg);
    } finally {
      setSyncing(false);
    }
  };

  const handleClustering = async () => {
    setClustering(true);
    try {
      await runClustering();
      await loadStats();
    } catch (error) {
      console.error('Clustering failed:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Clustering failed. Please check your connection.';
      alert(errorMsg);
    } finally {
      setClustering(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    setGenerating(true);
    try {
      await generateRoadmap();
      await loadStats();
    } catch (error) {
      console.error('Roadmap generation failed:', error);
      const errorMsg = error.response?.data?.detail || error.message || 'Roadmap generation failed. Please check your connection.';
      alert(errorMsg);
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  const steps = [
    {
      number: 1,
      title: 'Sync Feedback',
      description: 'Import feedback from 8 sources',
      action: handleSync,
      loading: syncing,
      buttonText: 'Import Feedback',
      completed: stats?.total_feedback > 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" />
        </svg>
      ),
    },
    {
      number: 2,
      title: 'Analyze Patterns',
      description: 'Group similar feedback using NLP',
      action: handleClustering,
      loading: clustering,
      buttonText: 'Run Analysis',
      completed: stats?.total_clusters > 0,
      disabled: stats?.total_feedback === 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
    },
    {
      number: 3,
      title: 'Generate Roadmap',
      description: 'Create priority-ranked roadmap',
      action: handleGenerateRoadmap,
      loading: generating,
      buttonText: 'Build Roadmap',
      completed: stats?.total_roadmap_items > 0,
      disabled: stats?.total_clusters === 0,
      icon: (
        <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
        </svg>
      ),
    },
  ];

  return (
    <div className="space-y-8">
      {/* Welcome Section */}
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-2">Welcome to Compass</h2>
        <p className="text-gray-600">
          Transform scattered customer feedback into actionable product insights
        </p>
      </div>

      {/* Getting Started Guide */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-lg font-semibold text-gray-900">Getting Started</h3>
          <span className="text-sm text-gray-500">
            Step {currentStep + 1} of {steps.length}
          </span>
        </div>

        {/* Progress Bar */}
        <div className="mb-8">
          <div className="flex items-center">
            {steps.map((step, index) => (
              <div key={step.number} className="flex items-center flex-1">
                <div className="flex flex-col items-center flex-1">
                  <div
                    className={`
                      w-10 h-10 rounded-full flex items-center justify-center text-sm font-medium
                      ${step.completed
                        ? 'bg-success-500 text-white'
                        : index === currentStep
                        ? 'bg-primary-600 text-white'
                        : 'bg-gray-200 text-gray-600'
                      }
                    `}
                  >
                    {step.completed ? (
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                    ) : (
                      step.number
                    )}
                  </div>
                  <span className={`mt-2 text-xs font-medium ${step.completed || index === currentStep ? 'text-gray-900' : 'text-gray-500'}`}>
                    {step.title}
                  </span>
                </div>
                {index < steps.length - 1 && (
                  <div className={`h-0.5 flex-1 mx-2 ${step.completed ? 'bg-success-500' : 'bg-gray-200'}`} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Current Step Card */}
        {currentStep < 3 && (
          <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center text-primary-600">
                {steps[currentStep].icon}
              </div>
              <div className="flex-1">
                <h4 className="text-base font-semibold text-gray-900 mb-1">
                  {steps[currentStep].title}
                </h4>
                <p className="text-sm text-gray-600 mb-4">
                  {steps[currentStep].description}
                </p>
                <button
                  onClick={steps[currentStep].action}
                  disabled={steps[currentStep].disabled || steps[currentStep].loading}
                  className="inline-flex items-center px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {steps[currentStep].loading ? (
                    <>
                      <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                      Processing...
                    </>
                  ) : (
                    steps[currentStep].buttonText
                  )}
                </button>
              </div>
            </div>
          </div>
        )}

        {/* All Steps Complete */}
        {currentStep === 3 && (
          <div className="bg-success-50 rounded-lg p-6 border border-success-200">
            <div className="flex items-start space-x-4">
              <div className="flex-shrink-0 w-12 h-12 bg-success-100 rounded-lg flex items-center justify-center text-success-600">
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <h4 className="text-base font-semibold text-gray-900 mb-1">
                  Setup Complete!
                </h4>
                <p className="text-sm text-gray-600">
                  Your feedback has been analyzed and prioritized. Explore the tabs above to view insights and roadmap.
                </p>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          label="Total Feedback"
          value={stats?.total_feedback || 0}
          subtext="from 8 sources"
        />
        <StatCard
          label="Insights Found"
          value={stats?.total_clusters || 0}
          subtext="similar patterns"
        />
        <StatCard
          label="Roadmap Items"
          value={stats?.total_roadmap_items || 0}
          subtext="prioritized"
        />
        <StatCard
          label="Customer Revenue"
          value={`$${((stats?.total_revenue_impact || 0) / 1000000).toFixed(1)}M`}
          subtext="total impact"
        />
      </div>
    </div>
  );
}

function StatCard({ label, value, subtext }) {
  return (
    <div className="bg-white rounded-lg border border-gray-200 p-5">
      <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">{label}</p>
      <p className="text-2xl font-semibold text-gray-900 mb-0.5">{value}</p>
      <p className="text-xs text-gray-500">{subtext}</p>
    </div>
  );
}

export default Dashboard;
