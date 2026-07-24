'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box, Typography, TextField, InputAdornment, Paper, Avatar, Badge,
  IconButton, Divider, CircularProgress,
} from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import SearchIcon from '@mui/icons-material/Search';
import SendIcon from '@mui/icons-material/Send';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import { getInitials, getAvatarColor } from '@/utils/helpers';
import { formatRelativeTime } from '@/utils/formatters';
import api from '@/services/api';

export default function MessagesPage() {
  const [search, setSearch] = useState('');
  const [conversations, setConversations] = useState([]);
  const [selected, setSelected] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(true);
  const [wsConnected, setWsConnected] = useState(false);
  const [typingUsers, setTypingUsers] = useState({});
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const typingTimerRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  }, []);

  useEffect(() => {
    loadConversations();
    connectWebSocket();
    return () => wsRef.current?.close();
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);

  const getToken = () => {
    if (typeof window === 'undefined') return '';
    return localStorage.getItem('accessToken') || '';
  };

  const connectWebSocket = () => {
    const token = getToken();
    if (!token || wsRef.current?.readyState === WebSocket.OPEN) return;
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    try {
      const ws = new WebSocket(`${wsUrl}/ws/chat/?token=${token}`);
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === 'new_message' && selected?.id === data.data?.conversation_id) {
            setMessages((prev) => [...prev, data.data]);
          } else if (data.type === 'messages_read') {
            setMessages((prev) => prev.map((m) => m.sender_id !== m.sender_id ? { ...m, is_read: true } : m));
          } else if (data.type === 'typing_start') {
            setTypingUsers((prev) => ({ ...prev, [data.data.user_id]: true }));
          } else if (data.type === 'typing_stop') {
            setTypingUsers((prev) => ({ ...prev, [data.data.user_id]: false }));
          }
        } catch {}
      };
      ws.onclose = () => { setWsConnected(false); setTimeout(() => connectWebSocket(), 3000); };
      ws.onerror = () => setWsConnected(false);
      wsRef.current = ws;
    } catch {}
  };

  const sendWsMessage = (type, payload) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ type, ...payload }));
    }
  };

  const loadConversations = async () => {
    setLoading(true);
    try {
      const { data } = await api.get('/chat/conversations/');
      setConversations(data?.data?.results || []);
    } catch {} finally {
      setLoading(false);
    }
  };

  const loadMessages = async (convId) => {
    try {
      const { data } = await api.get(`/chat/conversations/${convId}/messages/`);
      setMessages(data?.data?.results || []);
      await api.post('/chat/messages/mark-read/', { conversation_id: convId });
      sendWsMessage('mark_read', { conversation_id: convId });
    } catch {}
  };

  const handleSelect = (conv) => {
    setSelected(conv);
    loadMessages(conv.id);
    setConversations((prev) => prev.map((c) => c.id === conv.id ? { ...c, unread_count: 0 } : c));
  };

  const handleSend = async () => {
    if (!input.trim() || !selected) return;
    const content = input.trim();
    setInput('');

    sendWsMessage('send_message', { conversation_id: selected.id, content, message_type: 'text' });

    try {
      const { data } = await api.post(`/chat/conversations/${selected.id}/messages/`, { content, message_type: 'text' });
      const newMsg = data?.data;
      if (newMsg) setMessages((prev) => [...prev, newMsg]);
    } catch {}
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  const handleTyping = () => {
    if (!selected) return;
    sendWsMessage('typing_start', { conversation_id: selected.id });
    clearTimeout(typingTimerRef.current);
    typingTimerRef.current = setTimeout(() => {
      sendWsMessage('typing_stop', { conversation_id: selected.id });
    }, 2000);
  };

  const filtered = conversations.filter((c) => {
    const name = c.other_participant?.name || '';
    return name.toLowerCase().includes(search.toLowerCase());
  });

  const currentUserId = typeof window !== 'undefined' ? JSON.parse(localStorage.getItem('user') || '{}')?.id : null;

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3 }}>
        <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Messages</Typography>
        <Typography variant="body2" color="text.secondary">Communicate with your applicants</Typography>
      </Box>

      <Paper sx={{ display: 'flex', borderRadius: 3, overflow: 'hidden', minHeight: 600, border: '1px solid', borderColor: 'divider' }}>
        <Box sx={{ width: 360, borderRight: '1px solid', borderColor: 'divider', flexShrink: 0, display: 'flex', flexDirection: 'column' }}>
          <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 1 }}>
            <TextField
              fullWidth size="small"
              placeholder="Search conversations..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              InputProps={{
                startAdornment: <InputAdornment position="start"><SearchIcon sx={{ fontSize: 20, color: 'text.secondary' }} /></InputAdornment>,
              }}
            />
            <Badge color="success" variant="dot" invisible={!wsConnected}>
              <Typography variant="caption" color="text.disabled">{wsConnected ? '' : ''}</Typography>
            </Badge>
          </Box>
          <Box sx={{ flex: 1, overflow: 'auto' }}>
            {loading ? (
              <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}><CircularProgress size={24} /></Box>
            ) : filtered.length === 0 ? (
              <Box sx={{ p: 4, textAlign: 'center' }}>
                <Typography color="text.secondary">No messages yet</Typography>
                <Typography variant="body2" color="text.disabled" sx={{ mt: 1 }}>Messages from applicants will appear here</Typography>
              </Box>
            ) : (
              filtered.map((conv) => {
                const other = conv.other_participant || {};
                return (
                  <Box
                    key={conv.id}
                    onClick={() => handleSelect(conv)}
                    sx={{
                      display: 'flex', gap: 2, p: 2, cursor: 'pointer',
                      bgcolor: selected?.id === conv.id ? 'action.selected' : 'transparent',
                      borderBottom: '1px solid', borderColor: 'divider',
                      '&:hover': { bgcolor: 'action.hover' },
                    }}
                  >
                    <Badge color="success" variant="dot" invisible={!conv.is_online} overlap="circular">
                      <Avatar sx={{ bgcolor: getAvatarColor(other.name), width: 44, height: 44 }}>
                        {getInitials(other.name)}
                      </Avatar>
                    </Badge>
                    <Box sx={{ flex: 1, minWidth: 0 }}>
                      <Typography variant="subtitle2" sx={{ fontWeight: conv.unread_count ? 700 : 500 }}>
                        {other.name || 'Unknown'}
                      </Typography>
                      <Typography variant="body2" color="text.secondary" noWrap>{conv.last_message?.content || 'No messages'}</Typography>
                      <Typography variant="caption" color="text.disabled">
                        {conv.last_message_at ? formatRelativeTime(conv.last_message_at) : ''}
                      </Typography>
                    </Box>
                    {conv.unread_count > 0 && (
                      <Badge badgeContent={conv.unread_count} color="primary" />
                    )}
                  </Box>
                );
              })
            )}
          </Box>
        </Box>

        {selected ? (
          <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
            <Box sx={{ p: 2, borderBottom: '1px solid', borderColor: 'divider', display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar sx={{ bgcolor: getAvatarColor(selected.other_participant?.name), width: 40, height: 40 }}>
                {getInitials(selected.other_participant?.name)}
              </Avatar>
              <Box>
                <Typography variant="subtitle2">{selected.other_participant?.name || 'Chat'}</Typography>
                <Typography variant="caption" color={wsConnected ? 'success.main' : 'text.disabled'}>
                  {wsConnected ? 'Online' : 'Offline'}
                </Typography>
              </Box>
            </Box>
            <Box sx={{ flex: 1, overflow: 'auto', p: 3, bgcolor: 'grey.50' }}>
              {messages.map((msg, i) => {
                const isMe = msg.sender_id === currentUserId || msg.sender === currentUserId;
                return (
                  <Box key={msg.id || i} sx={{ display: 'flex', justifyContent: isMe ? 'flex-end' : 'flex-start', mb: 2 }}>
                    <Box sx={{ maxWidth: '70%', px: 2.5, py: 1.5, borderRadius: 3, bgcolor: isMe ? 'primary.main' : 'background.paper', color: isMe ? 'white' : 'text.primary', boxShadow: 1 }}>
                      <Typography variant="body2">{msg.content}</Typography>
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5, mt: 0.5 }}>
                        <Typography variant="caption" sx={{ color: isMe ? 'rgba(255,255,255,0.7)' : 'text.disabled' }}>
                          {msg.created_at ? formatRelativeTime(msg.created_at) : ''}
                        </Typography>
                        {isMe && (
                          <Typography variant="caption" sx={{ color: msg.is_read ? 'success.light' : 'rgba(255,255,255,0.5)' }}>
                            {msg.is_read ? '✓✓' : '✓'}
                          </Typography>
                        )}
                      </Box>
                    </Box>
                  </Box>
                );
              })}
              {typingUsers[selected.other_participant?.id] && (
                <Typography variant="caption" color="text.secondary" sx={{ fontStyle: 'italic' }}>typing...</Typography>
              )}
              <div ref={messagesEndRef} />
            </Box>
            <Divider />
            <Box sx={{ p: 2, display: 'flex', alignItems: 'flex-end', gap: 1 }}>
              <IconButton size="small"><AttachFileIcon /></IconButton>
              <TextField
                fullWidth size="small" placeholder="Type a message..."
                value={input}
                onChange={(e) => { setInput(e.target.value); handleTyping(); }}
                onKeyDown={handleKeyDown}
                multiline maxRows={4}
                sx={{ '& fieldset': { border: 'none' }, bgcolor: 'grey.100', borderRadius: 2 }}
              />
              <IconButton color="primary" onClick={handleSend} disabled={!input.trim()}><SendIcon /></IconButton>
            </Box>
          </Box>
        ) : (
          <Box sx={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', bgcolor: 'action.hover' }}>
            <Box sx={{ textAlign: 'center' }}>
              <Typography variant="h6" color="text.disabled">Select a conversation</Typography>
              <Typography variant="body2" color="text.disabled">Choose a conversation from the left to start messaging</Typography>
            </Box>
          </Box>
        )}
      </Paper>
    </DashboardLayout>
  );
}
