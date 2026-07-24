'use client';
import { useState } from 'react';
import {
  Card,
  CardContent,
  Avatar,
  Typography,
  Box,
  IconButton,
  Chip,
  Menu,
  MenuItem,
  ListItemIcon,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Button,
  TextField,
} from '@mui/material';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import EmailIcon from '@mui/icons-material/Email';
import { getInitials } from '@/utils/helpers';

const roleColors = {
  admin: 'error',
  editor: 'primary',
  viewer: 'default',
};

export default function TeamMemberCard({ member, onEdit, onDelete }) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [editDialog, setEditDialog] = useState(false);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [role, setRole] = useState(member?.role || 'viewer');

  const handleMenuClose = () => setAnchorEl(null);

  const handleEdit = () => {
    handleMenuClose();
    setEditDialog(true);
  };

  const handleDelete = () => {
    handleMenuClose();
    setDeleteDialog(true);
  };

  const handleSaveRole = () => {
    if (onEdit) onEdit(member._id || member.id, { ...member, role });
    setEditDialog(false);
  };

  const handleConfirmDelete = () => {
    if (onDelete) onDelete(member._id || member.id);
    setDeleteDialog(false);
  };

  return (
    <>
      <Card
        sx={{
          borderRadius: 3,
          transition: 'all 0.2s',
          '&:hover': { transform: 'translateY(-2px)', boxShadow: 4 },
        }}
      >
        <CardContent sx={{ p: 3, '&:last-child': { pb: 3 } }}>
          <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
              <Avatar
                sx={{
                  width: 48,
                  height: 48,
                  bgcolor: 'primary.main',
                  fontWeight: 600,
                }}
              >
                {getInitials(member.name || member.email)}
              </Avatar>
              <Box>
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {member.name || 'Team Member'}
                </Typography>
                <Typography variant="caption" color="text.secondary" sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 0.3 }}>
                  <EmailIcon sx={{ fontSize: 14 }} />
                  {member.email}
                </Typography>
              </Box>
            </Box>
            <IconButton size="small" onClick={(e) => setAnchorEl(e.currentTarget)}>
              <MoreVertIcon fontSize="small" />
            </IconButton>
          </Box>

          <Box sx={{ mt: 2, display: 'flex', alignItems: 'center', gap: 1 }}>
            <Chip
              label={member.role || 'viewer'}
              size="small"
              color={roleColors[member.role] || 'default'}
              sx={{ fontWeight: 500, textTransform: 'capitalize' }}
            />
            {member.status === 'pending' && (
              <Chip label="Pending" size="small" variant="outlined" color="warning" />
            )}
          </Box>
        </CardContent>
      </Card>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={handleMenuClose}>
        <MenuItem onClick={handleEdit}>
          <ListItemIcon><EditIcon fontSize="small" /></ListItemIcon>
          Edit Role
        </MenuItem>
        <MenuItem onClick={handleDelete} sx={{ color: 'error.main' }}>
          <ListItemIcon><DeleteIcon fontSize="small" color="error" /></ListItemIcon>
          Remove
        </MenuItem>
      </Menu>

      <Dialog open={editDialog} onClose={() => setEditDialog(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Edit Team Member Role</DialogTitle>
        <DialogContent>
          <TextField
            select
            fullWidth
            label="Role"
            value={role}
            onChange={(e) => setRole(e.target.value)}
            sx={{ mt: 1 }}
            SelectProps={{ native: true }}
          >
            <option value="admin">Admin</option>
            <option value="editor">Editor</option>
            <option value="viewer">Viewer</option>
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={handleSaveRole}>Save</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialog} onClose={() => setDeleteDialog(false)} maxWidth="xs" fullWidth>
        <DialogTitle>Remove Team Member</DialogTitle>
        <DialogContent>
          <Typography>Are you sure you want to remove {member.name || member.email}?</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialog(false)}>Cancel</Button>
          <Button variant="contained" color="error" onClick={handleConfirmDelete}>Remove</Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
