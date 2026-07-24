'use client';
import { useState, useEffect, useCallback } from 'react';
import { Box, Typography, TextField, Button, MenuItem, Grid, Alert, Dialog, DialogTitle, DialogContent, DialogActions, Chip, IconButton, Avatar } from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import SendIcon from '@mui/icons-material/Send';
import DataTable from '@/components/admin/DataTable';
import StatusBadge from '@/components/admin/StatusBadge';
import { formatDate, formatDateTime, formatRelativeTime } from '@/utils/formatters';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';
import ConfirmDialog from '@/components/admin/ConfirmDialog';

export default function AdminSupportPage() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [statusFilter, setStatusFilter] = useState('all');
  const [priorityFilter, setPriorityFilter] = useState('all');
  const [page, setPage] = useState(0);
  const [rowsPerPage, setRowsPerPage] = useState(10);
  const [total, setTotal] = useState(0);
  const [ticketDetail, setTicketDetail] = useState(null);
  const [detailOpen, setDetailOpen] = useState(false);
  const [replyText, setReplyText] = useState('');
  const [sending, setSending] = useState(false);
  const [kbArticles, setKbArticles] = useState([]);
  const [kbOpen, setKbOpen] = useState(false);
  const [kbForm, setKbForm] = useState({ title: '', content: '', category: '' });
  const [editingKb, setEditingKb] = useState(null);

  const fetchTickets = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = { page: page + 1, limit: rowsPerPage, status: statusFilter !== 'all' ? statusFilter : undefined, priority: priorityFilter !== 'all' ? priorityFilter : undefined };
      const { data } = await adminService.getTickets(params);
      setTickets(data.tickets || data.data || data || []);
      setTotal(data.total || 0);
    } catch (err) {
      setError(err.message || 'Failed to load tickets');
    } finally { setLoading(false); }
  }, [page, rowsPerPage, statusFilter, priorityFilter]);

  useEffect(() => { fetchTickets(); }, [fetchTickets]);

  const openDetail = async (ticket) => {
    try {
      const { data } = await adminService.getTicketById(ticket._id || ticket.id);
      setTicketDetail(data);
      setDetailOpen(true);
    } catch { toast.error('Failed to load ticket'); }
  };

  const handleReply = async () => {
    if (!replyText.trim() || !ticketDetail) return;
    setSending(true);
    try {
      await adminService.addTicketReply(ticketDetail._id || ticketDetail.id, { message: replyText });
      toast.success('Reply sent');
      setReplyText('');
      const { data } = await adminService.getTicketById(ticketDetail._id || ticketDetail.id);
      setTicketDetail(data);
    } catch (err) { toast.error(err.message || 'Failed to send reply'); }
    finally { setSending(false); }
  };

  const handleStatusUpdate = async (status) => {
    if (!ticketDetail) return;
    try {
      await adminService.updateTicket(ticketDetail._id || ticketDetail.id, { status });
      toast.success(`Ticket ${status}`);
      setDetailOpen(false);
      fetchTickets();
    } catch (err) { toast.error(err.message || 'Update failed'); }
  };

  const loadKb = async () => {
    try {
      const { data } = await adminService.getKnowledgeBase({ limit: 100 });
      setKbArticles(data.articles || data.data || data || []);
    } catch {}
  };

  const handleSaveKb = async () => {
    if (!kbForm.title || !kbForm.content) return;
    try {
      if (editingKb) {
        await adminService.updateKnowledgeArticle(editingKb._id || editingKb.id, kbForm);
        toast.success('Article updated');
      } else {
        await adminService.createKnowledgeArticle(kbForm);
        toast.success('Article created');
      }
      setKbForm({ title: '', content: '', category: '' });
      setEditingKb(null);
      loadKb();
    } catch (err) { toast.error('Failed to save article'); }
  };

  const columns = [
    { key: 'subject', label: 'Subject', render: (row) => <Box><Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{row.subject}</Typography><Typography variant="caption" sx={{ color: '#64748B' }}>{row.user?.name || row.name}</Typography></Box> },
    { key: 'priority', label: 'Priority', render: (row) => <StatusBadge status={row.priority} /> },
    { key: 'status', label: 'Status', render: (row) => <StatusBadge status={row.status} /> },
    { key: 'assignedTo', label: 'Assigned', render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{row.assignedTo?.name || row.assignedTo || 'Unassigned'}</Typography> },
    { key: 'updatedAt', label: 'Updated', sortable: true, render: (row) => <Typography variant="body2" sx={{ color: '#94A3B8' }}>{formatRelativeTime(row.updatedAt)}</Typography> },
  ];

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Support Tickets</Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button startIcon={<AddIcon />} onClick={() => { setKbOpen(true); loadKb(); }} sx={{ color: '#94A3B8', '&:hover': { color: '#818CF8' } }}>Knowledge Base</Button>
        </Box>
      </Box>

      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={6} md={3}>
          <TextField select fullWidth label="Status" value={statusFilter} onChange={(e) => { setStatusFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Status</MenuItem>
            <MenuItem value="open">Open</MenuItem>
            <MenuItem value="in_progress">In Progress</MenuItem>
            <MenuItem value="resolved">Resolved</MenuItem>
            <MenuItem value="closed">Closed</MenuItem>
          </TextField>
        </Grid>
        <Grid item xs={6} md={3}>
          <TextField select fullWidth label="Priority" value={priorityFilter} onChange={(e) => { setPriorityFilter(e.target.value); setPage(0); }}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }}>
            <MenuItem value="all">All Priority</MenuItem>
            <MenuItem value="low">Low</MenuItem>
            <MenuItem value="medium">Medium</MenuItem>
            <MenuItem value="high">High</MenuItem>
            <MenuItem value="urgent">Urgent</MenuItem>
          </TextField>
        </Grid>
      </Grid>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      <DataTable columns={columns} rows={tickets} loading={loading} onRetry={fetchTickets}
        page={page} rowsPerPage={rowsPerPage} total={total}
        onPageChange={setPage} onRowsPerPageChange={setRowsPerPage}
        onRowClick={(row) => openDetail(row)}
        emptyTitle="No tickets found" emptyDescription="No support tickets match your filters" />

      <Dialog open={detailOpen} onClose={() => setDetailOpen(false)} maxWidth="md" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        {ticketDetail && (
          <>
            <DialogTitle sx={{ borderBottom: '1px solid rgba(255,255,255,0.06)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <Box>
                <Typography variant="h6" sx={{ fontWeight: 600 }}>{ticketDetail.subject}</Typography>
                <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                  <StatusBadge status={ticketDetail.status} />
                  <StatusBadge status={ticketDetail.priority} />
                </Box>
              </Box>
            </DialogTitle>
            <DialogContent sx={{ pt: 2 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2, pb: 2, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                <Avatar sx={{ width: 32, height: 32, bgcolor: '#818CF8', fontSize: '0.875rem' }}>{ticketDetail.user?.name?.[0] || 'U'}</Avatar>
                <Box>
                  <Typography variant="body2" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{ticketDetail.user?.name || 'User'}</Typography>
                  <Typography variant="caption" sx={{ color: '#64748B' }}>{formatDateTime(ticketDetail.createdAt)}</Typography>
                </Box>
              </Box>
              <Typography variant="body2" sx={{ color: '#CBD5E1', mb: 3, whiteSpace: 'pre-wrap' }}>{ticketDetail.description}</Typography>

              {(ticketDetail.replies || ticketDetail.conversation) && (
                <Box sx={{ mb: 3 }}>
                  <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 2, color: '#94A3B8', textTransform: 'uppercase', fontSize: '0.75rem' }}>Conversation</Typography>
                  {(ticketDetail.replies || ticketDetail.conversation).map((reply, i) => (
                    <Box key={i} sx={{ display: 'flex', gap: 1.5, mb: 2, p: 2, borderRadius: 2, bgcolor: reply.isAdmin ? 'rgba(129,140,248,0.08)' : 'rgba(255,255,255,0.03)' }}>
                      <Avatar sx={{ width: 28, height: 28, bgcolor: reply.isAdmin ? '#818CF8' : '#64748B', fontSize: '0.75rem' }}>{reply.user?.name?.[0] || (reply.isAdmin ? 'A' : 'U')}</Avatar>
                      <Box sx={{ flex: 1 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                          <Typography variant="caption" sx={{ fontWeight: 600, color: '#F1F5F9' }}>{reply.user?.name || (reply.isAdmin ? 'Admin' : 'User')}</Typography>
                          <Typography variant="caption" sx={{ color: '#64748B' }}>{formatRelativeTime(reply.createdAt)}</Typography>
                        </Box>
                        <Typography variant="body2" sx={{ color: '#CBD5E1' }}>{reply.message || reply.text}</Typography>
                      </Box>
                    </Box>
                  ))}
                </Box>
              )}

              <TextField fullWidth multiline rows={3} placeholder="Type your reply..." value={replyText} onChange={(e) => setReplyText(e.target.value)}
                sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }} />
            </DialogContent>
            <DialogActions sx={{ p: 2, borderTop: '1px solid rgba(255,255,255,0.06)', gap: 1 }}>
              <Button startIcon={<SendIcon />} variant="contained" onClick={handleReply} disabled={!replyText.trim() || sending}
                sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>{sending ? 'Sending...' : 'Send Reply'}</Button>
              <Button onClick={() => handleStatusUpdate('resolved')} sx={{ color: '#4ADE80' }}>Resolve</Button>
              <Button onClick={() => handleStatusUpdate('closed')} sx={{ color: '#94A3B8' }}>Close</Button>
            </DialogActions>
          </>
        )}
      </Dialog>

      <Dialog open={kbOpen} onClose={() => setKbOpen(false)} maxWidth="md" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Knowledge Base</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap' }}>
            <TextField size="small" label="Title" value={kbForm.title} onChange={(e) => setKbForm({ ...kbForm, title: e.target.value })}
              sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
            <TextField size="small" label="Category" value={kbForm.category} onChange={(e) => setKbForm({ ...kbForm, category: e.target.value })}
              sx={{ flex: 1, minWidth: 200, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
            <Button variant="contained" onClick={handleSaveKb} disabled={!kbForm.title || !kbForm.content}
              sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' }, flexShrink: 0 }}>
              {editingKb ? 'Update' : 'Add Article'}
            </Button>
          </Box>
          <TextField fullWidth multiline rows={6} placeholder="Article content (markdown supported)..." value={kbForm.content} onChange={(e) => setKbForm({ ...kbForm, content: e.target.value })}
            sx={{ mb: 3, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }} />
          <Typography variant="subtitle2" sx={{ fontWeight: 600, mb: 1, color: '#94A3B8' }}>Existing Articles</Typography>
          {kbArticles.length > 0 ? kbArticles.map((article, i) => (
            <Box key={i} sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', p: 1.5, borderRadius: 2, bgcolor: 'rgba(255,255,255,0.03)', mb: 1 }}>
              <Box>
                <Typography variant="body2" sx={{ color: '#F1F5F9', fontWeight: 500 }}>{article.title}</Typography>
                <Typography variant="caption" sx={{ color: '#64748B' }}>{article.category} &middot; {article.slug}</Typography>
              </Box>
              <Box sx={{ display: 'flex', gap: 0.5 }}>
                <Chip label="Edit" size="small" onClick={() => setKbForm({ title: article.title, content: article.content, category: article.category })}
                  sx={{ color: '#60A5FA', bgcolor: 'rgba(96,165,250,0.15)', cursor: 'pointer' }} />
                <Chip label="Delete" size="small" onClick={async () => { try { await adminService.deleteKnowledgeArticle(article._id || article.id); loadKb(); toast.success('Deleted'); } catch {} }}
                  sx={{ color: '#F87171', bgcolor: 'rgba(248,113,113,0.15)', cursor: 'pointer' }} />
              </Box>
            </Box>
          )) : <Typography variant="body2" sx={{ color: '#64748B', textAlign: 'center', py: 2 }}>No articles yet</Typography>}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setKbOpen(false)} sx={{ color: '#94A3B8' }}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
