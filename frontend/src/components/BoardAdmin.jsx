import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function BoardAdmin() {
  const { slug } = useParams();
  const [board, setBoard] = useState(null);
  const [posts, setPosts] = useState([]);
  const [analytics, setAnalytics] = useState(null);
  const [adminEmail, setAdminEmail] = useState(localStorage.getItem('compass_admin_email') || '');
  const [activeTab, setActiveTab] = useState('posts'); // posts, analytics, settings

  useEffect(() => {
    if (adminEmail) {
      loadBoard();
      loadPosts();
      loadAnalytics();
    }
  }, [slug, adminEmail]);

  const loadBoard = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/public-boards/boards/${slug}`);
      if (res.ok) {
        const data = await res.json();
        setBoard(data);
      }
    } catch (error) {
      console.error('Error loading board:', error);
    }
  };

  const loadPosts = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/public-boards/boards/${slug}/posts?sort_by=recent`);
      if (res.ok) {
        const data = await res.json();
        setPosts(data);
      }
    } catch (error) {
      console.error('Error loading posts:', error);
    }
  };

  const loadAnalytics = async () => {
    try {
      const res = await fetch(`${API_BASE}/api/public-boards/boards/${slug}/analytics`);
      if (res.ok) {
        const data = await res.json();
        setAnalytics(data);
      }
    } catch (error) {
      console.error('Error loading analytics:', error);
    }
  };

  const updatePostStatus = async (postId, newStatus) => {
    try {
      const res = await fetch(`${API_BASE}/api/public-boards/posts/${postId}/status`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          status: newStatus,
          admin_email: adminEmail
        })
      });

      if (res.ok) {
        loadPosts();
      } else {
        const error = await res.json();
        alert(error.detail || 'Error updating status');
      }
    } catch (error) {
      console.error('Error updating status:', error);
    }
  };

  if (!adminEmail) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center p-4">
        <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Admin Login</h2>
          <p className="text-gray-600 mb-6">Enter your email to access the admin dashboard</p>
          <input
            type="email"
            placeholder="admin@company.com"
            className="w-full px-4 py-3 border border-gray-300 rounded-lg mb-4 focus:ring-2 focus:ring-indigo-500"
            onKeyDown={(e) => {
              if (e.key === 'Enter') {
                setAdminEmail(e.target.value);
                localStorage.setItem('compass_admin_email', e.target.value);
              }
            }}
          />
          <button
            onClick={() => {
              const email = document.querySelector('input[type="email"]').value;
              setAdminEmail(email);
              localStorage.setItem('compass_admin_email', email);
            }}
            className="w-full py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
          >
            Continue
          </button>
        </div>
      </div>
    );
  }

  if (!board) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">{board.title} - Admin</h1>
              <p className="text-sm text-gray-500 mt-1">
                <a href={`/boards/${board.slug}`} className="text-indigo-600 hover:text-indigo-700">
                  View Public Board →
                </a>
              </p>
            </div>
            <div className="text-sm text-gray-600">
              Logged in as: {adminEmail}
            </div>
          </div>

          {/* Tabs */}
          <div className="mt-6 flex space-x-4 border-b border-gray-200">
            <button
              onClick={() => setActiveTab('posts')}
              className={`pb-3 px-1 font-medium ${
                activeTab === 'posts'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Posts ({posts.length})
            </button>
            <button
              onClick={() => setActiveTab('analytics')}
              className={`pb-3 px-1 font-medium ${
                activeTab === 'analytics'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Analytics
            </button>
            <button
              onClick={() => setActiveTab('settings')}
              className={`pb-3 px-1 font-medium ${
                activeTab === 'settings'
                  ? 'text-indigo-600 border-b-2 border-indigo-600'
                  : 'text-gray-500 hover:text-gray-700'
              }`}
            >
              Settings
            </button>
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        {activeTab === 'posts' && (
          <PostsTab posts={posts} onStatusUpdate={updatePostStatus} />
        )}

        {activeTab === 'analytics' && analytics && (
          <AnalyticsTab analytics={analytics} />
        )}

        {activeTab === 'settings' && (
          <SettingsTab board={board} slug={slug} />
        )}
      </div>
    </div>
  );
}

