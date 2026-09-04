import { useEffect, useRef } from 'react';
import { API_BASE_URL } from '../api/axios';

/**
 * Derives the WebSocket URL from the configured API_BASE_URL
 */
export const getWsUrl = (path: string): string => {
  const cleanBase = API_BASE_URL.replace(/\/+$/, '');
  const wsProtocol = cleanBase.startsWith('https://') ? 'wss://' : 'ws://';
  const host = cleanBase.replace(/^https?:\/\//i, '');
  const cleanPath = path.startsWith('/') ? path : `/${path}`;
  return `${wsProtocol}${host}${cleanPath}`;
};

class RealTimeManager {
  private socket: WebSocket | null = null;
  private token: string | null = null;
  private reconnectTimeout: any = null;
  private pingInterval: any = null;
  private reconnectAttempts = 0;
  private isConnecting = false;
  private isExplicitlyClosed = false;

  public connect(token: string) {
    if (!token) return;
    this.token = token;
    this.isExplicitlyClosed = false;

    if (this.socket && (this.socket.readyState === WebSocket.OPEN || this.socket.readyState === WebSocket.CONNECTING)) {
      return;
    }

    this.isConnecting = true;
    const wsUrl = getWsUrl(`/ws/live?token=${encodeURIComponent(token)}`);

    try {
      this.socket = new WebSocket(wsUrl);

      this.socket.onopen = () => {
        this.isConnecting = false;
        this.reconnectAttempts = 0;
        console.log('[RealTime] WebSocket connected successfully');

        // Start ping heartbeat every 25 seconds
        if (this.pingInterval) clearInterval(this.pingInterval);
        this.pingInterval = setInterval(() => {
          if (this.socket && this.socket.readyState === WebSocket.OPEN) {
            this.socket.send(JSON.stringify({ type: 'ping' }));
          }
        }, 25000);
      };

      this.socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data?.type === 'pong') return;

          console.log('[RealTime] Event received:', data);

          // Broadcast custom browser events
          window.dispatchEvent(new CustomEvent('homiq:realtime_event', { detail: data }));
          window.dispatchEvent(new CustomEvent('homiq:booking_update', { detail: data }));
        } catch (e) {
          // non-json or text
        }
      };

      this.socket.onerror = (err) => {
        console.warn('[RealTime] WebSocket error:', err);
      };

      this.socket.onclose = () => {
        this.isConnecting = false;
        if (this.pingInterval) {
          clearInterval(this.pingInterval);
          this.pingInterval = null;
        }

        if (!this.isExplicitlyClosed) {
          // Exponential backoff reconnect
          const delay = Math.min(1000 * Math.pow(1.5, this.reconnectAttempts), 10000);
          this.reconnectAttempts++;
          console.log(`[RealTime] Reconnecting in ${Math.round(delay / 1000)}s (attempt ${this.reconnectAttempts})...`);
          if (this.reconnectTimeout) clearTimeout(this.reconnectTimeout);
          this.reconnectTimeout = setTimeout(() => {
            if (this.token && !this.isExplicitlyClosed) {
              this.connect(this.token);
            }
          }, delay);
        }
      };
    } catch (err) {
      this.isConnecting = false;
      console.error('[RealTime] Failed to create WebSocket connection:', err);
    }
  }

  public disconnect() {
    this.isExplicitlyClosed = true;
    this.token = null;
    if (this.reconnectTimeout) {
      clearTimeout(this.reconnectTimeout);
      this.reconnectTimeout = null;
    }
    if (this.pingInterval) {
      clearInterval(this.pingInterval);
      this.pingInterval = null;
    }
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }
}

export const realTimeManager = new RealTimeManager();

/**
 * Manually trigger a local sync event across all mounted dashboards in this client.
 */
export const triggerLocalSync = () => {
  window.dispatchEvent(new CustomEvent('homiq:booking_update', { detail: { local: true } }));
};

/**
 * React hook that binds any dashboard / page to live real-time sync.
 * Triggers onUpdate() when:
 * 1. A WebSocket booking/status event is received
 * 2. Window/tab gains focus or becomes visible
 * 3. Fallback background polling every intervalMs (default: 8s)
 */
export function useRealTimeSync(onUpdate: () => void, intervalMs: number = 8000) {
  const onUpdateRef = useRef(onUpdate);
  onUpdateRef.current = onUpdate;

  useEffect(() => {
    const handleEvent = () => {
      onUpdateRef.current();
    };

    const handleVisibility = () => {
      if (document.visibilityState === 'visible') {
        onUpdateRef.current();
      }
    };

    window.addEventListener('homiq:booking_update', handleEvent);
    window.addEventListener('visibilitychange', handleVisibility);
    window.addEventListener('focus', handleEvent);

    // Periodic fallback polling
    const pollTimer = setInterval(() => {
      onUpdateRef.current();
    }, intervalMs);

    return () => {
      window.removeEventListener('homiq:booking_update', handleEvent);
      window.removeEventListener('visibilitychange', handleVisibility);
      window.removeEventListener('focus', handleEvent);
      clearInterval(pollTimer);
    };
  }, [intervalMs]);
}
