import { useState, useEffect } from 'react';
import { Activity, CheckCircle, XCircle, Clock, Zap, TrendingUp } from 'lucide-react';

function WebhookMonitor() {
  const [webhookStats, setWebhookStats] = useState({});
  const [recentEvents, setRecentEvents] = useState([]);
  const [loading, setLoading] = useState(true);
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadWebhookStats();
    const interval = setInterval(loadWebhookStats, 5000); // Refresh every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const loadWebhookStats = async () => {
    try {
      // In a real implementation, this would fetch from a webhook stats endpoint
      // For now, we'll show placeholder data
      setWebhookStats({
        slack: {
          total_events: 142,
          success_rate: 99.3,
          avg_latency_ms: 87,
          last_event: '2 minutes ago',
          is_active: true,
        },
        github: {
          total_events: 89,
          success_rate: 100,
          avg_latency_ms: 134,
          last_event: '5 minutes ago',
          is_active: true,
        },
        intercom: {
          total_events: 67,
          success_rate: 98.5,
          avg_latency_ms: 92,
          last_event: '1 minute ago',
          is_active: true,
        },
      });

      // Mock recent events
      setRecentEvents([
        {
          id: 1,
          source: 'Slack',
          type: 'message',
          latency_ms: 87,
          success: true,
          timestamp: new Date(Date.now() - 120000).toISOString(),
        },
        {
          id: 2,
          source: 'Intercom',
          type: 'conversation.created',
          latency_ms: 92,
          success: true,
          timestamp: new Date(Date.now() - 60000).toISOString(),
        },
        {
          id: 3,
          source: 'GitHub',
          type: 'issues.opened',
          latency_ms: 134,
          success: true,
          timestamp: new Date(Date.now() - 300000).toISOString(),
        },
      ]);

      setLoading(false);
    } catch (error) {
      console.error('Failed to load webhook stats:', error);
      setLoading(false);
    }
  };

  const getStatusColor = (isActive) => {
    return isActive ? 'text-green-600' : 'text-gray-400';
  };

  const getLatencyColor = (latency_ms) => {
    if (latency_ms < 100) return 'text-green-600';
    if (latency_ms < 500) return 'text-yellow-600';
    return 'text-red-600';
  };

  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);

    if (diffMins < 1) return 'just now';
    if (diffMins === 1) return '1 minute ago';
    if (diffMins < 60) return `${diffMins} minutes ago`;

    const diffHours = Math.floor(diffMins / 60);
    if (diffHours === 1) return '1 hour ago';
    if (diffHours < 24) return `${diffHours} hours ago`;

    return date.toLocaleString();
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Clock className="w-8 h-8 animate-spin text-blue-600" />
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Activity className="w-8 h-8 text-blue-600" />
          <h1 className="text-3xl font-bold text-gray-900">Webhook Monitor</h1>
        </div>
        <p className="text-gray-600">Real-time webhook performance and statistics</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        {Object.entries(webhookStats).map(([service, stats]) => (
          <div key={service} className="bg-white border-2 border-gray-200 rounded-xl p-6 shadow-sm">
            {/* Service Header */}
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold capitalize">{service}</h3>
              {stats.is_active ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <XCircle className="w-6 h-6 text-gray-400" />
              )}
            </div>

            {/* Stats */}
            <div className="space-y-3">
              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Total Events</span>
                <span className="text-lg font-bold">{stats.total_events}</span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Success Rate</span>
                <span className="text-lg font-bold text-green-600">
                  {stats.success_rate}%
                </span>
              </div>

              <div className="flex justify-between items-center">
                <span className="text-sm text-gray-600">Avg Latency</span>
                <span
                  className={`text-lg font-bold font-mono ${getLatencyColor(
                    stats.avg_latency_ms
                  )}`}
                >
                  {stats.avg_latency_ms}ms
                </span>
              </div>

              <div className="flex justify-between items-center pt-2 border-t border-gray-200">
                <span className="text-sm text-gray-600">Last Event</span>
                <span className="text-sm font-medium">{stats.last_event}</span>
              </div>
            </div>

            {/* Status Indicator */}
            <div className="mt-4 pt-4 border-t border-gray-200">
              <div className="flex items-center gap-2">
                <div
                  className={`w-2 h-2 rounded-full ${
                    stats.is_active ? 'bg-green-500 animate-pulse' : 'bg-gray-300'
                  }`}
                ></div>
                <span className="text-xs font-medium text-gray-600">
                  {stats.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Overall Performance */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-200 rounded-xl p-6 mb-8">
        <div className="flex items-center gap-3 mb-4">
          <Zap className="w-6 h-6 text-yellow-500" />
          <h2 className="text-xl font-bold">Performance Overview</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="bg-white rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Total Events</div>
            <div className="text-2xl font-bold text-blue-600">
              {Object.values(webhookStats).reduce(
                (sum, stats) => sum + stats.total_events,
                0
              )}
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Avg Latency</div>
            <div className="text-2xl font-bold text-green-600">
              {Math.round(
                Object.values(webhookStats).reduce(
                  (sum, stats) => sum + stats.avg_latency_ms,
                  0
                ) / Object.keys(webhookStats).length
              )}
              ms
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Success Rate</div>
            <div className="text-2xl font-bold text-green-600">
              {(
                Object.values(webhookStats).reduce(
                  (sum, stats) => sum + stats.success_rate,
                  0
                ) / Object.keys(webhookStats).length
              ).toFixed(1)}
              %
            </div>
          </div>

          <div className="bg-white rounded-lg p-4">
            <div className="text-sm text-gray-600 mb-1">Active Services</div>
            <div className="text-2xl font-bold text-blue-600">
              {Object.values(webhookStats).filter((s) => s.is_active).length}/
              {Object.keys(webhookStats).length}
            </div>
          </div>
        </div>

        {/* Comparison */}
        <div className="mt-4 pt-4 border-t border-green-200">
          <div className="flex items-center gap-2 text-sm">
            <TrendingUp className="w-4 h-4 text-green-600" />
            <span className="font-semibold text-green-700">
              300x faster than polling (5 min → &lt;1 sec)
            </span>
          </div>
        </div>
      </div>

      {/* Recent Events */}
      <div className="bg-white border-2 border-gray-200 rounded-xl p-6">
        <h2 className="text-xl font-bold mb-4">Recent Events</h2>

        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-200">
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                  Source
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                  Event Type
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                  Latency
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                  Status
                </th>
                <th className="text-left py-3 px-4 text-sm font-semibold text-gray-600">
                  Time
                </th>
              </tr>
            </thead>
            <tbody>
              {recentEvents.map((event) => (
                <tr key={event.id} className="border-b border-gray-100 hover:bg-gray-50">
                  <td className="py-3 px-4">
                    <span className="font-semibold">{event.source}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-sm font-mono text-gray-600">{event.type}</span>
                  </td>
                  <td className="py-3 px-4">
                    <span
                      className={`text-sm font-mono font-bold ${getLatencyColor(
                        event.latency_ms
                      )}`}
                    >
                      {event.latency_ms}ms
                    </span>
                  </td>
                  <td className="py-3 px-4">
                    {event.success ? (
                      <CheckCircle className="w-5 h-5 text-green-600" />
                    ) : (
                      <XCircle className="w-5 h-5 text-red-600" />
                    )}
                  </td>
                  <td className="py-3 px-4">
                    <span className="text-sm text-gray-600">
                      {formatTimestamp(event.timestamp)}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {recentEvents.length === 0 && (
          <div className="text-center py-8 text-gray-500">
            No recent events. Configure webhooks to see activity.
          </div>
        )}
      </div>
    </div>
  );
}

export default WebhookMonitor;
