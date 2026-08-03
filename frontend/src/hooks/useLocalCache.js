import { useState, useEffect } from 'react';

const DB_NAME = 'CompassDB';
const DB_VERSION = 1;
const CACHE_STORE = 'apiCache';
const QUEUE_STORE = 'requestQueue';

// Initialize IndexedDB
function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onerror = () => reject(request.error);
    request.onsuccess = () => resolve(request.result);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      // Create cache store
      if (!db.objectStoreNames.contains(CACHE_STORE)) {
        const cacheStore = db.createObjectStore(CACHE_STORE, { keyPath: 'key' });
        cacheStore.createIndex('timestamp', 'timestamp', { unique: false });
      }

      // Create request queue store
      if (!db.objectStoreNames.contains(QUEUE_STORE)) {
        db.createObjectStore(QUEUE_STORE, { keyPath: 'id', autoIncrement: true });
      }
    };
  });
}

// Cache data in IndexedDB
export async function cacheData(key, data, ttl = 5 * 60 * 1000) {
  try {
    const db = await openDB();
    const transaction = db.transaction([CACHE_STORE], 'readwrite');
    const store = transaction.objectStore(CACHE_STORE);

    const cacheEntry = {
      key,
      data,
      timestamp: Date.now(),
      ttl
    };

    store.put(cacheEntry);

    return new Promise((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  } catch (error) {
    console.error('Failed to cache data:', error);
  }
}

// Get cached data from IndexedDB
export async function getCachedData(key) {
  try {
    const db = await openDB();
    const transaction = db.transaction([CACHE_STORE], 'readonly');
    const store = transaction.objectStore(CACHE_STORE);

    return new Promise((resolve, reject) => {
      const request = store.get(key);

      request.onsuccess = () => {
        const entry = request.result;

        if (!entry) {
          resolve(null);
          return;
        }

        // Check if cache is expired
        if (Date.now() - entry.timestamp > entry.ttl) {
          resolve(null);
          return;
        }

        resolve(entry.data);
      };

      request.onerror = () => reject(request.error);
    });
  } catch (error) {
    console.error('Failed to get cached data:', error);
    return null;
  }
}

// Queue request for later sync
export async function queueRequest(url, options) {
  try {
    const db = await openDB();
    const transaction = db.transaction([QUEUE_STORE], 'readwrite');
    const store = transaction.objectStore(QUEUE_STORE);

    const queueEntry = {
      url,
      options,
      timestamp: Date.now()
    };

    store.add(queueEntry);

    return new Promise((resolve, reject) => {
      transaction.oncomplete = () => resolve();
      transaction.onerror = () => reject(transaction.error);
    });
  } catch (error) {
    console.error('Failed to queue request:', error);
  }
}

// Get all queued requests
export async function getQueuedRequests() {
  try {
    const db = await openDB();
    const transaction = db.transaction([QUEUE_STORE], 'readonly');
    const store = transaction.objectStore(QUEUE_STORE);

    return new Promise((resolve, reject) => {
      const request = store.getAll();
      request.onsuccess = () => resolve(request.result);
      request.onerror = () => reject(request.error);
    });
  } catch (error) {
    console.error('Failed to get queued requests:', error);
    return [];
  }
}

// Clear queued request
export async function clearQueuedRequest(id) {
  try {
    const db = await openDB();
    const transaction = db.transaction([QUEUE_STORE], 'readwrite');
    const store = transaction.objectStore(QUEUE_STORE);

    return new Promise((resolve, reject) => {
      const request = store.delete(id);
      request.onsuccess = () => resolve();
      request.onerror = () => reject(request.error);
    });
  } catch (error) {
    console.error('Failed to clear queued request:', error);
  }
}

// React hook for using local cache
export function useLocalCache(key, ttl) {
  const [cachedData, setCachedData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadCache() {
      setLoading(true);
      const data = await getCachedData(key);
      setCachedData(data);
      setLoading(false);
    }

    if (key) {
      loadCache();
    }
  }, [key]);

  const updateCache = async (data) => {
    await cacheData(key, data, ttl);
    setCachedData(data);
  };

  return { cachedData, loading, updateCache };
}
