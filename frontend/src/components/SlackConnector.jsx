import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function SlackConnector() {
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(true);
  const [syncing, setSyncing] = useState(false);
  const [error, setError] = useState(null);
  const [workspaces, setWorkspaces] = useState([]);
  const [selectedWorkspace, setSelectedWorkspace] = useState(null);
  const [channels, setChannels] = useState([]);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [showChannels, setShowChannels] = useState(false);

  useEffect(() => {
    loadStatus();

    // Listen for OAuth callback messages
    const handleMessage = (event) => {
      if (event.data.type === 'slack_oauth_success') {
        console.log('Slack OAuth successful:', event.data);
        loadStatus();
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, []);

  const loadStatus = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/auth/slack/status`);
      setStatus(response.data);
      setWorkspaces(response.data.workspaces || []);

      // Auto-select first workspace if available
      if (response.data.workspaces && response.data.workspaces.length > 0) {
        setSelectedWorkspace(response.data.workspaces[0]);
      }

      setError(null);
    } catch (error) {
      console.error('Failed to load Slack status:', error);
      setError('Failed to load Slack status');
    } finally {
      setLoading(false);
    }
  };

  const handleConnectSlack = () => {
    // Check if OAuth is configured
    if (status && !status.oauth_configured) {
      setError('Slack OAuth not configured. Please set SLACK_CLIENT_ID and SLACK_CLIENT_SECRET environment variables.');
      return;
    }

    // Open OAuth flow in popup
    const width = 600;
    const height = 700;
    const left = window.screenX + (window.outerWidth - width) / 2;
    const top = window.screenY + (window.outerHeight - height) / 2;

    const popup = window.open(
      `${API_URL}/api/auth/slack/connect`,
      'Slack OAuth',
      `width=${width},height=${height},left=${left},top=${top}`
    );

    // Check if popup was blocked
    if (!popup || popup.closed || typeof popup.closed === 'undefined') {
      setError('Popup blocked. Please allow popups for this site.');
    }
  };

  const handleDisconnect = async (sourceId) => {
    if (!confirm('Are you sure you want to disconnect this Slack workspace?')) {
      return;
    }

    try {
      await axios.post(`${API_URL}/api/auth/slack/disconnect/${sourceId}`);
      await loadStatus();
      setSelectedWorkspace(null);
      setChannels([]);
      setShowChannels(false);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to disconnect');
    }
  };

  const handleLoadChannels = async (workspace) => {
    try {
      setLoading(true);
      const response = await axios.get(`${API_URL}/api/auth/slack/channels/${workspace.source_id}`);
      setChannels(response.data.channels || []);
      setShowChannels(true);
      setError(null);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load channels');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    if (!selectedWorkspace || !selectedChannel) {
      setError('Please select a workspace and channel');
      return;
    }

    try {
      setSyncing(true);
      setError(null);

      const response = await axios.post(
        `${API_URL}/api/auth/slack/sync/${selectedWorkspace.source_id}?channel_id=${selectedChannel.id}&limit=100`
      );

      alert(`✓ Synced ${response.data.synced} new messages from #${selectedChannel.name}!`);
      await loadStatus();
    } catch (error) {
      setError(error.response?.data?.detail || 'Sync failed: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  if (loading && !status) {
    return (
      <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl">
        <div className="animate-pulse">
          <div className="h-8 bg-gray-200 rounded w-1/3 mb-4"></div>
          <div className="h-4 bg-gray-200 rounded w-2/3"></div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl">
      <div className="flex items-center mb-4">
        <svg className="w-8 h-8 mr-3" viewBox="0 0 24 24" fill="none">
          <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" fill="#E01E5A"/>
        </svg>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Slack Integration</h2>
          <p className="text-sm text-gray-500">Connect your Slack workspace with one click</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!status?.oauth_configured && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-4">
          <h3 className="font-medium text-yellow-900 mb-2">OAuth Not Configured</h3>
          <p className="text-sm text-yellow-800 mb-3">
            To use Slack OAuth, you need to set up a Slack app and configure environment variables.
          </p>
          <ol className="text-sm text-yellow-800 space-y-2 list-decimal list-inside">
            <li>Go to <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="underline">api.slack.com/apps</a></li>
            <li>Click "Create New App" → "From scratch"</li>
            <li>Name it "Compass" and select your workspace</li>
            <li>Go to "OAuth & Permissions" and add these scopes:
              <ul className="ml-6 mt-1 space-y-1">
                <li>• <code className="bg-yellow-100 px-1 rounded">channels:read</code></li>
                <li>• <code className="bg-yellow-100 px-1 rounded">channels:history</code></li>
                <li>• <code className="bg-yellow-100 px-1 rounded">groups:read</code></li>
                <li>• <code className="bg-yellow-100 px-1 rounded">groups:history</code></li>
                <li>• <code className="bg-yellow-100 px-1 rounded">users:read</code></li>
                <li>• <code className="bg-yellow-100 px-1 rounded">users:read.email</code></li>
              </ul>
            </li>
            <li>Add redirect URL: <code className="bg-yellow-100 px-1 rounded">http://localhost:8000/api/auth/slack/callback</code></li>
            <li>Copy "Client ID" and "Client Secret" from "Basic Information"</li>
            <li>Set environment variables:
              <pre className="bg-yellow-100 p-2 rounded mt-2 text-xs overflow-x-auto">
                export SLACK_CLIENT_ID="your_client_id"{'\n'}
                export SLACK_CLIENT_SECRET="your_client_secret"
              </pre>
            </li>
            <li>Restart the backend server</li>
          </ol>
        </div>
      )}

      {workspaces.length === 0 ? (
        <div className="space-y-4">
          <div className="bg-gray-50 rounded-lg p-6 text-center">
            <svg className="w-12 h-12 text-gray-400 mx-auto mb-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Slack Workspace Connected</h3>
            <p className="text-gray-600 mb-4">Connect your Slack workspace to start importing customer feedback</p>
            <button
              onClick={handleConnectSlack}
              disabled={!status?.oauth_configured}
              className="px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium inline-flex items-center"
            >
              <svg className="w-5 h-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52z"/>
              </svg>
              Connect Slack Workspace
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          {/* Connected Workspaces */}
          <div className="space-y-3">
            {workspaces.map((workspace) => (
              <div key={workspace.source_id} className="border border-gray-200 rounded-lg p-4">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center">
                    <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-pink-500 rounded-lg flex items-center justify-center text-white font-bold mr-3">
                      {workspace.team_name.charAt(0).toUpperCase()}
                    </div>
                    <div>
                      <h3 className="font-medium text-gray-900">{workspace.team_name}</h3>
                      <p className="text-xs text-gray-500">
                        Connected {new Date(workspace.connected_at).toLocaleDateString()}
                      </p>
                    </div>
                  </div>
                  <button
                    onClick={() => handleDisconnect(workspace.source_id)}
                    className="text-sm text-red-600 hover:text-red-700"
                  >
                    Disconnect
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-3 mb-3">
                  <div className="bg-gray-50 rounded p-2">
                    <p className="text-xs text-gray-500">Messages Synced</p>
                    <p className="text-lg font-bold text-primary-600">{workspace.feedback_count}</p>
                  </div>
                  <div className="bg-gray-50 rounded p-2">
                    <p className="text-xs text-gray-500">Last Synced</p>
                    <p className="text-sm font-medium">
                      {workspace.last_synced_at
                        ? new Date(workspace.last_synced_at).toLocaleTimeString()
                        : 'Never'}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => handleLoadChannels(workspace)}
                  disabled={loading}
                  className="w-full px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50 font-medium"
                >
                  {loading ? 'Loading...' : 'Select Channel to Sync'}
                </button>

                {showChannels && selectedWorkspace?.source_id === workspace.source_id && (
                  <div className="mt-3 border-t pt-3">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Choose a channel:
                    </label>
                    <div className="max-h-48 overflow-y-auto space-y-1 mb-3">
                      {channels.map((channel) => (
                        <button
                          key={channel.id}
                          onClick={() => setSelectedChannel(channel)}
                          className={`w-full text-left px-3 py-2 rounded flex items-center justify-between ${
                            selectedChannel?.id === channel.id
                              ? 'bg-primary-100 border border-primary-300'
                              : 'bg-gray-50 hover:bg-gray-100'
                          }`}
                        >
                          <span className="font-mono text-sm">
                            {channel.is_private ? '🔒' : '#'} {channel.name}
                          </span>
                          <span className="text-xs text-gray-500">
                            {channel.num_members} members
                          </span>
                        </button>
                      ))}
                    </div>

                    {selectedChannel && (
                      <button
                        onClick={handleSync}
                        disabled={syncing}
                        className="w-full px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
                      >
                        {syncing ? 'Syncing...' : `Sync #${selectedChannel.name}`}
                      </button>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* Add Another Workspace */}
          <button
            onClick={handleConnectSlack}
            disabled={!status?.oauth_configured}
            className="w-full px-4 py-2 border-2 border-dashed border-gray-300 text-gray-600 rounded-lg hover:border-primary-400 hover:text-primary-600 disabled:opacity-50 font-medium"
          >
            + Connect Another Workspace
          </button>

          {/* Help Section */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">How it works</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Click "Select Channel to Sync" to see available channels</li>
              <li>Choose a channel where customers give feedback</li>
              <li>Click "Sync" to import messages as feedback</li>
              <li>Visit the Feedback tab to see imported messages</li>
              <li>Run clustering to group similar feedback together</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}

export default SlackConnector;
