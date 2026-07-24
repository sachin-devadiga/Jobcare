'use client';
import { createContext, useState, useCallback, useRef, useEffect, useContext } from 'react';
import { toast } from 'react-toastify';

const NOTIFICATION_SOUND = '/sounds/notification.mp3';

export const NotificationContext = createContext(null);

export function NotificationProvider({ children }) {
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [wsConnected, setWsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const audioRef = useRef(null);

  const playNotificationSound = useCallback(() => {
    try {
      if (!audioRef.current) {
        audioRef.current = new Audio(NOTIFICATION_SOUND);
      }
      audioRef.current.currentTime = 0;
      audioRef.current.play().catch(() => {});
    } catch {}
  }, []);

  const showToast = useCallback((notification) => {
    const toastFn = notification.type === 'success' ? toast.success :
      notification.type === 'error' ? toast.error :
      notification.type === 'warning' ? toast.warning :
      toast.info;
    toastFn(notification.message || notification.body || notification.title, {
      toastId: notification.id,
      onClick: () => {
        if (notification.actionLink) {
          window.location.href = notification.actionLink;
        }
      },
    });
  }, []);

  const addNotification = useCallback((notification) => {
    const notif = {
      id: notification.id || Date.now().toString(),
      title: notification.title || '',
      body: notification.body || notification.message || '',
      type: notification.type || 'info',
      data: notification.data || {},
      actionLink: notification.actionLink || notification.data?.action_link,
      read: notification.read || false,
      createdAt: notification.created_at || new Date().toISOString(),
    };

    setNotifications((prev) => [notif, ...prev]);
    setUnreadCount((prev) => prev + (notif.read ? 0 : 1));

    showToast(notif);
    playNotificationSound();
  }, [showToast, playNotificationSound]);

  const markAsRead = useCallback((id) => {
    setNotifications((prev) => {
      const updated = prev.map((n) => n.id === id ? { ...n, read: true } : n);
      const wasUnread = prev.find((n) => n.id === id && !n.read);
      if (wasUnread) {
        setUnreadCount((c) => Math.max(0, c - 1));
      }
      return updated;
    });
  }, []);

  const markAllAsRead = useCallback(() => {
    setNotifications((prev) => prev.map((n) => ({ ...n, read: true })));
    setUnreadCount(0);
  }, []);

  const clearNotifications = useCallback(() => {
    setNotifications([]);
    setUnreadCount(0);
  }, []);

  const removeNotification = useCallback((id) => {
    setNotifications((prev) => {
      const removed = prev.find((n) => n.id === id);
      if (removed && !removed.read) {
        setUnreadCount((c) => Math.max(0, c - 1));
      }
      return prev.filter((n) => n.id !== id);
    });
  }, []);

  const connectWebSocket = useCallback((token) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;

    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    try {
      const ws = new WebSocket(`${wsUrl}/ws/notifications/?token=${token}`);

      ws.onopen = () => {
        setWsConnected(true);
        reconnectAttemptsRef.current = 0;
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'notification' || data.type === 'notification_event') {
            const notification = data.notification || data.data || data;
            addNotification(notification);
          } else if (data.type === 'badge_update') {
            setUnreadCount(data.unread_count || 0);
          }
        } catch {}
      };

      ws.onclose = () => {
        setWsConnected(false);
        scheduleReconnect(token);
      };

      ws.onerror = () => {
        setWsConnected(false);
      };

      wsRef.current = ws;
    } catch {
      scheduleReconnect(token);
    }
  }, [addNotification]);

  const scheduleReconnect = useCallback((token) => {
    if (reconnectTimerRef.current) return;
    const maxAttempts = 10;
    if (reconnectAttemptsRef.current >= maxAttempts) return;

    const delay = reconnectAttemptsRef.current === 0
      ? 1000
      : Math.min(30000, Math.pow(2, reconnectAttemptsRef.current) * 1000);
    reconnectAttemptsRef.current++;

    reconnectTimerRef.current = setTimeout(() => {
      reconnectTimerRef.current = null;
      connectWebSocket(token);
    }, delay);
  }, [connectWebSocket]);

  const disconnectWebSocket = useCallback(() => {
    if (reconnectTimerRef.current) {
      clearTimeout(reconnectTimerRef.current);
      reconnectTimerRef.current = null;
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
    setWsConnected(false);
  }, []);

  useEffect(() => {
    return () => {
      disconnectWebSocket();
    };
  }, [disconnectWebSocket]);

  const value = {
    notifications,
    unreadCount,
    wsConnected,
    addNotification,
    markAsRead,
    markAllAsRead,
    clearNotifications,
    removeNotification,
    connectWebSocket,
    disconnectWebSocket,
  };

  return (
    <NotificationContext.Provider value={value}>
      {children}
    </NotificationContext.Provider>
  );
}

export function useNotifications() {
  const context = useContext(NotificationContext);
  if (!context) {
    throw new Error('useNotifications must be used within NotificationProvider');
  }
  return context;
}
