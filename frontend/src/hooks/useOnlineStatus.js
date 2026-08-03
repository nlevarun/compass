import { useState, useEffect } from 'react';

export function useOnlineStatus() {
  const [isOnline, setIsOnline] = useState(navigator.onLine);
  const [wasOffline, setWasOffline] = useState(false);

  useEffect(() => {
    function handleOnline() {
      setIsOnline(true);
      if (wasOffline) {
        // Trigger a sync when coming back online
        if ('serviceWorker' in navigator && 'sync' in navigator.serviceWorker) {
          navigator.serviceWorker.ready.then((registration) => {
            return registration.sync.register('sync-feedback');
          }).catch((err) => {
            console.error('Background sync registration failed:', err);
          });
        }
      }
      setWasOffline(false);
    }

    function handleOffline() {
      setIsOnline(false);
      setWasOffline(true);
    }

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, [wasOffline]);

  return { isOnline, wasOffline };
}
