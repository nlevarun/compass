import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function PublicBoard() {
  const { slug } = useParams();
  const [board, setBoard] = useState(null);
  const [posts, setPosts] = useState([]);
  const [sortBy, setSortBy] = useState('votes');
  const [filterCategory, setFilterCategory] = useState('all');
  const [showNewPostModal, setShowNewPostModal] = useState(false);
  const [userEmail, setUserEmail] = useState(localStorage.getItem('compass_user_email') || '');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadBoard();
    loadPosts();
  }, [slug, sortBy, filterCategory]);

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
      setLoading(true);
      const params = new URLSearchParams({
        sort_by: sortBy,
        ...(filterCategory !== 'all' && { category: filterCategory }),
        ...(userEmail && { user_email: userEmail })
      });

      const res = await fetch(`${API_BASE}/api/public-boards/boards/${slug}/posts?${params}`);
      if (res.ok) {
        const data = await res.json();
        setPosts(data);
      }
    } catch (error) {
      console.error('Error loading posts:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleVote = async (postId) => {
    if (!userEmail) {
      alert('Please enter your email to vote');
      return;
    }

    try {
      const res = await fetch(`${API_BASE}/api/public-boards/posts/${postId}/vote`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          user_email: userEmail,
          user_name: 'Anonymous',
          user_revenue: 0
        })
      });

      if (res.ok) {
        const data = await res.json();
        // Update post in list
        setPosts(posts.map(p =>
          p.id === postId
            ? { ...p, vote_count: data.vote_count, revenue_weighted_score: data.revenue_weighted_score, user_has_voted: true }
            : p
        ));
        localStorage.setItem('compass_user_email', userEmail);
      } else {
        const error = await res.json();
        alert(error.detail || 'Error voting');
      }
    } catch (error) {
      console.error('Error voting:', error);
    }
  };

  const handleNewPost = async (formData) => {
    try {
      const res = await fetch(`${API_BASE}/api/public-boards/boards/${slug}/posts`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          author_email: userEmail || null
        })
      });

      if (res.ok) {
        setShowNewPostModal(false);
        loadPosts();
      }
    } catch (error) {
      console.error('Error creating post:', error);
    }
  };

  const getCategoryEmoji = (category) => {
    const emojis = {
      feature: '✨',
      bug: '🐛',
      improvement: '📈',
      question: '❓'
    };
    return emojis[category] || '💡';
  };

  const getStatusBadge = (status) => {
    const badges = {
      open: { label: 'Open', color: 'bg-gray-200 text-gray-700' },
      planned: { label: 'Planned', color: 'bg-blue-200 text-blue-700' },
      in_progress: { label: 'In Progress', color: 'bg-yellow-200 text-yellow-700' },
      completed: { label: 'Completed', color: 'bg-green-200 text-green-700' },
      closed: { label: 'Closed', color: 'bg-red-200 text-red-700' }
    };
    const badge = badges[status] || badges.open;
    return (
      <span className={`px-2 py-1 rounded-full text-xs font-medium ${badge.color}`}>
        {badge.label}
      </span>
    );
  };

  if (!board) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading board...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900" style={{ color: board.theme_color }}>
                {board.title}
              </h1>
              <p className="mt-2 text-gray-600">{board.description}</p>
              <p className="mt-1 text-sm text-gray-500">{board.organization_name}</p>
            </div>
            <button
              onClick={() => setShowNewPostModal(true)}
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              style={{ backgroundColor: board.theme_color }}
            >
              Submit Feedback
            </button>
          </div>

          {/* Email input for voting */}
          {!userEmail && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg">
              <p className="text-sm text-blue-800 mb-2">Enter your email to vote on feedback</p>
              <input
                type="email"
                placeholder="your@email.com"
                className="px-3 py-2 border border-blue-200 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                onChange={(e) => setUserEmail(e.target.value)}
              />
            </div>
          )}
        </div>
      </div>

      {/* Filters and Sorting */}
      <div className="max-w-5xl mx-auto px-4 py-4">
        <div className="flex items-center justify-between">
          <div className="flex space-x-2">
            <select
              value={filterCategory}
              onChange={(e) => setFilterCategory(e.target.value)}
              className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">All Categories</option>
              <option value="feature">Features</option>
              <option value="bug">Bugs</option>
              <option value="improvement">Improvements</option>
              <option value="question">Questions</option>
            </select>
          </div>

          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-600">Sort by:</span>
            <select
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
              className="px-3 py-2 bg-white border border-gray-300 rounded-lg text-sm focus:ring-2 focus:ring-indigo-500"
            >
              <option value="votes">Most Votes</option>
              <option value="revenue_weighted">Revenue-Weighted</option>
              <option value="recent">Most Recent</option>
              <option value="trending">Trending</option>
            </select>
          </div>
        </div>
      </div>

      {/* Posts List */}
      <div className="max-w-5xl mx-auto px-4 pb-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-indigo-600 mx-auto"></div>
          </div>
        ) : posts.length === 0 ? (
          <div className="text-center py-12 bg-white rounded-lg">
            <p className="text-gray-500">No feedback yet. Be the first to submit!</p>
          </div>
        ) : (
          <div className="space-y-4">
            {posts.map((post) => (
              <div
                key={post.id}
                className="bg-white rounded-lg border border-gray-200 hover:border-gray-300 transition-colors"
              >
                <div className="p-6">
                  <div className="flex items-start space-x-4">
                    {/* Vote Button */}
                    <button
                      onClick={() => handleVote(post.id)}
                      disabled={post.user_has_voted}
                      className={`flex flex-col items-center min-w-[60px] px-3 py-2 rounded-lg transition-colors ${
                        post.user_has_voted
                          ? 'bg-indigo-100 text-indigo-700 cursor-not-allowed'
                          : 'bg-gray-100 hover:bg-indigo-50 text-gray-700 hover:text-indigo-700'
                      }`}
                    >
                      <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                      </svg>
                      <span className="text-lg font-bold mt-1">{post.vote_count}</span>
                    </button>

                    {/* Post Content */}
                    <div className="flex-1">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <div className="flex items-center space-x-2 mb-2">
                            <span className="text-xl">{getCategoryEmoji(post.category)}</span>
                            <h3 className="text-lg font-semibold text-gray-900">{post.title}</h3>
                            {post.status !== 'open' && getStatusBadge(post.status)}
                          </div>
                          {post.description && (
                            <p className="text-gray-600 mb-3">{post.description}</p>
                          )}
                          <div className="flex items-center space-x-4 text-sm text-gray-500">
                            <span>by {post.author_name}</span>
                            <span>•</span>
                            <span>{new Date(post.created_at).toLocaleDateString()}</span>
                            <span>•</span>
                            <span>{post.comment_count} comments</span>
                          </div>
                        </div>
                      </div>

                      {/* Revenue-Weighted Score Badge */}
                      {sortBy === 'revenue_weighted' && post.revenue_weighted_score > 0 && (
                        <div className="mt-3 inline-flex items-center px-3 py-1 bg-gradient-to-r from-yellow-100 to-yellow-200 rounded-full">
                          <span className="text-yellow-700 font-medium text-sm">
                            Revenue-Weighted Score: {post.revenue_weighted_score.toFixed(1)}
                          </span>
                          <span className="ml-2" title="Enterprise customer votes count more!">
                            ℹ️
                          </span>
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* New Post Modal */}
      {showNewPostModal && (
        <NewPostModal
          board={board}
          userEmail={userEmail}
          onClose={() => setShowNewPostModal(false)}
          onSubmit={handleNewPost}
        />
      )}
    </div>
  );
}

function NewPostModal({ board, userEmail, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    category: 'feature',
    author_name: ''
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-lg max-w-2xl w-full p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Submit Feedback</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Title *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Brief summary of your feedback"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={4}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Provide more details about your feedback..."
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Category
              </label>
              <select
                value={formData.category}
                onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              >
                <option value="feature">Feature Request</option>
                <option value="bug">Bug Report</option>
                <option value="improvement">Improvement</option>
                <option value="question">Question</option>
              </select>
            </div>

            {board.allow_anonymous && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Your Name (optional)
                </label>
                <input
                  type="text"
                  value={formData.author_name}
                  onChange={(e) => setFormData({ ...formData, author_name: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                  placeholder="Leave blank to post anonymously"
                />
              </div>
            )}
          </div>

          <div className="mt-6 flex justify-end space-x-3">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 text-gray-700 hover:text-gray-900 transition-colors"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition-colors"
              style={{ backgroundColor: board.theme_color }}
            >
              Submit Feedback
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
