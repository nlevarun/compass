import { useState, useEffect } from 'react';
import { getRoadmap, generateRoadmap, getStats } from '../services/api';

function PrioritizeTab({ showToast }) {
  const [roadmapItems, setRoadmapItems] = useState([]);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      const [roadmapResponse, statsResponse] = await Promise.all([
        getRoadmap(),
        getStats()
      ]);
      setRoadmapItems(roadmapResponse?.data || []);
      setStats(statsResponse?.data || {});
    } catch (error) {
      console.error('Failed to load data:', error);
      setRoadmapItems([]);
      setStats({});
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    setGenerating(true);
    try {
      await generateRoadmap();
      await loadData();
      showToast('Roadmap generated successfully', 'success');
    } catch (error) {
      console.error('Roadmap generation failed:', error);
      showToast('Failed to generate roadmap. Please try again.', 'error');
    } finally {
      setGenerating(false);
    }
  };

  const handleExport = () => {
    showToast('Export coming soon', 'info');
  };

  const totalClusters = stats?.total_clusters || 0;
  const totalItems = roadmapItems.length;

  const getPriorityConfig = (priority) => {
    switch (priority?.toLowerCase()) {
      case 'high':
        return {
          badge: 'bg-red-100 text-red-800 border-red-200',
          icon: 'bg-red-500',
          label: 'HIGH'
        };
      case 'medium':
        return {
          badge: 'bg-orange-100 text-orange-800 border-orange-200',
          icon: 'bg-orange-500',
          label: 'MEDIUM'
        };
      case 'low':
        return {
          badge: 'bg-yellow-100 text-yellow-800 border-yellow-200',
          icon: 'bg-yellow-500',
          label: 'LOW'
        };
      default:
        return {
          badge: 'bg-gray-100 text-gray-800 border-gray-200',
          icon: 'bg-gray-500',
          label: priority || 'N/A'
        };
    }
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
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" />
            </svg>
          </div>
          <h2 className="text-2xl font-semibold text-gray-900 mb-3">
            Build What Customers Actually Want
          </h2>
          <p className="text-gray-600 text-base mb-6">
            Data-driven roadmap prioritized by customer demand, revenue impact, and strategic value. Know exactly what to build next.
          </p>
          <div className="flex items-center space-x-3">
            <button
              onClick={handleGenerateRoadmap}
              disabled={generating || totalClusters === 0}
              className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors shadow-sm"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  {totalItems > 0 ? 'Regenerate Roadmap' : 'Generate Roadmap'}
                </>
              )}
            </button>
            {totalItems > 0 && (
              <button
                onClick={handleExport}
                className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-gray-700 bg-white rounded-lg hover:bg-gray-50 border border-gray-300 transition-colors"
              >
                <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                </svg>
                Export to Jira
              </button>
            )}
            {totalClusters === 0 && (
              <span className="text-sm text-gray-600">
                Run AI analysis first to generate roadmap
              </span>
            )}
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      {totalItems > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Total Items</p>
            <p className="text-2xl font-semibold text-gray-900">{totalItems}</p>
            <p className="text-xs text-gray-500 mt-0.5">in roadmap</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">High Priority</p>
            <p className="text-2xl font-semibold text-gray-900">
              {roadmapItems.filter(i => i.priority?.toLowerCase() === 'high').length}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">items</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Revenue Impact</p>
            <p className="text-2xl font-semibold text-gray-900">
              ${((stats?.total_revenue_impact || 0) / 1000000).toFixed(1)}M
            </p>
            <p className="text-xs text-gray-500 mt-0.5">potential</p>
          </div>
          <div className="bg-white rounded-lg border border-gray-200 p-5">
            <p className="text-xs font-medium text-gray-600 uppercase tracking-wide mb-1">Customer Requests</p>
            <p className="text-2xl font-semibold text-gray-900">
              {roadmapItems.reduce((sum, item) => sum + (item.request_count || 0), 0)}
            </p>
            <p className="text-xs text-gray-500 mt-0.5">total</p>
          </div>
        </div>
      )}

      {/* Roadmap Items */}
      {totalItems > 0 ? (
        <div>
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Priority Roadmap</h3>
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500">Sorted by priority score</span>
            </div>
          </div>
          <div className="space-y-3">
            {roadmapItems.map((item, index) => (
              <RoadmapCard
                key={item.id || index}
                item={item}
                index={index}
                priorityConfig={getPriorityConfig(item.priority)}
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
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
              </svg>
            </div>
            <h3 className="text-lg font-semibold text-gray-900 mb-2">No Roadmap Yet</h3>
            <p className="text-gray-600 mb-6 max-w-md mx-auto">
              {totalClusters === 0
                ? 'Import feedback and run AI analysis first, then generate your prioritized roadmap.'
                : 'Generate a prioritized roadmap based on your AI-analyzed themes. This takes about 30 seconds.'
              }
            </p>
            <button
              onClick={handleGenerateRoadmap}
              disabled={generating || totalClusters === 0}
              className="inline-flex items-center px-5 py-2.5 text-sm font-medium text-white bg-indigo-600 rounded-lg hover:bg-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {generating ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                  Generating...
                </>
              ) : (
                <>
                  <svg className="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                  Generate Roadmap
                </>
              )}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function RoadmapCard({ item, index, priorityConfig }) {
  const [expanded, setExpanded] = useState(false);
  const score = item.priority_score || 0;
  const requestCount = item.request_count || 0;
  const revenueImpact = item.revenue_impact || 0;
  const customers = item.top_customers || [];
  const description = item.description || '';

  return (
    <div className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors">
      <div className="p-5">
        <div className="flex items-start space-x-4">
          <div className={`flex-shrink-0 w-10 h-10 ${priorityConfig.icon} rounded-lg flex items-center justify-center text-white font-semibold`}>
            {index + 1}
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-start justify-between mb-2">
              <div className="flex-1 mr-4">
                <h4 className="text-base font-semibold text-gray-900 mb-1">
                  {item.title || item.name || `Feature ${index + 1}`}
                </h4>
                {description && !expanded && (
                  <p className="text-sm text-gray-600 line-clamp-2 mb-2">
                    {description}
                  </p>
                )}
              </div>
              <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium ${priorityConfig.badge} border flex-shrink-0`}>
                {priorityConfig.label}
              </span>
            </div>

            {/* Expanded Description */}
            {expanded && description && (
              <p className="text-sm text-gray-600 mb-3">
                {description}
              </p>
            )}

            {/* Metrics */}
            <div className="flex flex-wrap items-center gap-4 mb-3 text-sm">
              <div className="flex items-center text-gray-700">
                <svg className="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
                <span className="font-medium">Score: {score}</span>
              </div>
              <div className="flex items-center text-gray-700">
                <svg className="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
                <span>{requestCount} {requestCount === 1 ? 'request' : 'requests'}</span>
              </div>
              {revenueImpact > 0 && (
                <div className="flex items-center text-gray-700">
                  <svg className="w-4 h-4 mr-1.5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>${(revenueImpact / 1000).toFixed(0)}K revenue</span>
                </div>
              )}
            </div>

            {/* Top Customers */}
            {customers.length > 0 && (
              <div className="mb-3">
                <p className="text-xs font-medium text-gray-600 mb-1.5">Top customers:</p>
                <div className="flex flex-wrap gap-2">
                  {customers.slice(0, expanded ? undefined : 3).map((customer, idx) => (
                    <span
                      key={idx}
                      className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-indigo-50 text-indigo-700 border border-indigo-100"
                    >
                      {customer}
                    </span>
                  ))}
                  {!expanded && customers.length > 3 && (
                    <span className="inline-flex items-center px-2.5 py-1 rounded-md text-xs font-medium bg-gray-100 text-gray-600">
                      +{customers.length - 3} more
                    </span>
                  )}
                </div>
              </div>
            )}

            {/* Actions */}
            <div className="flex items-center space-x-4 text-sm">
              <button
                onClick={() => setExpanded(!expanded)}
                className="text-indigo-600 hover:text-indigo-700 font-medium"
              >
                {expanded ? 'Show less' : 'View details'}
              </button>
              <button className="text-gray-600 hover:text-gray-900 font-medium">
                Add to Sprint
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default PrioritizeTab;
