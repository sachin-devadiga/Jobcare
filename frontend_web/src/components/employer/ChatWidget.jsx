'use client';
import { useState, useEffect, useRef, useCallback } from 'react';
import {
  Box, TextField, IconButton, Typography, Avatar, Badge,
  Paper, InputAdornment, CircularProgress, Divider, ClickAwayListener,
} from '@mui/material';
import SendIcon from '@mui/icons-material/Send';
import CloseIcon from '@mui/icons-material/Close';
import ChatIcon from '@mui/icons-material/Chat';
import AttachFileIcon from '@mui/icons-material/AttachFile';
import InsertEmoticonIcon from '@mui/icons-material/InsertEmoticon';
import api from '@/services/api';
import { formatRelativeTime } from '@/utils/formatters';
import { getInitials, getAvatarColor } from '@/utils/helpers';

export default function ChatWidget({ token, currentUserId, currentUserName }) {
  const [open, setOpen] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [activeConv, setActiveConv] = useState(null);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const [wsConnected, setWsConnected] = useState(false);
  const [typingUsers, setTypingUsers] = useState({});
  const wsRef = useRef(null);
  const messagesEndRef = useRef(null);
  const typingTimerRef = useRef(null);

  const scrollToBottom = useCallback(() => {
    setTimeout(() => messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' }), 100);
  }, []);

  useEffect(() => {
    if (open && !wsRef.current) {
      connectWebSocket();
    }
    return () => {};
  }, [open]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  const connectWebSocket = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return;
    const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000';
    try {
      const ws = new WebSocket(`${wsUrl}/ws/chat/?token=${token}`);
      ws.onopen = () => setWsConnected(true);
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleWsMessage(data);
        } catch {}
      };
      ws.onclose = () => {
        setWsConnected(false);
        setTimeout(() => connectWebSocket(), 3000);
      };
      ws.onerror = () => setWsConnected(false);
      wsRef.current = ws;
    } catch {}
  }, [token]);

  const handleWsMessage = (data) => {
    if (data.type === 'new_message') {
      const msg = data.data;
      setMessages((prev) => [...prev, msg]);
      setConversations((prev) =>
        prev.map((c) =>
          c.id === msg.conversation_id
            ? { ...c, last_message: msg, last_message_at: msg.created_at }
            : c
        )
      );
    } else if (data.type === 'messages_read') {
      setMessages((prev) =>
        prev.map((m) =>
          m.sender_id !== currentUserId && m.conversation_id === data.data.conversation_id
            ? { ...m, is_read: true }
            : m
        )
      );
    } else if (data.type === 'typing_start') {
      setTypingUsers((prev) => ({ ...prev, [data.data.user_id]: true }));
    } else if (data.type === 'typing_stop') {
      setTypingUsers((prev) => ({ ...prev, [data.data.user_id]: false }));
    }
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
      markAsRead(convId);
    } catch {}
  };

  const markAsRead = async (convId) => {
    try {
      await api.post('/chat/messages/mark-read/', { conversation_id: convId });
      sendWsMessage('mark_read', { conversation_id: convId });
    } catch {}
  };

  const handleSelectConversation = (conv) => {
    setActiveConv(conv);
    loadMessages(conv.id);
  };

  const handleSend = async () => {
    if (!input.trim() || !activeConv) return;
    const content = input.trim();
    setInput('');

    sendWsMessage('send_message', {
      conversation_id: activeConv.id,
      content,
      message_type: 'text',
    });

    try {
      await api.post(`/chat/conversations/${activeConv.id}/messages/`, {
        content,
        message_type: 'text',
      });
    } catch {}
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleTyping = () => {
    if (!activeConv) return;
    sendWsMessage('typing_start', { conversation_id: activeConv.id });
    clearTimeout(typingTimerRef.current);
    typingTimerRef.current = setTimeout(() => {
      sendWsMessage('typing_stop', { conversation_id: activeConv.id });
    }, 2000);
  };

  const getOtherParticipant = (conv) => conv?.other_participant;

  return (
    <Box sx={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999 }}>
      {open ? (
        <ClickAwayListener onClickAway={() => setOpen(false)}>
          <Paper
            elevation={8}
            sx={{
              width: 380,
              height: 560,
              display: 'flex',
              flexDirection: 'column',
              borderRadius: 3,
              overflow: 'hidden',
              bgcolor: 'background.paper',
            }}
          >
            <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
                <ChatIcon />
                <Box>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                    {activeConv ? getOtherParticipant(activeConv)?.name || 'Chat' : 'Messages'}
                  </Typography>
                  <Typography variant="caption" sx={{ opacity: 0.8 }}>
                    {wsConnected ? 'Online' : 'Connecting...'}
                  </Typography>
                </Box>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                {activeConv && (
                  <IconButton size="small" sx={{ color: 'white' }} onClick={() => { setActiveConv(null); loadConversations(); }}>
                    <Typography variant="caption" sx={{ mr: 0.5 }}>Back</Typography>
                  </IconButton>
                )}
                <IconButton size="small" sx={{ color: 'white' }} onClick={() => setOpen(false)}>
                  <CloseIcon fontSize="small" />
                </IconButton>
              </Box>
            </Box>

            <Box sx={{ flex: 1, display: 'flex', overflow: 'hidden' }}>
              {!activeConv ? (
                <Box sx={{ flex: 1, overflow: 'auto' }}>
                  {loading ? (
                    <Box sx={{ display: 'flex', justifyContent: 'center', p: 4 }}>
                      <CircularProgress size={24} />
                    </Box>
                  ) : conversations.length === 0 ? (
                    <Box sx={{ p: 4, textAlign: 'center' }}>
                      <Typography variant="body2" color="text.secondary">No conversations</Typography>
                    </Box>
                  ) : (
                    conversations.map((conv) => {
                      const other = getOtherParticipant(conv);
                      return (
                        <Box
                          key={conv.id}
                          onClick={() => handleSelectConversation(conv)}
                          sx={{
                            display: 'flex', gap: 1.5, p: 2, cursor: 'pointer',
                            borderBottom: '1px solid', borderColor: 'divider',
                            '&:hover': { bgcolor: 'action.hover' },
                          }}
                        >
                          <Badge color="success" variant="dot" invisible={!conv.is_online} overlap="circular">
                            <Avatar sx={{ bgcolor: getAvatarColor(other?.name), width: 40, height: 40 }}>
                              {getInitials(other?.name)}
                            </Avatar>
                          </Badge>
                          <Box sx={{ flex: 1, minWidth: 0 }}>
                            <Typography variant="subtitle2" noWrap>{other?.name || 'Unknown'}</Typography>
                            <Typography variant="body2" color="text.secondary" noWrap sx={{ fontSize: 13 }}>
                              {conv.last_message?.content || 'No messages'}
                            </Typography>
                          </Box>
                          <Box sx={{ textAlign: 'right', flexShrink: 0 }}>
                            <Typography variant="caption" color="text.disabled">
                              {conv.last_message_at ? formatRelativeTime(conv.last_message_at) : ''}
                            </Typography>
                            {conv.unread_count > 0 && (
                              <Box sx={{ mt: 0.5, bgcolor: 'primary.main', borderRadius: '50%', width: 20, height: 20, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                                <Typography variant="caption" sx={{ color: 'white', fontSize: 11 }}>{conv.unread_count}</Typography>
                              </Box>
                            )}
                          </Box>
                        </Box>
                      );
                    })
                  )}
                </Box>
              ) : (
                <Box sx={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
                  <Box sx={{ flex: 1, overflow: 'auto', p: 2, bgcolor: 'grey.50' }}>
                    {messages.map((msg, i) => {
                      const isMe = msg.sender_id === currentUserId;
                      return (
                        <Box key={msg.id || i} sx={{ display: 'flex', justifyContent: isMe ? 'flex-end' : 'flex-start', mb: 1.5 }}>
                          <Box sx={{ maxWidth: '75%', px: 2, py: 1, borderRadius: 2, bgcolor: isMe ? 'primary.main' : 'background.paper', color: isMe ? 'white' : 'text.primary', boxShadow: 1 }}>
                            <Typography variant="body2">{msg.content}</Typography>
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5, mt: 0.5 }}>
                              <Typography variant="caption" sx={{ color: isMe ? 'rgba(255,255,255,0.7)' : 'text.disabled', fontSize: 10 }}>
                                {msg.created_at ? formatRelativeTime(msg.created_at) : ''}
                              </Typography>
                              {isMe && (
                                <Typography variant="caption" sx={{ color: msg.is_read ? 'success.light' : 'rgba(255,255,255,0.5)', fontSize: 12 }}>
                                  {msg.is_read ? '✓✓' : '✓'}
                                </Typography>
                              )}
                            </Box>
                          </Box>
                        </Box>
                      );
                    })}
                    {typingUsers[getOtherParticipant(activeConv)?.id] && (
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, color: 'text.secondary' }}>
                        <Typography variant="caption" sx={{ fontStyle: 'italic' }}>typing...</Typography>
                      </Box>
                    )}
                    <div ref={messagesEndRef} />
                  </Box>
                  <Divider />
                  <Box sx={{ p: 1.5, display: 'flex', alignItems: 'flex-end', gap: 1 }}>
                    <IconButton size="small"><AttachFileIcon fontSize="small" /></IconButton>
                    <TextField
                      fullWidth
                      size="small"
                      placeholder="Type a message..."
                      value={input}
                      onChange={(e) => { setInput(e.target.value); handleTyping(); }}
                      onKeyDown={handleKeyDown}
                      multiline
                      maxRows={4}
                      variant="outlined"
                      sx={{ '& fieldset': { border: 'none' }, bgcolor: 'grey.100', borderRadius: 2 }}
                    />
                    <IconButton color="primary" onClick={handleSend} disabled={!input.trim()}>
                      <SendIcon />
                    </IconButton>
                  </Box>
                </Box>
              )}
            </Box>
          </Paper>
        </ClickAwayListener>
      ) : (
        <IconButton
          onClick={() => { setOpen(true); loadConversations(); }}
          sx={{
            width: 56, height: 56, bgcolor: 'primary.main', color: 'white',
            '&:hover': { bgcolor: 'primary.dark' },
            boxShadow: 4,
          }}
        >
          <ChatIcon />
        </IconButton>
      )}
    </Box>
  );
}
