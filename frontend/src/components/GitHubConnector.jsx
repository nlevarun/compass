import { useState, useEffect } from 'react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function GitHubConnector() {
  const [clientId, setClientId] = useState('');
  const [clientSecret, setClientSecret] = useState('');
  const [connected, setConnected] = useState(false);
  const [syncing, setSyncing] = useState(false);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState(null);
  const [error, setError] = useState(null);
  const [repositories, setRepositories] = useState([]);
  const [selectedRepos, setSelectedRepos] = useState([]);
  const [labels, setLabels] = useState('');
  const [showRepoSelection, setShowRepoSelection] = useState(false);

  useEffect(() => {
    loadStatus();
    handleOAuthCallback();
  }, []);

  const loadStatus = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/connectors/github/status`);
      setStatus(response.data);
      setConnected(response.data.connected);
      if (response.data.repositories) {
        setSelectedRepos(response.data.repositories);
      }
      if (response.data.labels) {
        setLabels(response.data.labels.join(', '));
      }
    } catch (error) {
      console.error('Failed to load GitHub status:', error);
    }
  };

  const handleOAuthCallback = async () => {
    const params = new URLSearchParams(window.location.search);
    const code = params.get('code');

    if (code) {
      setLoading(true);
      setError(null);

      try {
        // Get client credentials from local storage or prompt user
        const savedClientId = localStorage.getItem('github_client_id');
        const savedClientSecret = localStorage.getItem('github_client_secret');

        if (!savedClientId || !savedClientSecret) {
          setError('Client ID and Secret not found. Please enter them below.');
          setLoading(false);
          // Remove code from URL
          window.history.replaceState({}, document.title, window.location.pathname);
          return;
        }

        await axios.post(`${API_URL}/api/auth/github/callback`, {
          client_id: savedClientId,
          client_secret: savedClientSecret,
          code
        });

        setConnected(true);
        setError(null);

        // Remove code from URL
        window.history.replaceState({}, document.title, window.location.pathname);

        // Load repositories
        await loadRepositories();
        setShowRepoSelection(true);

        alert('GitHub connected successfully! Now select repositories to monitor.');
      } catch (error) {
        setError(error.response?.data?.detail || 'OAuth callback failed: ' + error.message);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleConnect = async () => {
    if (!clientId || !clientSecret) {
      setError('Please enter both Client ID and Client Secret');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Save credentials to local storage
      localStorage.setItem('github_client_id', clientId);
      localStorage.setItem('github_client_secret', clientSecret);

      // Get OAuth URL
      const response = await axios.get(`${API_URL}/api/auth/github`, {
        params: { client_id: clientId }
      });

      // Redirect to GitHub OAuth
      window.location.href = response.data.oauth_url;
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to start OAuth flow');
      setLoading(false);
    }
  };

  const loadRepositories = async () => {
    try {
      const response = await axios.get(`${API_URL}/api/connectors/github/repositories`);
      setRepositories(response.data.repositories);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to load repositories');
    }
  };

  const handleConfigureRepos = async () => {
    if (selectedRepos.length === 0) {
      setError('Please select at least one repository');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const labelList = labels.split(',').map(l => l.trim()).filter(l => l);

      await axios.post(`${API_URL}/api/connectors/github/configure`, {
        repository_full_names: selectedRepos,
        labels: labelList
      });

      setShowRepoSelection(false);
      await loadStatus();

      alert('Repositories configured! Click "Sync Now" to import issues.');
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to configure repositories');
    } finally {
      setLoading(false);
    }
  };

  const handleSync = async () => {
    setSyncing(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/api/connectors/github/sync`, {
        limit: 100
      });

      alert(`Synced ${response.data.synced} issues and comments from GitHub!`);
      await loadStatus();
    } catch (error) {
      setError(error.response?.data?.detail || 'Sync failed: ' + error.message);
    } finally {
      setSyncing(false);
    }
  };

  const toggleRepo = (repoFullName) => {
    if (selectedRepos.includes(repoFullName)) {
      setSelectedRepos(selectedRepos.filter(r => r !== repoFullName));
    } else {
      setSelectedRepos([...selectedRepos, repoFullName]);
    }
  };

  return (
    <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl">
      <div className="flex items-center mb-4">
        <svg className="w-8 h-8 mr-3" viewBox="0 0 24 24" fill="none">
          <path fillRule="evenodd" clipRule="evenodd" d="M12 2C6.477 2 2 6.477 2 12c0 4.42 2.865 8.17 6.839 9.49.5.092.682-.217.682-.482 0-.237-.008-.866-.013-1.7-2.782.603-3.369-1.34-3.369-1.34-.454-1.156-1.11-1.463-1.11-1.463-.908-.62.069-.608.069-.608 1.003.07 1.531 1.03 1.531 1.03.892 1.529 2.341 1.087 2.91.831.092-.646.35-1.086.636-1.336-2.22-.253-4.555-1.11-4.555-4.943 0-1.091.39-1.984 1.029-2.683-.103-.253-.446-1.27.098-2.647 0 0 .84-.269 2.75 1.025A9.578 9.578 0 0112 6.836c.85.004 1.705.114 2.504.336 1.909-1.294 2.747-1.025 2.747-1.025.546 1.377.203 2.394.1 2.647.64.699 1.028 1.592 1.028 2.683 0 3.842-2.339 4.687-4.566 4.935.359.309.678.919.678 1.852 0 1.336-.012 2.415-.012 2.743 0 .267.18.578.688.48C19.137 20.167 22 16.418 22 12c0-5.523-4.477-10-10-10z" fill="#24292E"/>
        </svg>
        <div>
          <h2 className="text-xl font-semibold text-gray-900">GitHub Connector</h2>
          <p className="text-sm text-gray-500">Import issues and comments as customer feedback</p>
        </div>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
          {error}
        </div>
      )}

      {loading && (
        <div className="bg-blue-50 border border-blue-200 text-blue-700 px-4 py-3 rounded mb-4">
          Processing OAuth flow...
        </div>
      )}

      {!connected && !showRepoSelection ? (
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              GitHub OAuth App Client ID
            </label>
            <input
              type="text"
              placeholder="Iv1.abc123..."
              value={clientId}
              onChange={(e) => setClientId(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Client Secret
            </label>
            <input
              type="password"
              placeholder="..."
              value={clientSecret}
              onChange={(e) => setClientSecret(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleConnect}
              disabled={!clientId || !clientSecret || loading}
              className="flex-1 px-4 py-2 bg-gray-900 text-white rounded-lg hover:bg-gray-800 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Connecting...' : 'Connect with GitHub'}
            </button>
            <a
              href="https://github.com/settings/developers"
              target="_blank"
              rel="noopener noreferrer"
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
            >
              Create OAuth App →
            </a>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h3 className="font-medium text-blue-900 mb-2">Setup Instructions</h3>
            <ol className="text-sm text-blue-800 space-y-1 list-decimal list-inside">
              <li>Go to <a href="https://github.com/settings/developers" target="_blank" rel="noopener noreferrer" className="underline">GitHub Developer Settings</a></li>
              <li>Click "New OAuth App"</li>
              <li>Application name: "Compass Feedback"</li>
              <li>Homepage URL: <code className="bg-blue-100 px-1 rounded">http://localhost:3000</code></li>
              <li>Authorization callback URL: <code className="bg-blue-100 px-1 rounded">http://localhost:3000/oauth/github/callback</code></li>
              <li>Click "Register application"</li>
              <li>Copy the Client ID and generate a Client Secret</li>
              <li>Paste them above and click "Connect with GitHub"</li>
            </ol>
          </div>
        </div>
      ) : showRepoSelection ? (
        <div className="space-y-4">
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-800">
              Select repositories to monitor for customer feedback
            </p>
          </div>

          {repositories.length > 0 ? (
            <div className="border border-gray-200 rounded-lg max-h-96 overflow-y-auto">
              <div className="divide-y divide-gray-200">
                {repositories.map((repo) => (
                  <label
                    key={repo.id}
                    className="flex items-center p-4 hover:bg-gray-50 cursor-pointer"
                  >
                    <input
                      type="checkbox"
                      checked={selectedRepos.includes(repo.full_name)}
                      onChange={() => toggleRepo(repo.full_name)}
                      className="w-4 h-4 text-primary-600 border-gray-300 rounded focus:ring-primary-500"
                    />
                    <div className="ml-3 flex-1">
                      <div className="font-medium text-gray-900">{repo.full_name}</div>
                      {repo.description && (
                        <div className="text-sm text-gray-500">{repo.description}</div>
                      )}
                      <div className="flex items-center mt-1 space-x-3 text-xs text-gray-500">
                        <span>{repo.private ? '🔒 Private' : '🌐 Public'}</span>
                        <span>{repo.open_issues_count} open issues</span>
                      </div>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          ) : (
            <div className="text-center py-8 text-gray-500">
              Loading repositories...
            </div>
          )}

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Filter by Labels (optional)
            </label>
            <input
              type="text"
              placeholder="bug, feature-request, customer-feedback"
              value={labels}
              onChange={(e) => setLabels(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <p className="text-xs text-gray-500 mt-1">
              Comma-separated. Leave empty to import all issues.
            </p>
          </div>

          <div className="flex space-x-3">
            <button
              onClick={handleConfigureRepos}
              disabled={selectedRepos.length === 0 || loading}
              className="flex-1 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed font-medium"
            >
              {loading ? 'Configuring...' : `Configure ${selectedRepos.length} Repositories`}
            </button>
            <button
              onClick={() => setShowRepoSelection(false)}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <div className="space-y-4">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-center">
              <svg className="w-5 h-5 text-green-600 mr-2" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="font-medium text-green-900">Connected to GitHub</span>
            </div>
          </div>

          {status && (
            <div className="space-y-3">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-2">Monitoring Repositories</p>
                <div className="space-y-1">
                  {status.repositories.map((repo, idx) => (
                    <div key={idx} className="font-mono text-sm">{repo}</div>
                  ))}
                </div>
              </div>

              {status.labels.length > 0 && (
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 mb-2">Filtering by Labels</p>
                  <div className="flex flex-wrap gap-2">
                    {status.labels.map((label, idx) => (
                      <span key={idx} className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-xs">
                        {label}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div className="grid grid-cols-2 gap-4">
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Issues Imported</p>
                  <p className="text-2xl font-bold text-primary-600 mt-1">{status.feedback_count}</p>
                </div>
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500">Last Synced</p>
                  <p className="text-sm font-medium mt-1">
                    {status.last_synced ? new Date(status.last_synced).toLocaleString() : 'Never'}
                  </p>
                </div>
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
                setShowRepoSelection(true);
                loadRepositories();
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Change Repos
            </button>
            <button
              onClick={() => {
                setConnected(false);
                setClientId('');
                setClientSecret('');
                setStatus(null);
                setSelectedRepos([]);
                localStorage.removeItem('github_client_id');
                localStorage.removeItem('github_client_secret');
              }}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Disconnect
            </button>
          </div>

          <div className="bg-gray-50 rounded-lg p-4">
            <h3 className="font-medium text-gray-900 mb-2">What gets imported</h3>
            <ul className="text-sm text-gray-700 space-y-1 list-disc list-inside">
              <li>Issues (title + description) as feedback</li>
              <li>Issue comments as additional feedback</li>
              <li>Reactions (+1, heart, hooray, rocket) as vote counts</li>
              <li>Labels for categorization</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

export default GitHubConnector;
