import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function SlackConnector() {
  const [token, setToken] = useState('');
  const [channelId, setChannelId] = useState('');
  const [connected, setConnected] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [testing, setTesting] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [channels, setChannels] = useState([]);
  const [showChannelList, setShowChannelList] = useState(false);

  useEffect(() => {
    loadStatus();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/connectors/slack/status`);
      setStatus(response.data);
      setConnected(response.data.connected);
      if (response.data.channel_id) {
        setChannelId(response.data.channel_id);
      }
    } catch (error) {
      console.error('Failed to load Slack status:', error);
    }
  };

  const handleTest = async () => {
    if (!token) {
      setError('Please enter a Slack bot token');
      return;
    }

    setTesting(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/connectors/slack/test`, {
        token,
        channel_id: channelId || ''
      });

      setChannels(response.data.channels);
      setShowChannelList(true);
      setError(null);
    } catch (error) {
      setError(error.response?.data?.detail || 'Connection test failed. Check your token.');
    } finally {
      setTesting(false);
    }
  };

  const handleConnect = async () => {
    if (!token || !channelId) {
      setError('Please enter both token and channel ID');
      return;
    }

    setTesting(true);
    setError(null);

    try {
      await axios.post(`${API_URL}/api/connectors/slack/connect`, {
        token,
        channel_id: channelId
      });

      setConnected(true);
      setError(null);
      setShowChannelList(false);
      await loadStatus();

      // Show success message
      alert('Slack connected! Click "Sync Now" to import messages.');
    } catch (error) {
      setError(error.response?.data?.detail || 'Connection failed. Check your token and channel ID.');
    } finally {
      setTesting(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/connectors/slack/sync`, {
        limit: 100
      });

      alert(`Synced ${response.data.synced} new messages from Slack!`);
      await loadStatus();
    } catch (error) {
      setError(error.response?.data?.detail || 'Sync failed: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  const selectChannel = (channel) => {
    setChannelId(channel.id);
    setShowChannelList(false);
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl">
      <div className="flex items-center mb-4">
        <svg className="w-8 h-8 mr-3" viewBox="0 0 24 24" fill="none">
          <path d="M5.042 15.165a2.528 2.528 0 0 1-2.52 2.523A2.528 2.528 0 0 1 0 15.165a2.527 2.527 0 0 1 2.522-2.52h2.52v2.52zM6.313 15.165a2.527 2.527 0 0 1 2.521-2.52 2.527 2.527 0 0 1 2.521 2.52v6.313A2.528 2.528 0 0 1 8.834 24a2.528 2.528 0 0 1-2.521-2.522v-6.313zM8.834 5.042a2.528 2.528 0 0 1-2.521-2.52A2.528 2.528 0 0 1 8.834 0a2.528 2.528 0 0 1 2.521 2.522v2.52H8.834zM8.834 6.313a2.528 2.528 0 0 1 2.521 2.521 2.528 2.528 0 0 1-2.521 2.521H2.522A2.528 2.528 0 0 1 0 8.834a2.528 2.528 0 0 1 2.522-2.521h6.312zM18.956 8.834a2.528 2.528 0 0 1 2.522-2.521A2.528 2.528 0 0 1 24 8.834a2.528 2.528 0 0 1-2.522 2.521h-2.522V8.834zM17.688 8.834a2.528 2.528 0 0 1-2.523 2.521 2.527 2.527 0 0 1-2.52-2.521V2.522A2.527 2.527 0 0 1 15.165 0a2.528 2.528 0 0 1 2.523 2.522v6.312zM15.165 18.956a2.528 2.528 0 0 1 2.523 2.522A2.528 2.528 0 0 1 15.165 24a2.527 2.527 0 0 1-2.52-2.522v-2.522h2.52zM15.165 17.688a2.527 2.527 0 0 1-2.52-2.523 2.526 2.526 0 0 1 2.52-2.52h6.313A2.527 2.527 0 0 1 24 15.165a2.528 2.528 0 0 1-2.522 2.523h-6.313z" fill="#E01E5A"/>
        </svg>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">Slack Connector</h2>
          <p className="text-sm text-gray-500">Import customer feedback from Slack channels</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {!connected ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Slack Bot Token
            </label>
            <input
              type="text"
              placeholder="xoxb-..."
              value={token}
              onChange={(e) => setToken(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Get this from your Slack app's OAuth & Permissions page
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Channel ID
            </label>
            <div className="flex space-x-2">
              <input
                type="text"
                placeholder="C12345..."
                value={channelId}
                onChange={(e) => setChannelId(e.target.value)}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
              />
              <button
                onClick={handleTest}
                disabled={!token || testing}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 disabled:opacity-50"
              >
                {testing ? 'Testing...' : 'Browse Channels'}
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Right-click channel in Slack → View channel details → copy ID at bottom
            </p>
          </div>

          {showChannelList && channels.length > 0 && (
            <div className="border border-gray-200 rounded-lg p-4 max-h-64 overflow-y-auto">
              <h3 className="font-medium text-gray-900 mb-2">Available Channels</h3>
              <div className="space-y-2">
                {channels.map((channel) => (
                  <button
                    key={channel.id}
                    onClick={() => selectChannel(channel)}
                    className="w-full text-left px-3 py-2 hover:bg-gray-50 rounded flex items-center justify-between"
                  >
                    <span className="font-mono text-sm">
                      #{channel.name}
                    </span>
                    <span className="text-xs text-gray-500">
                      {channel.is_member ? '✓ Member' : 'Not joined'}
                    </span>
                  </button>
                ))}
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={handleConnect}
              disabled={!token || !channelId || testing}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {testing ? 'Connecting...' : 'Connect Slack'}
            </button>
            <a
              href="https://api.slack.com/apps"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Create Slack App →
            </a>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Setup Instructions</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Go to <a href="https://api.slack.com/apps" target="_blank" rel="noopener noreferrer" className="underline">api.slack.com/apps</a></li>
              <li>Click "Create New App" → "From scratch"</li>
              <li>Name it "Compass Feedback" and select your workspace</li>
              <li>Go to "OAuth & Permissions"</li>
              <li>Add these Bot Token Scopes: <code className="bg-blue-100 px-1 rounded">channels:history</code>, <code className="bg-blue-100 px-1 rounded">channels:read</code></li>
              <li>Click "Install to Workspace"</li>
              <li>Copy the "Bot User OAuth Token" (starts with xoxb-)</li>
              <li>Paste it above and connect!</li>
            </ol>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="font-medium text-green-900">Connected to Slack</span>
            </div>
          </div>

          {status && (
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Channel ID</p>
                <p className="font-mono text-sm font-medium mt-1">{status.channel_id}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Messages Synced</p>
                <p className="text-2xl font-bold text-primary-600 mt-1">{status.feedback_count}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500">Last Synced</p>
                <p className="text-sm font-medium mt-1">
                  {status.last_synced ? new Date(status.last_synced).toLocaleString() : 'Never'}
                </p>
              </div>
            </div>
          )}

          <div className="flex space-x-3">
            <button
              onClick={handleSync}
              disabled={syncing}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 font-medium"
            >
              {syncing ? 'Syncing...' : 'Sync Now'}
            </button>
            <button
              onClick={() => {
                setConnected(false);
                setToken('');
                setChannelId('');
                setStatus(null);
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Disconnect
            </button>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">How to test</h3>
            <ol className="text-sm text-gray-700 space-y-1 list-decimal list-inside">
              <li>Go to your Slack channel</li>
              <li>Post a message like: "We need better analytics"</li>
              <li>Click "Sync Now" above</li>
              <li>Go to the Feedback tab to see your message!</li>
            </ol>
          </div>
        </div>
      )}
    </div>
  );
}

export default SlackConnector;
