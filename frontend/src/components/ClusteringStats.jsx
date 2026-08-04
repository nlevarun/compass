import { useState, useEffect } from 'react';
import { getClusteringQuality } from '../services/api';

function ClusteringStats() {
  const [quality, setQuality] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadQuality();
  }, []);

  const loadQuality = async () => {
    setLoading(true);
    try {
      const response = await getClusteringQuality();
      setQuality(response?.data || null);
    } catch (error) {
      console.error('Failed to load clustering quality:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <div className="animate-pulse space-y-4">
          <div className="h-4 bg-gray-200 rounded w-1/3"></div>
          <div className="h-8 bg-gray-200 rounded"></div>
        </div>
      </div>
    );
  }

  if (!quality || quality.error) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Clustering Quality</h3>
        <p className="text-gray-600 text-sm">
          {quality?.error || 'No clustering data available. Run clustering first.'}
        </p>
      </div>
    );
  }

  const metrics = quality.quality_metrics || {};
  const compass = quality.competitive_comparison?.compass || {};
  const canny = quality.competitive_comparison?.canny_autopilot || {};

  // Calculate improvement vs Canny
  const improvement = compass.accuracy - canny.accuracy;

  return (
    <div className="bg-white rounded-lg shadow p-6">
      {/* Header */}
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Clustering Quality</h3>
          <p className="text-sm text-gray-600">{quality.current_algorithm}</p>
        </div>
        <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-green-100 text-green-800">
          {compass.rating}
        </span>
      </div>

      {/* Main Metrics */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="text-center">
          <div className="text-3xl font-bold text-primary-600">
            {compass.accuracy}%
          </div>
          <div className="text-sm text-gray-600 mt-1">Accuracy</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-primary-600">
            {compass.coverage}%
          </div>
          <div className="text-sm text-gray-600 mt-1">Coverage</div>
        </div>
        <div className="text-center">
          <div className="text-3xl font-bold text-primary-600">
            {metrics.num_clusters || 0}
          </div>
          <div className="text-sm text-gray-600 mt-1">Clusters</div>
        </div>
      </div>

      {/* Competitive Comparison */}
      <div className="border-t border-gray-200 pt-4">
        <h4 className="text-sm font-semibold text-gray-900 mb-3">Competitive Advantage</h4>

        <div className="space-y-3">
          {/* Compass (Us) */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">🏆</span>
              <div>
                <div className="font-medium text-gray-900">Compass (BERTopic)</div>
                <div className="text-xs text-gray-500">State-of-the-art NLP</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-green-600">{compass.accuracy}%</div>
              <div className="text-xs text-gray-500">Fully automatic</div>
            </div>
          </div>

          {/* Canny */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">⚠️</span>
              <div>
                <div className="font-medium text-gray-900">Canny Autopilot</div>
                <div className="text-xs text-gray-500">Users complain</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-orange-600">{canny.accuracy}%</div>
              <div className="text-xs text-gray-500">{canny.rating}</div>
            </div>
          </div>

          {/* Productboard */}
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <span className="text-2xl">🐌</span>
              <div>
                <div className="font-medium text-gray-900">Productboard</div>
                <div className="text-xs text-gray-500">Manual categorization</div>
              </div>
            </div>
            <div className="text-right">
              <div className="font-bold text-gray-600">100%</div>
              <div className="text-xs text-gray-500">60+ minutes</div>
            </div>
          </div>
        </div>

        {/* Improvement Badge */}
        {improvement > 0 && (
          <div className="mt-4 p-3 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium text-green-800">
                Better than competitors
              </span>
              <span className="text-lg font-bold text-green-600">
                +{improvement.toFixed(0)}%
              </span>
            </div>
            <p className="text-xs text-green-700 mt-1">
              {improvement.toFixed(0)}% more accurate than Canny Autopilot
            </p>
          </div>
        )}
      </div>

      {/* Technical Details (Expandable) */}
      {metrics.silhouette_score && (
        <details className="mt-4 text-sm">
          <summary className="cursor-pointer text-gray-600 hover:text-gray-900 font-medium">
            Technical Details
          </summary>
          <div className="mt-2 space-y-1 text-gray-600 pl-4">
            <div>Silhouette Score: {metrics.silhouette_score.toFixed(3)}</div>
            <div>Avg Cluster Size: {metrics.avg_cluster_size?.toFixed(1)}</div>
            <div>Outliers: {metrics.outliers || 0} ({metrics.outlier_percentage?.toFixed(1)}%)</div>
          </div>
        </details>
      )}
    </div>
  );
}

export default ClusteringStats;
