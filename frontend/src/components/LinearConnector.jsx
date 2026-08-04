import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function LinearConnector() {
  const [connected, setConnected] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [teams, setTeams] = useState([]);
  const [selectedTeamId, setSelectedTeamId] = useState('');
  const [showTeamList, setShowTeamList] = useState(false);

  useEffect(() => {
    loadStatus();
    // Check if returning from OAuth callback
    const params = new URLSearchParams(window.location.search);
    if (params.get('linear_connected') === 'true') {
      loadStatus();
      // Remove query param
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const loadStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/connectors/linear/status`);
      setStatus(response.data);
      setConnected(response.data.connected);

      if (response.data.connected && response.data.teams) {
        setTeams(response.data.teams);
      }
    } catch (error) {
      console.error('Failed to load Linear status:', error);
    }
  };

  const handleConnect = async () => {
    setError(null);

    try {
      // Get OAuth URL
      const response = await axios.get(`${API_URL}/api/auth/linear`);
      const authUrl = response.data.auth_url;

      // Open OAuth popup
      const width = 600;
      const height = 700;
      const left = window.screen.width / 2 - width / 2;
      const top = window.screen.height / 2 - height / 2;

      const popup = window.open(
        authUrl,
        'Linear OAuth',
        `width=${width},height=${height},left=${left},top=${top}`
      );

      // Poll for popup close or success
      const checkPopup = setInterval(() => {
        if (popup.closed) {
          clearInterval(checkPopup);
          // Reload status after popup closes
          setTimeout(() => loadStatus(), 500);
        }
      }, 500);

    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to initiate OAuth flow');
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/connectors/linear/sync`, {
        team_id: selectedTeamId || null,
        limit: 50
      });

      alert(`Synced ${response.data.new} new issues and updated ${response.data.updated} existing issues from Linear!`);
      await loadStatus();
      setShowTeamList(false);
    } catch (error) {
      setError(error.response?.data?.detail || 'Sync failed: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  const handleDisconnect = () => {
    // In production, call API to revoke token
    setConnected(false);
    setStatus(null);
    setTeams([]);
    setSelectedTeamId('');
  };

  const loadTeams = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/connectors/linear/teams`);
      setTeams(response.data.teams);
      setShowTeamList(true);
    } catch (error) {
      setError('Failed to load teams: ' + error.message);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl">
      <div className="flex items-center mb-4">
        <svg className="w-8 h-8 mr-3" viewBox="0 0 100 100" fill="none">
          <path
            d="M1.22541 61.5228c-.2225-1.7441 1.0415-3.3485 2.7855-3.5709l4.366-.5567c1.7441-.2224 3.3486 1.0415 3.571 2.7856l4.8722 38.1806c.2225 1.744-1.0415 3.3485-2.7855 3.5709l-4.366.5567c-1.7441.2224-3.3486-1.0415-3.571-2.7856L1.22541 61.5228ZM26.4499 57.9095c-.2225-1.7441 1.0415-3.3486 2.7855-3.571l4.366-.5566c1.7441-.2225 3.3486 1.0415 3.571 2.7855l4.8722 38.1806c.2225 1.744-1.0415 3.3486-2.7855 3.571l-4.366.5567c-1.7441.2224-3.3486-1.0415-3.571-2.7856l-4.8722-38.1806ZM51.6744 54.2962c-.2225-1.7441 1.0415-3.3486 2.7855-3.571l4.366-.5567c1.744-.2224 3.3486 1.0415 3.571 2.7856l4.8722 38.1806c.2225 1.744-1.0415 3.3486-2.7856 3.571l-4.366.5567c-1.744.2224-3.3485-1.0415-3.571-2.7856l-4.8721-38.1806ZM76.8989 50.6829c-.2225-1.7441 1.0415-3.3486 2.7856-3.571l4.366-.5567c1.744-.2225 3.3485 1.0415 3.571 2.7855l4.8721 38.1806c.2225 1.744-1.0415 3.3486-2.7855 3.571l-4.366.5567c-1.7441.2225-3.3486-1.0415-3.571-2.7855l-4.8722-38.1806Z"
            fill="#5E6AD2"
          />
        </svg>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Linear Connector</h2>
          <p className="text-sm text-gray-500">Sync issues and feedback from Linear</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!connected ? (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Connect Linear</h3>
            <p className="text-sm text-blue-800 mb-3">
              Authorize Compass to access your Linear workspace. We'll sync issues, comments, and feedback automatically.
            </p>
            <ul className="text-sm text-blue-800 space-y-1 list-disc list-inside mb-4">
              <li>Import issues as feedback</li>
              <li>Sync issue comments</li>
              <li>Two-way sync with roadmaps</li>
              <li>Automatic priority mapping</li>
            </ul>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleConnect}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 font-medium"
            >
              Connect with Linear
            </button>
            <a
              href="https://developers.linear.app/docs/oauth"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Learn More →
            </a>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">What permissions do we request?</h3>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li><strong>read</strong> - View your issues, comments, and teams</li>
              <li><strong>write</strong> - Create and update issues from Compass roadmap</li>
            </ul>
            <p className="text-xs text-gray-500 mt-2">
              You can revoke access anytime from your Linear workspace settings.
            </p>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="font-medium text-green-900">Connected to Linear</span>
            </div>
          </div>

          {status && status.user && (
            <div className="bg-gray-50 rounded-lg p-3">
              <p className="text-xs text-gray-500">Connected as</p>
              <p className="font-medium text-gray-900 mt-1">{status.user.name}</p>
              <p className="text-sm text-gray-600">{status.user.email}</p>
            </div>
          )}

          {status && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Teams</p>
                <p className="text-2xl font-bold text-primary-600 mt-1">{status.team_count || 0}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Issues Synced</p>
                <p className="text-2xl font-bold text-primary-600 mt-1">{status.feedback_count || 0}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Last Synced</p>
                <p className="text-sm font-medium mt-1">
                  {status.last_synced ? new Date(status.last_synced).toLocaleString() : 'Never'}
                </p>
              </div>
            </div>
          )}

          {teams && teams.length > 0 && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Select Team (Optional)
              </label>
              <select
                value={selectedTeamId}
                onChange={(e) => setSelectedTeamId(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              >
                <option value="">All Teams</option>
                {teams.map((team) => (
                  <option key={team.id} value={team.id}>
                    {team.name} ({team.key})
                  </option>
                ))}
              </select>
              <p className="text-xs text-gray-500 mt-1">
                Leave blank to sync issues from all teams you have access to
              </p>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={handleSync}
              disabled={syncing}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
            >
              {syncing ? 'Syncing...' : 'Sync Issues'}
            </button>
            <button
              onClick={loadTeams}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Refresh Teams
            </button>
            <button
              onClick={handleDisconnect}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Disconnect
            </button>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">How it works</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Click "Sync Issues" to import Linear issues as feedback</li>
              <li>Issue descriptions and comments become feedback items</li>
              <li>Feedback is automatically clustered by topic</li>
              <li>Create roadmap items and push back to Linear</li>
              <li>Two-way sync keeps everything in sync</li>
            </ol>
          </div>

          <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">Synced Data</h3>
            <div className="text-sm text-gray-700 space-y-1">
              <p><strong>From Linear:</strong> Issues, comments, labels, priorities, assignees</p>
              <p><strong>To Linear:</strong> Roadmap items as issues, feedback summaries</p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default LinearConnector;
