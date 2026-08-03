/**
 * WebSocket Service for Compass
 *
 * Provides real-time communication with the Compass backend.
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Event subscription system
 * - Type-safe event handlers
 * - Connection state management
 * - Heartbeat/keepalive handling
 */

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000/ws';

// Connection states
export const ConnectionState = {
  CONNECTING: 'connecting',
  CONNECTED: 'connected',
  DISCONNECTED: 'disconnected',
  RECONNECTING: 'reconnecting',
  ERROR: 'error',
};

// Event types from backend
export const EventTypes = {
  // Connection events
  CONNECTION_ESTABLISHED: 'connection.established',
  HEARTBEAT: 'heartbeat',
  ROOM_JOINED: 'room.joined',
  ROOM_LEFT: 'room.left',

  // Feedback events
  FEEDBACK_NEW: 'feedback.new',
  FEEDBACK_SYNCED: 'feedback.synced',
  FEEDBACK_BATCH: 'feedback.batch',

  // Cluster events
  CLUSTER_CREATED: 'cluster.created',
  CLUSTERING_COMPLETE: 'clustering.complete',
  CLUSTER_UPDATED: 'cluster.updated',

  // Roadmap events
  ROADMAP_GENERATED: 'roadmap.generated',
  ROADMAP_UPDATED: 'roadmap.updated',

  // Stats events
  STATS_UPDATED: 'stats.updated',

  // Progress events
  PROGRESS_UPDATE: 'progress.update',
  TASK_STARTED: 'task.started',
  TASK_COMPLETED: 'task.completed',
  TASK_ERROR: 'task.error',

  // Notification events
  NOTIFICATION: 'notification',
};

class WebSocketService {
  constructor() {
    this.ws = null;
    this.clientId = null;
    this.connectionState = ConnectionState.DISCONNECTED;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 10;
    this.reconnectDelay = 1000; // Start with 1 second
    this.maxReconnectDelay = 30000; // Max 30 seconds
    this.reconnectTimer = null;
    this.heartbeatTimer = null;
    this.lastHeartbeat = null;

    // Event listeners: { eventType: [callbacks] }
    this.eventListeners = {};

    // State change listeners
    this.stateChangeListeners = [];

    // Message queue for offline mode
    this.messageQueue = [];
    this.maxQueueSize = 50;

    // Auto-connect flag
    this.autoConnect = true;

    // Subscribed rooms
    this.subscribedRooms = new Set();
  }

  /**
   * Connect to WebSocket server
   */
  connect() {
    if (this.ws && (this.ws.readyState === WebSocket.CONNECTING || this.ws.readyState === WebSocket.OPEN)) {
      console.log('[WS] Already connected or connecting');
      return;
    }

    console.log('[WS] Connecting to:', WS_URL);
    this.updateConnectionState(ConnectionState.CONNECTING);

    try {
      this.ws = new WebSocket(WS_URL);
      this.setupEventHandlers();
    } catch (error) {
      console.error('[WS] Connection error:', error);
      this.handleConnectionError(error);
    }
  }

  /**
   * Disconnect from WebSocket server
   */
  disconnect() {
    console.log('[WS] Disconnecting...');
    this.autoConnect = false;
    this.clearReconnectTimer();
    this.clearHeartbeatTimer();

    if (this.ws) {
      this.ws.close(1000, 'Client disconnecting');
      this.ws = null;
    }

    this.updateConnectionState(ConnectionState.DISCONNECTED);
  }

  /**
   * Setup WebSocket event handlers
   */
  setupEventHandlers() {
    this.ws.onopen = this.handleOpen.bind(this);
    this.ws.onclose = this.handleClose.bind(this);
    this.ws.onerror = this.handleError.bind(this);
    this.ws.onmessage = this.handleMessage.bind(this);
  }

  /**
   * Handle WebSocket open event
   */
  handleOpen(event) {
    console.log('[WS] Connected successfully');
    this.updateConnectionState(ConnectionState.CONNECTED);
    this.reconnectAttempts = 0;
    this.reconnectDelay = 1000;
    this.lastHeartbeat = Date.now();

    // Start heartbeat monitoring
    this.startHeartbeatMonitoring();

    // Re-subscribe to rooms if reconnecting
    if (this.subscribedRooms.size > 0) {
      this.subscribeToRooms(Array.from(this.subscribedRooms));
    }

    // Process queued messages
    this.processMessageQueue();
  }

  /**
   * Handle WebSocket close event
   */
  handleClose(event) {
    console.log('[WS] Connection closed:', event.code, event.reason);
    this.clearHeartbeatTimer();

    if (event.code === 1000) {
      // Normal closure
      this.updateConnectionState(ConnectionState.DISCONNECTED);
    } else if (this.autoConnect) {
      // Abnormal closure - attempt reconnect
      this.attemptReconnect();
    } else {
      this.updateConnectionState(ConnectionState.DISCONNECTED);
    }
  }

  /**
   * Handle WebSocket error event
   */
  handleError(error) {
    console.error('[WS] WebSocket error:', error);
    this.updateConnectionState(ConnectionState.ERROR);
  }

  /**
   * Handle incoming WebSocket messages
   */
  handleMessage(event) {
    try {
      const message = JSON.parse(event.data);
      const eventType = message.event;

      // console.log('[WS] Received event:', eventType, message);

      // Handle special events
      if (eventType === EventTypes.CONNECTION_ESTABLISHED) {
        this.clientId = message.client_id;
        console.log('[WS] Client ID assigned:', this.clientId);
      } else if (eventType === EventTypes.HEARTBEAT) {
        this.lastHeartbeat = Date.now();
      }

      // Dispatch to event listeners
      this.dispatchEvent(eventType, message.data || message);

    } catch (error) {
      console.error('[WS] Error parsing message:', error);
    }
  }

