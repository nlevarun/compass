import { useState, useEffect } from 'react';
import FeedbackInbox from './components/FeedbackInbox';
import ClusterView from './components/ClusterView';
import RoadmapDashboard from './components/RoadmapDashboard';
import Dashboard from './components/Dashboard';
import PriorityAnalysis from './components/PriorityAnalysis';
import OfflineBanner from './components/OfflineBanner';
import InstallPrompt from './components/InstallPrompt';
import Toast from './components/Toast';
import websocketService from './services/websocket';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [toasts, setToasts] = useState([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Connect to WebSocket
    websocketService.connect();

    // Listen for connection status
    const unsubscribe = websocketService.subscribe('connection', (data) => {
      setIsConnected(data.connected);
    });

    return () => {
      unsubscribe();
      websocketService.disconnect();
    };
  }, []);

  const showToast = (message, type = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => {
      setToasts(prev => prev.filter(t => t.id !== id));
    }, 5000);
  };

  const tabs = [
    { id: 'dashboard', name: 'Overview' },
    { id: 'feedback', name: 'Feedback' },
    { id: 'clusters', name: 'Insights' },
    { id: 'roadmap', name: 'Roadmap' },
    { id: 'priority', name: 'Priority Analysis' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Offline Banner */}
      <OfflineBanner />

      {/* Install Prompt */}
      <InstallPrompt />

      {/* Toasts */}
      <div className="fixed top-4 right-4 z-50 space-y-2">
        {toasts.map(toast => (
          <Toast key={toast.id} message={toast.message} type={toast.type} />
        ))}
      </div>

      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6">
          <div className="flex items-center justify-between h-16">
            {/* Logo and Title */}
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <div>
                <h1 className="text-lg font-semibold text-gray-900">Compass</h1>
                <p className="text-xs text-gray-500">Feedback Intelligence</p>
              </div>
            </div>

            {/* Navigation Tabs */}
            <nav className="flex space-x-1">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`
                    px-4 py-2 text-sm font-medium rounded-lg transition-colors
                    ${activeTab === tab.id
                      ? 'bg-gray-100 text-gray-900'
                      : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                    }
                  `}
                >
                  {tab.name}
                </button>
              ))}
            </nav>

            {/* User Menu */}
            <div className="flex items-center space-x-3">
              {/* Connection Status */}
              <div className="flex items-center space-x-2">
                <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
                <span className="text-xs text-gray-500">{isConnected ? 'Connected' : 'Offline'}</span>
              </div>

              <button className="p-2 text-gray-400 hover:text-gray-600 rounded-lg hover:bg-gray-50">
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" />
                </svg>
              </button>
              <div className="w-8 h-8 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-medium">
                VV
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        {activeTab === 'dashboard' && <Dashboard showToast={showToast} />}
        {activeTab === 'feedback' && <FeedbackInbox showToast={showToast} />}
        {activeTab === 'clusters' && <ClusterView showToast={showToast} />}
        {activeTab === 'roadmap' && <RoadmapDashboard showToast={showToast} />}
        {activeTab === 'priority' && <PriorityAnalysis showToast={showToast} />}
      </main>
    </div>
  );
}

export default App;
