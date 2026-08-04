import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function BoardCreator() {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    organization_name: '',
    title: '',
    description: '',
    allow_anonymous: true,
    theme_color: '#4F46E5',
    owner_email: ''
  });
  const [creating, setCreating] = useState(false);
  const [previewSlug, setPreviewSlug] = useState('');

  const generateSlug = (orgName) => {
    const slug = orgName
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-+|-+$/g, '');
    setPreviewSlug(slug);
  };

  const handleOrgNameChange = (e) => {
    const value = e.target.value;
    setFormData({ ...formData, organization_name: value });
    generateSlug(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setCreating(true);

    try {
      const res = await fetch(`${API_BASE}/api/public-boards/boards`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });

      if (res.ok) {
        const data = await res.json();
        navigate(`/boards/${data.slug}`);
      } else {
        alert('Error creating board');
      }
    } catch (error) {
      console.error('Error:', error);
      alert('Error creating board');
    } finally {
      setCreating(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 to-white py-12 px-4">
      <div className="max-w-3xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Create Your Public Feedback Board
          </h1>
          <p className="text-lg text-gray-600">
            Like Canny, but with revenue-weighted voting built-in
          </p>
        </div>

        {/* Form */}
        <div className="bg-white rounded-xl shadow-lg p-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization Name *
              </label>
              <input
                type="text"
                required
                value={formData.organization_name}
                onChange={handleOrgNameChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Acme Corp"
              />
              {previewSlug && (
                <p className="mt-2 text-sm text-gray-500">
                  Your board URL: <span className="font-mono font-medium text-indigo-600">
                    compass.app/boards/{previewSlug}
                  </span>
                </p>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Board Title *
              </label>
              <input
                type="text"
                required
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Product Feedback"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Description
              </label>
              <textarea
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="Help us build better products by sharing your feedback"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Theme Color
              </label>
              <div className="flex items-center space-x-4">
                <input
                  type="color"
                  value={formData.theme_color}
                  onChange={(e) => setFormData({ ...formData, theme_color: e.target.value })}
                  className="h-12 w-20 rounded cursor-pointer"
                />
                <input
                  type="text"
                  value={formData.theme_color}
                  onChange={(e) => setFormData({ ...formData, theme_color: e.target.value })}
                  className="px-4 py-2 border border-gray-300 rounded-lg font-mono"
                  pattern="^#[0-9A-Fa-f]{6}$"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Owner Email (optional)
              </label>
              <input
                type="email"
                value={formData.owner_email}
                onChange={(e) => setFormData({ ...formData, owner_email: e.target.value })}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                placeholder="you@company.com"
              />
              <p className="mt-1 text-sm text-gray-500">
                For admin access and moderation
              </p>
            </div>

            <div className="flex items-center space-x-2">
              <input
                type="checkbox"
                id="allow_anonymous"
                checked={formData.allow_anonymous}
                onChange={(e) => setFormData({ ...formData, allow_anonymous: e.target.checked })}
                className="w-4 h-4 text-indigo-600 border-gray-300 rounded focus:ring-indigo-500"
              />
              <label htmlFor="allow_anonymous" className="text-sm text-gray-700">
                Allow anonymous feedback submissions
              </label>
            </div>

            <div className="pt-6 border-t border-gray-200">
              <button
                type="submit"
                disabled={creating}
                className={`w-full py-3 px-4 rounded-lg text-white font-medium transition-colors ${
                  creating
                    ? 'bg-gray-400 cursor-not-allowed'
                    : 'bg-indigo-600 hover:bg-indigo-700'
                }`}
              >
                {creating ? 'Creating Board...' : 'Create Public Board'}
              </button>
            </div>
          </form>
        </div>

        {/* Feature Highlights */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-3xl mb-3">💰</div>
            <h3 className="font-semibold text-gray-900 mb-2">Revenue-Weighted Voting</h3>
            <p className="text-sm text-gray-600">
              Enterprise customer votes count more than free users
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-3xl mb-3">⚡</div>
            <h3 className="font-semibold text-gray-900 mb-2">Real-Time Updates</h3>
            <p className="text-sm text-gray-600">
              See votes and comments appear instantly via WebSockets
            </p>
          </div>

          <div className="bg-white p-6 rounded-lg shadow">
            <div className="text-3xl mb-3">🎨</div>
            <h3 className="font-semibold text-gray-900 mb-2">Customizable</h3>
            <p className="text-sm text-gray-600">
              Match your brand with custom colors and domain
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