function PostsTab({ posts, onStatusUpdate }) {
  const statusOptions = ['open', 'planned', 'in_progress', 'completed', 'closed'];

  const getStatusColor = (status) => {
    const colors = {
      open: 'bg-gray-100 text-gray-700',
      planned: 'bg-blue-100 text-blue-700',
      in_progress: 'bg-yellow-100 text-yellow-700',
      completed: 'bg-green-100 text-green-700',
      closed: 'bg-red-100 text-red-700'
    };
    return colors[status] || colors.open;
  };

  return (
    <div className="space-y-4">
      {posts.map((post) => (
        <div key={post.id} className="bg-white rounded-lg border border-gray-200 p-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-gray-900 mb-2">{post.title}</h3>
              {post.description && (
                <p className="text-gray-600 mb-3">{post.description}</p>
              )}
              <div className="flex items-center space-x-4 text-sm text-gray-500">
                <span>{post.vote_count} votes</span>
                <span>•</span>
                <span>Revenue Score: {post.revenue_weighted_score.toFixed(1)}</span>
                <span>•</span>
                <span>{post.comment_count} comments</span>
                <span>•</span>
                <span>by {post.author_name}</span>
              </div>
            </div>

            <div className="ml-6">
              <select
                value={post.status}
                onChange={(e) => onStatusUpdate(post.id, e.target.value)}
                className={`px-3 py-2 rounded-lg text-sm font-medium ${getStatusColor(post.status)}`}
              >
                {statusOptions.map((status) => (
                  <option key={status} value={status}>
                    {status.replace('_', ' ').toUpperCase()}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
      ))}

      {posts.length === 0 && (
        <div className="text-center py-12 bg-white rounded-lg">
          <p className="text-gray-500">No posts yet</p>
        </div>
      )}
    </div>
  );
}

function AnalyticsTab({ analytics }) {
  return (
    <div className="space-y-6">
      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Total Posts</div>
          <div className="text-3xl font-bold text-gray-900">{analytics.stats.total_posts}</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Total Votes</div>
          <div className="text-3xl font-bold text-gray-900">{analytics.stats.total_votes}</div>
        </div>
        <div className="bg-white p-6 rounded-lg border border-gray-200">
          <div className="text-sm text-gray-600 mb-1">Total Comments</div>
          <div className="text-3xl font-bold text-gray-900">{analytics.stats.total_comments}</div>
        </div>
      </div>

      {/* Top Posts */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Top Posts</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {analytics.top_posts.map((post, idx) => (
              <div key={post.id} className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="text-2xl font-bold text-gray-400">#{idx + 1}</div>
                  <div>
                    <div className="font-medium text-gray-900">{post.title}</div>
                    <div className="text-sm text-gray-500">
                      {post.votes} votes • Revenue Score: {post.revenue_score.toFixed(1)}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Top Voters */}
      <div className="bg-white rounded-lg border border-gray-200">
        <div className="p-6 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Top Voters by Revenue</h2>
          <p className="text-sm text-gray-500 mt-1">
            Showing customers with the highest revenue impact
          </p>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {analytics.top_voters.map((voter, idx) => (
              <div key={voter.email} className="flex items-center justify-between">
                <div className="flex items-center space-x-4">
                  <div className="text-lg font-bold text-gray-400">#{idx + 1}</div>
                  <div>
                    <div className="font-medium text-gray-900">{voter.name || voter.email}</div>
                    <div className="text-sm text-gray-500">{voter.email}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-semibold text-green-600">
                    ${voter.total_revenue.toLocaleString()}
                  </div>
                  <div className="text-sm text-gray-500">{voter.vote_count} votes</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

function SettingsTab({ board, slug }) {
  const embedCode = `<iframe
  src="${window.location.origin}/boards/${slug}"
  width="100%"
  height="800px"
  frameborder="0"
></iframe>`;

  const copyEmbedCode = () => {
    navigator.clipboard.writeText(embedCode);
    alert('Embed code copied to clipboard!');
  };

  return (
    <div className="space-y-6">
      {/* Board Info */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Board Information</h2>
        <div className="space-y-3">
          <div>
            <div className="text-sm text-gray-600">Public URL</div>
            <div className="font-mono text-sm text-indigo-600">
              {window.location.origin}/boards/{slug}
            </div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Slug</div>
            <div className="font-mono text-sm">{slug}</div>
          </div>
          <div>
            <div className="text-sm text-gray-600">Theme Color</div>
            <div className="flex items-center space-x-2">
              <div
                className="w-6 h-6 rounded"
                style={{ backgroundColor: board.theme_color }}
              />
              <span className="font-mono text-sm">{board.theme_color}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Embed Code */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Embed on Your Website</h2>
        <p className="text-sm text-gray-600 mb-4">
          Copy this code and paste it into your website to embed the feedback board
        </p>
        <div className="bg-gray-50 rounded-lg p-4 font-mono text-sm overflow-x-auto">
          <pre>{embedCode}</pre>
        </div>
        <button
          onClick={copyEmbedCode}
          className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
        >
          Copy Embed Code
        </button>
      </div>

      {/* Revenue Weighting Info */}
      <div className="bg-gradient-to-r from-yellow-50 to-yellow-100 rounded-lg border border-yellow-200 p-6">
        <div className="flex items-start space-x-3">
          <div className="text-2xl">💰</div>
          <div>
            <h3 className="font-semibold text-yellow-900 mb-2">
              Revenue-Weighted Voting is Active
            </h3>
            <p className="text-sm text-yellow-800 mb-3">
              This is Compass's unique feature! Votes from high-value customers automatically count more.
            </p>
            <ul className="text-sm text-yellow-800 space-y-1">
              <li>• Free users = 1 point per vote</li>
              <li>• $10k customer = ~2 points per vote</li>
              <li>• $100k customer = ~3 points per vote</li>
            </ul>
            <p className="text-sm text-yellow-800 mt-3">
              <strong>Note:</strong> Revenue data can be set via the API when users vote, or manually updated in the database.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
