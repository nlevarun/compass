import { useState } from 'react';
import FeedbackInbox from './components/FeedbackInbox';
import ClusterView from './components/ClusterView';
import RoadmapDashboard from './components/RoadmapDashboard';
import Dashboard from './components/Dashboard';

function App() {
  const [activeTab, setActiveTab] = useState('dashboard');

  const tabs = [
    { id: 'dashboard', name: 'Dashboard', icon: '📊' },
    { id: 'feedback', name: 'Feedback Inbox', icon: '📥' },
    { id: 'clusters', name: 'Clusters', icon: '🔗' },
    { id: 'roadmap', name: 'Roadmap', icon: '🗺️' },
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div className="flex items-center">
              <div className="text-3xl mr-3">🧭</div>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">Compass</h1>
                <p className="text-sm text-gray-500">Customer Feedback Intelligence</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Built with ❤️ by Varun
              </span>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="flex space-x-8 -mb-px">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`
                  flex items-center px-1 py-4 border-b-2 font-medium text-sm
                  ${activeTab === tab.id
                    ? 'border-primary-500 text-primary-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }
                `}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'dashboard' && <Dashboard />}
        {activeTab === 'feedback' && <FeedbackInbox />}
        {activeTab === 'clusters' && <ClusterView />}
        {activeTab === 'roadmap' && <RoadmapDashboard />}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            Compass v1.0 - Aggregates feedback from 8+ sources • NLP clustering • Data-driven prioritization
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
