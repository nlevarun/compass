import { useState, useEffect } from 'react';
import { getFeedback, getSources } from '../services/api';

function FeedbackInbox() {
  const [feedback, setFeedback] = useState([]);
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    source_id: '',
    cluster_id: '',
  });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [feedbackRes, sourcesRes] = await Promise.all([
        getFeedback(filters),
        getSources(),
      ]);
      setFeedback(feedbackRes.data);
      setSources(sourcesRes.data);
    } catch (error) {
      console.error('Failed to load feedback:', error);
    } finally {
      setLoading(false);
    }
  };

  const getSentimentColor = (score) => {
    if (score >= 0.6) return 'text-green-600 bg-green-50';
    if (score >= 0.2) return 'text-green-500 bg-green-50';
    if (score >= -0.2) return 'text-gray-600 bg-gray-50';
    if (score >= -0.6) return 'text-orange-600 bg-orange-50';
    return 'text-red-600 bg-red-50';
  };

  const getSentimentEmoji = (score) => {
    if (score >= 0.6) return '😊';
    if (score >= 0.2) return '🙂';
    if (score >= -0.2) return '😐';
    if (score >= -0.6) return '😕';
    return '😞';
  };

  if (loading) {
    return <div className="text-center py-12">Loading feedback...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header with Filters */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Feedback Inbox</h2>
          <p className="text-gray-600 mt-1">{feedback.length} total entries</p>
        </div>

        <div className="flex space-x-4">
          <select
            value={filters.source_id}
            onChange={(e) => setFilters({ ...filters, source_id: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Sources</option>
            {sources.map((source) => (
              <option key={source.id} value={source.id}>
                {source.name} ({source.feedback_count})
              </option>
            ))}
          </select>

          <select
            value={filters.cluster_id}
            onChange={(e) => setFilters({ ...filters, cluster_id: e.target.value })}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          >
            <option value="">All Clusters</option>
            <option value="-1">Unclustered</option>
            {/* Dynamic cluster options would go here */}
          </select>
        </div>
      </div>

      {/* Feedback Table */}
      <div className="bg-white rounded-lg shadow overflow-hidden">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Customer
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Feedback
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Source
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Sentiment
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Revenue
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Date
              </th>
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {feedback.map((item) => (
              <tr key={item.id} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {item.customer_name || 'Anonymous'}
                  </div>
                </td>
                <td className="px-6 py-4">
                  <div className="text-sm text-gray-900 max-w-md">
                    {item.text.length > 120
                      ? item.text.substring(0, 120) + '...'
                      : item.text}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                    {item.source_name}
                  </span>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <span className="text-xl mr-2">
                      {getSentimentEmoji(item.sentiment_score)}
                    </span>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${getSentimentColor(item.sentiment_score)}`}>
                      {(item.sentiment_score || 0).toFixed(2)}
                    </span>
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  ${(item.customer_revenue || 0).toLocaleString()}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                  {new Date(item.submitted_at).toLocaleDateString()}
                </td>
              </tr>
            ))}
          </tbody>
        </table>

        {feedback.length === 0 && (
          <div className="text-center py-12 text-gray-500">
            No feedback found. Try syncing sources first.
          </div>
        )}
      </div>
    </div>
  );
}

export default FeedbackInbox;
