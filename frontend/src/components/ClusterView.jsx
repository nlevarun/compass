import { useState, useEffect } from 'react';
import { getClusters, getClusterDetail } from '../services/api';

function ClusterView() {
  const [clusters, setClusters] = useState([]);
  const [selectedCluster, setSelectedCluster] = useState(null);
  const [loading, setLoading] = useState(true);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadClusters();
  }, []);

  const loadClusters = async () => {
    setLoading(true);
    try {
      const response = await getClusters();
      setClusters(response.data);
    } catch (error) {
      console.error('Failed to load clusters:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleClusterClick = async (clusterId) => {
    if (selectedCluster?.id === clusterId) {
      setSelectedCluster(null);
      return;
    }

    setDetailLoading(true);
    try {
      const response = await getClusterDetail(clusterId);
      setSelectedCluster(response.data);
    } catch (error) {
      console.error('Failed to load cluster detail:', error);
    } finally {
      setDetailLoading(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading clusters...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Feedback Clusters</h2>
        <p className="text-gray-600 mt-1">
          {clusters.length} clusters discovered by NLP
        </p>
      </div>

      {/* Clusters Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {clusters.map((cluster) => (
          <ClusterCard
            key={cluster.id}
            cluster={cluster}
            onClick={() => handleClusterClick(cluster.id)}
            isSelected={selectedCluster?.id === cluster.id}
          />
        ))}
      </div>

      {clusters.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">No clusters yet. Run clustering first from the Dashboard.</p>
        </div>
      )}

      {/* Cluster Detail Modal */}
      {selectedCluster && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-start">
                <div>
                  <h3 className="text-2xl font-bold text-gray-900">
                    {selectedCluster.label}
                  </h3>
                  <div className="flex items-center space-x-4 mt-2 text-sm text-gray-600">
                    <span>📊 {selectedCluster.size} requests</span>
                    <span>💰 ${selectedCluster.total_revenue.toLocaleString()}</span>
                    <span>
                      {getSentimentEmoji(selectedCluster.avg_sentiment)}
                      {' '}
                      {(selectedCluster.avg_sentiment * 100).toFixed(0)}% sentiment
                    </span>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedCluster(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>

            <div className="p-6 overflow-y-auto max-h-[70vh]">
              <h4 className="font-semibold text-gray-900 mb-4">Feedback in this cluster:</h4>
              <div className="space-y-4">
                {selectedCluster.feedback?.map((fb) => (
                  <div key={fb.id} className="bg-gray-50 rounded-lg p-4">
                    <div className="flex justify-between items-start mb-2">
                      <span className="font-medium text-gray-900">{fb.customer_name}</span>
                      <span className="text-sm text-gray-500">
                        {new Date(fb.submitted_at).toLocaleDateString()}
                      </span>
                    </div>
                    <p className="text-gray-700 text-sm">{fb.text}</p>
                    <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
                      <span>Revenue: ${(fb.customer_revenue || 0).toLocaleString()}</span>
                      <span>
                        Sentiment: {getSentimentEmoji(fb.sentiment_score)}
                        {' '}
                        {(fb.sentiment_score || 0).toFixed(2)}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function ClusterCard({ cluster, onClick, isSelected }) {
  const priorityColor = getPriorityColor(cluster.priority_score);

  return (
    <div
      onClick={onClick}
      className={`
        bg-white rounded-lg shadow p-6 cursor-pointer transition-all
        hover:shadow-lg hover:scale-105
        ${isSelected ? 'ring-2 ring-primary-500' : ''}
      `}
    >
      {/* Priority Badge */}
      <div className="flex justify-between items-start mb-3">
        <span className={`px-3 py-1 rounded-full text-xs font-bold ${priorityColor}`}>
          Priority: {cluster.priority_score.toFixed(1)}
        </span>
        <span className="text-2xl">{getClusterIcon(cluster.label)}</span>
      </div>

      {/* Cluster Label */}
      <h3 className="text-lg font-semibold text-gray-900 mb-2">
        {cluster.label}
      </h3>

      {/* Metrics */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between">
          <span className="text-gray-600">Requests:</span>
          <span className="font-medium text-gray-900">{cluster.size}</span>
        </div>
        <div className="flex justify-between">
          <span className="text-gray-600">Revenue:</span>
          <span className="font-medium text-gray-900">
            ${(cluster.total_revenue / 1000).toFixed(0)}K
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Sentiment:</span>
          <span className="flex items-center">
            <span className="mr-1">{getSentimentEmoji(cluster.avg_sentiment)}</span>
            <span className="font-medium text-gray-900">
              {(cluster.avg_sentiment * 100).toFixed(0)}%
            </span>
          </span>
        </div>
      </div>

      {/* Click hint */}
      <div className="mt-4 pt-4 border-t border-gray-200 text-center text-xs text-gray-500">
        Click to view all feedback →
      </div>
    </div>
  );
}

function getPriorityColor(score) {
  if (score >= 60) return 'bg-red-100 text-red-800';
  if (score >= 30) return 'bg-orange-100 text-orange-800';
  return 'bg-green-100 text-green-800';
}

function getClusterIcon(label) {
  const lower = label.toLowerCase();
  if (lower.includes('mobile') || lower.includes('app')) return '📱';
  if (lower.includes('api') || lower.includes('integration')) return '🔌';
  if (lower.includes('report') || lower.includes('analytics')) return '📊';
  if (lower.includes('user') || lower.includes('sso')) return '👤';
  if (lower.includes('price') || lower.includes('billing')) return '💰';
  if (lower.includes('ui') || lower.includes('interface')) return '🎨';
  if (lower.includes('collaboration') || lower.includes('team')) return '👥';
  if (lower.includes('security') || lower.includes('compliance')) return '🔒';
  if (lower.includes('search') || lower.includes('filter')) return '🔍';
  if (lower.includes('notification')) return '🔔';
  return '📋';
}

function getSentimentEmoji(score) {
  if (score >= 0.6) return '😊';
  if (score >= 0.2) return '🙂';
  if (score >= -0.2) return '😐';
  if (score >= -0.6) return '😕';
  return '😞';
}

export default ClusterView;
