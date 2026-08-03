import { useState, useEffect } from 'react';
import { getRoadmap } from '../services/api';

function RoadmapDashboard() {
  const [roadmap, setRoadmap] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState('all'); // all, proposed, planned, in_progress, shipped

  useEffect(() => {
    loadRoadmap();
  }, []);

  const loadRoadmap = async () => {
    setLoading(true);
    try {
      const response = await getRoadmap();
      setRoadmap(response.data);
    } catch (error) {
      console.error('Failed to load roadmap:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredRoadmap = filter === 'all'
    ? roadmap
    : roadmap.filter((item) => item.status === filter);

  if (loading) {
    return <div className="text-center py-12">Loading roadmap...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with Filter */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Product Roadmap</h2>
          <p className="text-gray-600 mt-1">
            Data-driven prioritization from {roadmap.length} clusters
          </p>
        </div>

        <select
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
        >
          <option value="all">All Items ({roadmap.length})</option>
          <option value="proposed">Proposed ({roadmap.filter(i => i.status === 'proposed').length})</option>
          <option value="planned">Planned ({roadmap.filter(i => i.status === 'planned').length})</option>
          <option value="in_progress">In Progress ({roadmap.filter(i => i.status === 'in_progress').length})</option>
          <option value="shipped">Shipped ({roadmap.filter(i => i.status === 'shipped').length})</option>
        </select>
      </div>

      {/* Priority Legend */}
      <div className="bg-white rounded-lg shadow p-4">
        <div className="flex items-center space-x-6 text-sm">
          <span className="font-medium text-gray-700">Priority Scale:</span>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-red-500 mr-2"></div>
            <span>High (60+)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-orange-500 mr-2"></div>
            <span>Medium (30-60)</span>
          </div>
          <div className="flex items-center">
            <div className="w-3 h-3 rounded-full bg-green-500 mr-2"></div>
            <span>Low (<30)</span>
          </div>
        </div>
      </div>

      {/* Roadmap Items */}
      <div className="space-y-4">
        {filteredRoadmap.map((item) => (
          <RoadmapItem key={item.id} item={item} />
        ))}
      </div>

      {filteredRoadmap.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <p className="text-gray-500">
            {filter === 'all'
              ? 'No roadmap items yet. Generate roadmap from the Dashboard.'
              : `No ${filter.replace('_', ' ')} items.`}
          </p>
        </div>
      )}

      {/* Summary Stats */}
      {roadmap.length > 0 && (
        <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-primary-900 mb-4">📈 Impact Summary</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-primary-700">Total Customer Requests</p>
              <p className="text-2xl font-bold text-primary-900">
                {roadmap.reduce((sum, item) => sum + item.request_count, 0)}
              </p>
            </div>
            <div>
              <p className="text-sm text-primary-700">Total Revenue Impact</p>
              <p className="text-2xl font-bold text-primary-900">
                ${(roadmap.reduce((sum, item) => sum + item.impacted_revenue, 0) / 1000000).toFixed(1)}M
              </p>
            </div>
            <div>
              <p className="text-sm text-primary-700">Average Priority Score</p>
              <p className="text-2xl font-bold text-primary-900">
                {(roadmap.reduce((sum, item) => sum + item.priority_score, 0) / roadmap.length).toFixed(1)}
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function RoadmapItem({ item }) {
  const priorityColor = getPriorityColorClass(item.priority_score);
  const statusBadge = getStatusBadge(item.status);

  return (
    <div className="bg-white rounded-lg shadow hover:shadow-md transition-shadow">
      <div className="p-6">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start space-x-4 flex-1">
            {/* Rank Badge */}
            <div className={`flex-shrink-0 w-12 h-12 rounded-full ${priorityColor} flex items-center justify-center`}>
              <span className="text-lg font-bold text-white">#{item.rank}</span>
            </div>

            {/* Title and Metrics */}
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                {item.title}
              </h3>
              <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                <div className="flex items-center">
                  <span className="mr-1">📊</span>
                  <span className="font-medium">{item.request_count}</span>
                  <span className="ml-1">requests</span>
                </div>
                <div className="flex items-center">
                  <span className="mr-1">💰</span>
                  <span className="font-medium">${(item.impacted_revenue / 1000).toFixed(0)}K</span>
                  <span className="ml-1">revenue</span>
                </div>
                <div className="flex items-center">
                  <span className="mr-1">⭐</span>
                  <span className="font-medium">{item.priority_score.toFixed(1)}</span>
                  <span className="ml-1">priority</span>
                </div>
              </div>
            </div>
          </div>

          {/* Status Badge */}
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${statusBadge.color}`}>
            {statusBadge.text}
          </span>
        </div>

        {/* Description */}
        {item.description && (
          <p className="text-sm text-gray-600 mt-2 ml-16">
            {item.description}
          </p>
        )}

        {/* Priority Breakdown */}
        <div className="mt-4 ml-16">
          <div className="flex items-center">
            <div className="flex-1 bg-gray-200 rounded-full h-2 overflow-hidden">
              <div
                className={`h-full ${priorityColor}`}
                style={{ width: `${Math.min(item.priority_score, 100)}%` }}
              ></div>
            </div>
            <span className="ml-3 text-xs font-medium text-gray-600">
              {getPriorityLabel(item.priority_score)}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

function getPriorityColorClass(score) {
  if (score >= 60) return 'bg-red-500';
  if (score >= 30) return 'bg-orange-500';
  return 'bg-green-500';
}

function getPriorityLabel(score) {
  if (score >= 60) return 'High Priority';
  if (score >= 30) return 'Medium Priority';
  return 'Low Priority';
}

function getStatusBadge(status) {
  const badges = {
    proposed: { text: '📝 Proposed', color: 'bg-gray-100 text-gray-700' },
    planned: { text: '📅 Planned', color: 'bg-blue-100 text-blue-700' },
    in_progress: { text: '🚧 In Progress', color: 'bg-yellow-100 text-yellow-700' },
    shipped: { text: '✅ Shipped', color: 'bg-green-100 text-green-700' },
  };
  return badges[status] || badges.proposed;
}

export default RoadmapDashboard;