  /**
   * Attempt to reconnect with exponential backoff
   */
  attemptReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('[WS] Max reconnect attempts reached');
      this.updateConnectionState(ConnectionState.ERROR);
      this.dispatchEvent(EventTypes.NOTIFICATION, {
        level: 'error',
        title: 'Connection Lost',
        message: 'Unable to reconnect to server. Please refresh the page.',
      });
      return;
    }

    this.reconnectAttempts++;
    this.updateConnectionState(ConnectionState.RECONNECTING);

    // Calculate delay with exponential backoff
    const delay = Math.min(
      this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1),
      this.maxReconnectDelay
    );

    console.log(`[WS] Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);

    this.reconnectTimer = setTimeout(() => {
      this.connect();
    }, delay);
  }

  /**
   * Clear reconnection timer
   */
  clearReconnectTimer() {
    if (this.reconnectTimer) {
      clearTimeout(this.reconnectTimer);
      this.reconnectTimer = null;
    }
  }

  /**
   * Start heartbeat monitoring
   */
  startHeartbeatMonitoring() {
    this.clearHeartbeatTimer();

    this.heartbeatTimer = setInterval(() => {
      const timeSinceLastHeartbeat = Date.now() - this.lastHeartbeat;

      // If no heartbeat for 45 seconds, consider connection dead
      if (timeSinceLastHeartbeat > 45000) {
        console.warn('[WS] No heartbeat received, connection may be dead');
        this.ws?.close();
      }
    }, 10000); // Check every 10 seconds
  }

  /**
   * Clear heartbeat timer
   */
  clearHeartbeatTimer() {
    if (this.heartbeatTimer) {
      clearInterval(this.heartbeatTimer);
      this.heartbeatTimer = null;
    }
  }

  /**
   * Send a message to the server
   */
  send(message) {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.warn('[WS] Cannot send message - not connected');

      // Queue message for later
      if (this.messageQueue.length < this.maxQueueSize) {
        this.messageQueue.push(message);
      }
    }
  }

  /**
   * Process queued messages
   */
  processMessageQueue() {
    while (this.messageQueue.length > 0) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }

  /**
   * Subscribe to one or more rooms
   */
  subscribeToRooms(rooms) {
    rooms.forEach(room => this.subscribedRooms.add(room));

    this.send({
      action: 'subscribe',
      rooms: rooms,
    });
  }

  /**
   * Join a specific room
   */
  joinRoom(room) {
    this.subscribedRooms.add(room);

    this.send({
      action: 'join',
      room: room,
    });
  }

  /**
   * Leave a specific room
   */
  leaveRoom(room) {
    this.subscribedRooms.delete(room);

    this.send({
      action: 'leave',
      room: room,
    });
  }

  /**
   * Send ping to server
   */
  ping() {
    this.send({ action: 'ping' });
  }

  /**
   * Request connection stats
   */
  requestStats() {
    this.send({ action: 'stats' });
  }

  /**
   * Subscribe to an event type
   */
  on(eventType, callback) {
    if (!this.eventListeners[eventType]) {
      this.eventListeners[eventType] = [];
    }

    this.eventListeners[eventType].push(callback);

    // Return unsubscribe function
    return () => this.off(eventType, callback);
  }

  /**
   * Unsubscribe from an event type
   */
  off(eventType, callback) {
    if (!this.eventListeners[eventType]) return;

    this.eventListeners[eventType] = this.eventListeners[eventType].filter(
      cb => cb !== callback
    );
  }

  /**
   * Subscribe to connection state changes
   */
  onStateChange(callback) {
    this.stateChangeListeners.push(callback);

    // Return unsubscribe function
    return () => {
      this.stateChangeListeners = this.stateChangeListeners.filter(
        cb => cb !== callback
      );
    };
  }

  /**
   * Dispatch an event to listeners
   */
  dispatchEvent(eventType, data) {
    const listeners = this.eventListeners[eventType] || [];

    listeners.forEach(callback => {
      try {
        callback(data);
      } catch (error) {
        console.error(`[WS] Error in event listener for ${eventType}:`, error);
      }
    });
  }

  /**
   * Update connection state and notify listeners
   */
  updateConnectionState(newState) {
    const oldState = this.connectionState;
    this.connectionState = newState;

    console.log(`[WS] State changed: ${oldState} -> ${newState}`);

    this.stateChangeListeners.forEach(callback => {
      try {
        callback(newState, oldState);
      } catch (error) {
        console.error('[WS] Error in state change listener:', error);
      }
    });
  }

  /**
   * Get current connection state
   */
  getState() {
    return this.connectionState;
  }

  /**
   * Check if connected
   */
  isConnected() {
    return this.connectionState === ConnectionState.CONNECTED;
  }

  /**
   * Handle connection error
   */
  handleConnectionError(error) {
    console.error('[WS] Connection error:', error);
    this.updateConnectionState(ConnectionState.ERROR);

    if (this.autoConnect) {
      this.attemptReconnect();
    }
  }

  /**
   * Get WebSocket ready state
   */
  getReadyState() {
    if (!this.ws) return WebSocket.CLOSED;
    return this.ws.readyState;
  }
}

// Create singleton instance
const wsService = new WebSocketService();

// Auto-connect on module load
if (typeof window !== 'undefined') {
  wsService.connect();

  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    wsService.disconnect();
  });
}

export default wsService;
