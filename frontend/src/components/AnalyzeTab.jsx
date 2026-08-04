import { useState, useEffect } from 'react';
import { getClusters, runClustering, getStats } from '../services/api';

function AnalyzeTab({ showToast }) {
  const [clusters, setClusters] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [clustersResponse, statsResponse] = await Promise.all([
        getClusters(),
        getStats()
      ]);
      setClusters(clustersResponse?.data || []);
      setStats(statsResponse?.data || {});
    } catch (error) {
      console.error('Failed to load data:', error);
      setClusters([]);
      setStats({});
    } finally {
      setLoading(false);
    }
  };

  const handleRunAnalysis = async () => {
    setAnalyzing(true);
    try {
      await runClustering();
      await loadData();
      showToast('AI analysis completed successfully', 'success');
    } catch (error) {
      console.error('Analysis failed:', error);
      showToast('Failed to run analysis. Please try again.', 'error');
    } finally {
      setAnalyzing(false);
    }
  };

  const totalFeedback = stats?.total_feedback || 0;
  const totalClusters = clusters.length;

  const getColorClass = (index) => {
    const colors = [
      'bg-blue-100 text-blue-800 border-blue-200',
      'bg-green-100 text-green-800 border-green-200',
      'bg-yellow-100 text-yellow-800 border-yellow-200',
      'bg-purple-100 text-purple-800 border-purple-200',
      'bg-pink-100 text-pink-800 border-pink-200',
      'bg-indigo-100 text-indigo-800 border-indigo-200',
      'bg-red-100 text-red-800 border-red-200',
      'bg-orange-100 text-orange-800 border-orange-200',
    ];
    return colors[index % colors.length];
  };

  const getIconColorClass = (index) => {
    const colors = [
      'bg-blue-500',
      'bg-green-500',
      'bg-yellow-500',
      'bg-purple-500',
      'bg-pink-500',
      'bg-indigo-500',
      'bg-red-500',
      'bg-orange-500',
    ];
    return colors[index % colors.length];
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Hero Section */}
      <div className="bg-gradient-to-br from-indigo-50 to-white rounded-xl border border-indigo-100 p-8">
        <div className="max-w-2xl">
          <div className="inline-flex items-center justify-center w-12 h-12 bg-indigo-600 rounded-lg mb-4">
            <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">
            Understand What Matters with AI
          </h2>
          <p className="text-gray-600 text-base mb-6">
            Our AI analyzes your feedback and groups similar requests together. Discover themes, patterns, and trends that would take hours to find manually.
          </p>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleRunAnalysis}
              disabled={analyzing || totalFeedback === 0}
              className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
            >
              {analyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  {totalClusters > 0 ? 'Re-run Analysis' : 'Run AI Analysis'}
                </>
              )}
            </button>
            {totalFeedback === 0 && (
              <span className="text-sm text-gray-600">
                Import feedback first to run analysis
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      {totalClusters > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Total Themes</p>
            <p className="text-2xl font-semibold text-gray-900">{totalClusters}</p>
            <p className="text-xs text-gray-500 mt-0.5">patterns identified</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Feedback Analyzed</p>
            <p className="text-2xl font-semibold text-gray-900">{totalFeedback}</p>
            <p className="text-xs text-gray-500 mt-0.5">items processed</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Coverage</p>
            <p className="text-2xl font-semibold text-gray-900">
              {totalFeedback > 0 ? Math.round((clusters.reduce((sum, c) => sum + (c.size || 0), 0) / totalFeedback) * 100) : 0}%
            </p>
            <p className="text-xs text-gray-500 mt-0.5">feedback grouped</p>
          </div>
        </div>
      )}

      {/* Clusters / Themes */}
      {totalClusters > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">AI-Discovered Themes</h3>
            <span className="text-sm text-gray-500">{totalClusters} themes found</span>
          </div>
          <div className="space-y-3">
            {clusters.map((cluster, index) => (
              <ClusterCard
                key={cluster.id || index}
                cluster={cluster}
                index={index}
                colorClass={getColorClass(index)}
                iconColorClass={getIconColorClass(index)}
              />
            ))}
          </div>
        </div>
      ) : (
        // Empty State
        <div className="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300 p-12">
          <div className="text-center">
            <div className="inline-flex items-center justify-center w-16 h-16 bg-gray-200 rounded-full mb-4">
              <svg className="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Analysis Yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {totalFeedback === 0
                ? 'Import feedback first, then run AI analysis to discover themes and patterns.'
                : 'Run AI analysis to discover themes and patterns in your feedback. This usually takes 30-60 seconds.'
              }
            </p>
            <button
              onClick={handleRunAnalysis}
              disabled={analyzing || totalFeedback === 0}
              className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {analyzing ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Analyzing...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Run AI Analysis
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function ClusterCard({ cluster, index, colorClass, iconColorClass }) {
  const [expanded, setExpanded] = useState(false);
  const size = cluster.size || 0;
  const examples = cluster.examples || [];
  const keywords = cluster.keywords || [];

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
      <div className="p-5">
        <div className="flex items-start space-x-4">
          <div className={`flex-shrink-0 w-10 h-10 ${iconColorClass} rounded-lg flex items-center justify-center text-white font-semibold`}>
            {index + 1}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-base font-semibold text-gray-900">
                {cluster.label || cluster.name || `Theme ${index + 1}`}
              </h4>
              <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${colorClass} border`}>
                {size} {size === 1 ? 'mention' : 'mentions'}
              </span>
            </div>

            {/* Keywords */}
            {keywords.length > 0 && (
              <div className="flex flex-wrap gap-2 mb-3">
                {keywords.slice(0, 5).map((keyword, idx) => (
                  <span
                    key={idx}
                    className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-700"
                  >
                    {keyword}
                  </span>
                ))}
              </div>
            )}

            {/* Example Preview */}
            {examples.length > 0 && (
              <div className="bg-gray-50 rounded p-3 mb-3">
                <p className="text-sm text-gray-700 line-clamp-2">
                  "{examples[0]}"
                </p>
              </div>
            )}

            {/* Expanded Examples */}
            {expanded && examples.length > 1 && (
              <div className="space-y-2 mb-3">
                {examples.slice(1, 5).map((example, idx) => (
                  <div key={idx} className="bg-gray-50 rounded p-3">
                    <p className="text-sm text-gray-700">
                      "{example}"
                    </p>
                  </div>
                ))}
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center space-x-4 text-sm">
              {examples.length > 1 && (
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="text-indigo-600 hover:text-indigo-700 font-medium"
                >
                  {expanded ? 'Show less' : `View all ${examples.length} examples`}
                </button>
              )}
              <button className="text-gray-600 hover:text-gray-900 font-medium">
                View Details
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default AnalyzeTab;
