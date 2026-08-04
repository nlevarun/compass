/**
 * Component Import Validation Test
 *
 * This test ensures all components can be imported without errors.
 * Run with: npm test (after setting up a test runner)
 */

describe('Component Imports', () => {
  test('App component imports successfully', async () => {
    const App = await import('../App.jsx');
    expect(App.default).toBeDefined();
  });

  test('Dashboard component imports successfully', async () => {
    const Dashboard = await import('../components/Dashboard.jsx');
    expect(Dashboard.default).toBeDefined();
  });

  test('FeedbackInbox component imports successfully', async () => {
    const FeedbackInbox = await import('../components/FeedbackInbox.jsx');
    expect(FeedbackInbox.default).toBeDefined();
  });

  test('ClusterView component imports successfully', async () => {
    const ClusterView = await import('../components/ClusterView.jsx');
    expect(ClusterView.default).toBeDefined();
  });

  test('RoadmapDashboard component imports successfully', async () => {
    const RoadmapDashboard = await import('../components/RoadmapDashboard.jsx');
    expect(RoadmapDashboard.default).toBeDefined();
  });

  test('PriorityAnalysis component imports successfully', async () => {
    const PriorityAnalysis = await import('../components/PriorityAnalysis.jsx');
    expect(PriorityAnalysis.default).toBeDefined();
  });

  test('ErrorBoundary component imports successfully', async () => {
    const ErrorBoundary = await import('../components/ErrorBoundary.jsx');
    expect(ErrorBoundary.default).toBeDefined();
  });

  test('OfflineBanner component imports successfully', async () => {
    const OfflineBanner = await import('../components/OfflineBanner.jsx');
    expect(OfflineBanner.default).toBeDefined();
  });

  test('InstallPrompt component imports successfully', async () => {
    const InstallPrompt = await import('../components/InstallPrompt.jsx');
    expect(InstallPrompt.default).toBeDefined();
  });

  test('Toast component imports successfully', async () => {
    const Toast = await import('../components/Toast.jsx');
    expect(Toast.default).toBeDefined();
  });
});

describe('Service Imports', () => {
  test('API service imports successfully', async () => {
    const api = await import('../services/api.js');
    expect(api.default).toBeDefined();
    expect(api.getStats).toBeDefined();
    expect(api.getFeedback).toBeDefined();
    expect(api.getClusters).toBeDefined();
    expect(api.getRoadmap).toBeDefined();
  });

  test('WebSocket service imports successfully', async () => {
    const websocketService = await import('../services/websocket.js');
    expect(websocketService.default).toBeDefined();
  });
});

describe('Hook Imports', () => {
  test('useOnlineStatus hook imports successfully', async () => {
    const { useOnlineStatus } = await import('../hooks/useOnlineStatus.js');
    expect(useOnlineStatus).toBeDefined();
  });

  test('usePWAInstall hook imports successfully', async () => {
    const { usePWAInstall } = await import('../hooks/usePWAInstall.js');
    expect(usePWAInstall).toBeDefined();
  });
});
