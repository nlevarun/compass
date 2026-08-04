import { useState, useEffect } from 'react';
import { CheckCircle, XCircle, Clock, Copy, ExternalLink, Zap } from 'lucide-react';

const WEBHOOK_SERVICES = [
  {
    name: 'Slack',
    endpoint: '/webhooks/slack/events',
    setupGuideEndpoint: '/webhooks/slack/setup-guide',
    testEndpoint: '/webhooks/slack/test',
    color: 'purple',
    icon: '💬',
    description: 'Real-time Slack message events',
  },
  {
    name: 'GitHub',
    endpoint: '/webhooks/github/issues',
    setupGuideEndpoint: '/webhooks/github/setup-guide',
    testEndpoint: '/webhooks/github/test',
    color: 'gray',
    icon: '🔧',
    description: 'GitHub issue and comment events',
  },
  {
    name: 'Intercom',
    endpoint: '/webhooks/intercom/conversations',
    setupGuideEndpoint: '/webhooks/intercom/setup-guide',
    testEndpoint: '/webhooks/intercom/test',
    color: 'blue',
    icon: '💬',
    description: 'Intercom conversation events',
  },
];

function WebhookSetup() {
  const [setupGuides, setSetupGuides] = useState({});
  const [testResults, setTestResults] = useState({});
  const [loading, setLoading] = useState({});
  const [copied, setCopied] = useState({});
  const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

  useEffect(() => {
    loadSetupGuides();
  }, []);

  const loadSetupGuides = async () => {
    for (const service of WEBHOOK_SERVICES) {
      try {
        const response = await fetch(`${API_BASE}${service.setupGuideEndpoint}`);
        const data = await response.json();
        setSetupGuides((prev) => ({ ...prev, [service.name]: data }));
      } catch (error) {
        console.error(`Failed to load setup guide for ${service.name}:`, error);
      }
    }
  };

  const copyToClipboard = (text, serviceName) => {
    navigator.clipboard.writeText(text);
    setCopied((prev) => ({ ...prev, [serviceName]: true }));
    setTimeout(() => {
      setCopied((prev) => ({ ...prev, [serviceName]: false }));
    }, 2000);
  };

  const testWebhook = async (service) => {
    setLoading((prev) => ({ ...prev, [service.name]: true }));
    try {
      const response = await fetch(`${API_BASE}${service.testEndpoint}`);
      const data = await response.json();
      setTestResults((prev) => ({
        ...prev,
        [service.name]: {
          success: true,
          data,
          timestamp: new Date().toISOString(),
        },
      }));
    } catch (error) {
      setTestResults((prev) => ({
        ...prev,
        [service.name]: {
          success: false,
          error: error.message,
          timestamp: new Date().toISOString(),
        },
      }));
    } finally {
      setLoading((prev) => ({ ...prev, [service.name]: false }));
    }
  };

  const getColorClasses = (color) => {
    const colors = {
      purple: 'bg-purple-50 border-purple-200 text-purple-700',
      gray: 'bg-gray-50 border-gray-200 text-gray-700',
      blue: 'bg-blue-50 border-blue-200 text-blue-700',
    };
    return colors[color] || colors.gray;
  };

  const getButtonColorClasses = (color) => {
    const colors = {
      purple: 'bg-purple-600 hover:bg-purple-700',
      gray: 'bg-gray-600 hover:bg-gray-700',
      blue: 'bg-blue-600 hover:bg-blue-700',
    };
    return colors[color] || colors.gray;
  };

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-2">
          <Zap className="w-8 h-8 text-yellow-500" />
          <h1 className="text-3xl font-bold text-gray-900">Real-Time Webhook Setup</h1>
        </div>
        <p className="text-gray-600 text-lg">
          Replace 5-minute polling with &lt;1 second real-time feedback delivery
        </p>

        {/* Performance Badge */}
        <div className="mt-4 inline-flex items-center gap-2 px-4 py-2 bg-green-50 border border-green-200 rounded-lg">
          <Zap className="w-4 h-4 text-green-600" />
          <span className="text-sm font-semibold text-green-700">
            300x Faster than polling
          </span>
          <span className="text-xs text-green-600">
            (5 minutes → &lt;1 second)
          </span>
        </div>
      </div>

      {/* Webhook Services */}
      <div className="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-6">
        {WEBHOOK_SERVICES.map((service) => {
          const guide = setupGuides[service.name];
          const testResult = testResults[service.name];
          const isLoading = loading[service.name];
          const isCopied = copied[service.name];

          return (
            <div
              key={service.name}
              className={`border-2 rounded-xl p-6 transition-all ${getColorClasses(service.color)}`}
            >
              {/* Service Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{service.icon}</span>
                  <div>
                    <h3 className="text-xl font-bold">{service.name}</h3>
                    <p className="text-sm opacity-80">{service.description}</p>
                  </div>
                </div>
              </div>

              {/* Webhook URL */}
              <div className="mb-4">
                <label className="text-xs font-semibold uppercase opacity-70 mb-1 block">
                  Webhook URL
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={guide?.webhook_url || `${API_BASE}${service.endpoint}`}
                    readOnly
                    className="flex-1 px-3 py-2 bg-white border border-gray-300 rounded text-sm font-mono"
                  />
                  <button
                    onClick={() =>
                      copyToClipboard(
                        guide?.webhook_url || `${API_BASE}${service.endpoint}`,
                        service.name
                      )
                    }
                    className="px-3 py-2 bg-white border border-gray-300 rounded hover:bg-gray-50 transition-colors"
                    title="Copy to clipboard"
                  >
                    {isCopied ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <Copy className="w-4 h-4" />
                    )}
                  </button>
                </div>
              </div>

              {/* Performance Stats */}
              {guide?.performance && (
                <div className="mb-4 p-3 bg-white bg-opacity-50 rounded-lg">
                  <div className="text-xs font-semibold mb-2">Performance</div>
                  <div className="grid grid-cols-2 gap-2 text-xs">
                    <div>
                      <span className="opacity-70">Before:</span>
                      <span className="ml-2 font-mono font-bold">
                        {guide.performance.before}
                      </span>
                    </div>
                    <div>
                      <span className="opacity-70">After:</span>
                      <span className="ml-2 font-mono font-bold text-green-600">
                        {guide.performance.after}
                      </span>
                    </div>
                  </div>
                </div>
              )}

              {/* Test Button */}
              <button
                onClick={() => testWebhook(service)}
                disabled={isLoading}
                className={`w-full px-4 py-2 text-white rounded-lg font-semibold transition-colors ${getButtonColorClasses(
                  service.color
                )} disabled:opacity-50 disabled:cursor-not-allowed`}
              >
                {isLoading ? (
                  <span className="flex items-center justify-center gap-2">
                    <Clock className="w-4 h-4 animate-spin" />
                    Testing...
                  </span>
                ) : (
                  'Test Webhook'
                )}
              </button>

              {/* Test Result */}
              {testResult && (
                <div
                  className={`mt-3 p-3 rounded-lg text-sm ${
                    testResult.success
                      ? 'bg-green-50 border border-green-200'
                      : 'bg-red-50 border border-red-200'
                  }`}
                >
                  <div className="flex items-center gap-2 mb-1">
                    {testResult.success ? (
                      <CheckCircle className="w-4 h-4 text-green-600" />
                    ) : (
                      <XCircle className="w-4 h-4 text-red-600" />
                    )}
                    <span
                      className={`font-semibold ${
                        testResult.success ? 'text-green-700' : 'text-red-700'
                      }`}
                    >
                      {testResult.success ? 'Test Successful!' : 'Test Failed'}
                    </span>
                  </div>
                  {testResult.success && testResult.data && (
                    <div className="text-xs space-y-1 text-gray-700">
                      <div>
                        Feedback ID: <span className="font-mono">{testResult.data.feedback_id}</span>
                      </div>
                      <div>
                        Latency:{' '}
                        <span className="font-mono font-bold text-green-600">
                          {testResult.data.processing_time_ms?.toFixed(2)}ms
                        </span>
                      </div>
                    </div>
                  )}
                  {!testResult.success && (
                    <div className="text-xs text-red-600">{testResult.error}</div>
                  )}
                </div>
              )}

              {/* Setup Guide Link */}
              {guide && (
                <div className="mt-4">
                  <details className="text-sm">
                    <summary className="cursor-pointer font-semibold hover:underline">
                      Setup Instructions
                    </summary>
                    <ol className="mt-2 space-y-1 pl-5 list-decimal text-xs">
                      {guide.steps?.map((step, idx) => (
                        <li key={idx} className="opacity-80">
                          {step}
                        </li>
                      ))}
                    </ol>
                  </details>
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Instructions Section */}
      <div className="mt-8 bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-200 rounded-xl p-6">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Start Guide</h2>
        <div className="grid md:grid-cols-2 gap-6">
          <div>
            <h3 className="font-bold text-lg mb-2">1. Test Locally (ngrok)</h3>
            <div className="bg-white rounded p-3 font-mono text-sm">
              <div className="text-gray-600"># Start ngrok</div>
              <div>ngrok http 8000</div>
              <div className="mt-2 text-gray-600"># Use ngrok URL for webhooks</div>
              <div className="text-xs text-gray-500">
                https://abc123.ngrok.io/webhooks/slack/events
              </div>
            </div>
          </div>
          <div>
            <h3 className="font-bold text-lg mb-2">2. Configure Service</h3>
            <ul className="space-y-2 text-sm">
              <li className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>Copy webhook URL from card above</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>Add to service provider settings</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>Set environment variables (secrets)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-green-600">✓</span>
                <span>Click "Test Webhook" to verify</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Benchmark */}
        <div className="mt-6 pt-6 border-t border-blue-200">
          <h3 className="font-bold text-lg mb-3">Performance Benchmark</h3>
          <div className="grid grid-cols-3 gap-4 text-center">
            <div className="bg-white rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-1">Before (Polling)</div>
              <div className="text-3xl font-bold text-red-600">300s</div>
              <div className="text-xs text-gray-500">5 minutes</div>
            </div>
            <div className="flex items-center justify-center">
              <div className="text-4xl font-bold text-green-600">→</div>
            </div>
            <div className="bg-white rounded-lg p-4">
              <div className="text-sm text-gray-600 mb-1">After (Webhooks)</div>
              <div className="text-3xl font-bold text-green-600">&lt;1s</div>
              <div className="text-xs text-gray-500">sub-second</div>
            </div>
          </div>
          <div className="mt-3 text-center">
            <span className="inline-flex items-center gap-2 px-4 py-2 bg-yellow-100 border border-yellow-300 rounded-lg text-sm font-bold text-yellow-800">
              <Zap className="w-4 h-4" />
              300x faster than Productboard (60min delay)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

export default WebhookSetup;
