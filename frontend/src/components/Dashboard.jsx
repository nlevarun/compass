import { useState, useEffect } from 'react';
import { getStats, syncSources, runClustering, generateRoadmap } from '../services/api';

function Dashboard() {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [clustering, setClustering] = useState(false);
  const [generating, setGenerating] = useState(false);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      const response = await getStats();
      setStats(response.data);
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    try {
      await syncSources();
      await loadStats();
      alert('✅ Feedback synced successfully!');
    } catch (error) {
      console.error('Sync failed:', error);
      alert('❌ Sync failed. Check console for details.');
    } finally {
      setSyncing(false);
    }
  };

  const handleClustering = async () => {
    setClustering(true);
    try {
      await runClustering();
      await loadStats();
      alert('✅ Clustering complete!');
    } catch (error) {
      console.error('Clustering failed:', error);
      alert('❌ Clustering failed. Check console for details.');
    } finally {
      setClustering(false);
    }
  };

  const handleGenerateRoadmap = async () => {
    setGenerating(true);
    try {
      await generateRoadmap();
      await loadStats();
      alert('✅ Roadmap generated!');
    } catch (error) {
      console.error('Roadmap generation failed:', error);
      alert('❌ Roadmap generation failed. Check console for details.');
    } finally {
      setGenerating(false);
    }
  };

  if (loading) {
    return <div className="text-center py-12">Loading dashboard...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Feedback"
          value={stats?.total_feedback || 0}
          icon="📝"
          color="blue"
        />
        <StatCard
          title="Active Sources"
          value={stats?.total_sources || 0}
          icon="🔌"
          color="green"
        />
        <StatCard
          title="Clusters"
          value={stats?.total_clusters || 0}
          icon="🔗"
          color="purple"
        />
        <StatCard
          title="Roadmap Items"
          value={stats?.total_roadmap_items || 0}
          icon="🗺️"
          color="orange"
        />
      </div>

      {/* Additional Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <MetricCard
          title="Total Revenue Impact"
          value={`$${(stats?.total_revenue_impact || 0).toLocaleString()}`}
          subtitle="From all feedback customers"
          icon="💰"
        />
        <MetricCard
          title="Average Sentiment"
          value={((stats?.avg_sentiment || 0) * 100).toFixed(0) + '%'}
          subtitle={getSentimentLabel(stats?.avg_sentiment || 0)}
          icon="😊"
        />
        <MetricCard
          title="Recent Feedback (30d)"
          value={stats?.recent_feedback_30d || 0}
          subtitle="Last 30 days"
          icon="📅"
        />
      </div>

      {/* Action Buttons */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <ActionButton
            onClick={handleSync}
            loading={syncing}
            icon="🔄"
            title="Sync Feedback"
            description="Pull latest feedback from all sources"
          />
          <ActionButton
            onClick={handleClustering}
            loading={clustering}
            icon="🧠"
            title="Run Clustering"
            description="Group similar feedback with NLP"
          />
          <ActionButton
            onClick={handleGenerateRoadmap}
            loading={generating}
            icon="🚀"
            title="Generate Roadmap"
            description="Create prioritized roadmap"
          />
        </div>
      </div>

      {/* Workflow Guide */}
      <div className="bg-primary-50 border border-primary-200 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-primary-900 mb-3">
          📖 Getting Started Workflow
        </h3>
        <ol className="space-y-2 text-primary-800">
          <li className="flex items-start">
            <span className="font-semibold mr-2">1.</span>
            <span><strong>Sync Feedback</strong> - Pull data from all 8 sources (500+ entries)</span>
          </li>
          <li className="flex items-start">
            <span className="font-semibold mr-2">2.</span>
            <span><strong>Run Clustering</strong> - Let NLP group similar requests automatically</span>
          </li>
          <li className="flex items-start">
            <span className="font-semibold mr-2">3.</span>
            <span><strong>Generate Roadmap</strong> - Get data-driven priority scores</span>
          </li>
          <li className="flex items-start">
            <span className="font-semibold mr-2">4.</span>
            <span><strong>Explore</strong> - Use tabs above to view feedback, clusters, and roadmap</span>
          </li>
        </ol>
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 text-blue-600',
    green: 'bg-green-50 text-green-600',
    purple: 'bg-purple-50 text-purple-600',
    orange: 'bg-orange-50 text-orange-600',
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mt-2">{value}</p>
        </div>
        <div className={`text-4xl p-3 rounded-lg ${colorClasses[color]}`}>
          {icon}
        </div>
      </div>
    </div>
  );
}

function MetricCard({ title, value, subtitle, icon }) {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center mb-3">
        <span className="text-2xl mr-2">{icon}</span>
        <h3 className="text-sm font-medium text-gray-600">{title}</h3>
      </div>
      <p className="text-2xl font-bold text-gray-900">{value}</p>
      <p className="text-sm text-gray-500 mt-1">{subtitle}</p>
    </div>
  );
}

function ActionButton({ onClick, loading, icon, title, description }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className="flex flex-col items-start p-4 border-2 border-gray-200 rounded-lg hover:border-primary-500 hover:bg-primary-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
    >
      <div className="text-3xl mb-2">{icon}</div>
      <h4 className="font-semibold text-gray-900">{title}</h4>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
      {loading && (
        <div className="mt-2 text-sm text-primary-600">Processing...</div>
      )}
    </button>
  );
}

function getSentimentLabel(score) {
  if (score >= 0.6) return 'Very Positive';
  if (score >= 0.2) return 'Positive';
  if (score >= -0.2) return 'Neutral';
  if (score >= -0.6) return 'Negative';
  return 'Very Negative';
}

export default Dashboard;
