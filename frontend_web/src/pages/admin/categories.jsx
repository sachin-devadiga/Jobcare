'use client';
import { useState, useEffect, useCallback } from 'react';
import {
  Box, Typography, TextField, Button, Dialog, DialogTitle, DialogContent, DialogActions,
  Grid, Card, CardContent, IconButton, Chip, Alert, Avatar, List, ListItem, ListItemText,
} from '@mui/material';
import AddIcon from '@mui/icons-material/Add';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import DragIndicatorIcon from '@mui/icons-material/DragIndicator';
import adminService from '@/services/adminService';
import { toast } from 'react-toastify';

export default function AdminCategoriesPage() {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [dialogOpen, setDialogOpen] = useState(false);
  const [editingCat, setEditingCat] = useState(null);
  const [formData, setFormData] = useState({ name: '', description: '', icon: '' });
  const [skillsDialogOpen, setSkillsDialogOpen] = useState(false);
  const [skillsCat, setSkillsCat] = useState(null);
  const [skills, setSkills] = useState([]);
  const [newSkill, setNewSkill] = useState('');
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState(null);

  const fetchCategories = useCallback(async () => {
    setLoading(true);
    try {
      const { data } = await adminService.getCategories({ limit: 100 });
      setCategories(data.categories || data.data || data || []);
    } catch (err) {
      setError(err.message || 'Failed to load categories');
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchCategories(); }, [fetchCategories]);

  const openEdit = (cat = null) => {
    setEditingCat(cat);
    setFormData(cat ? { name: cat.name, description: cat.description || '', icon: cat.icon || '' } : { name: '', description: '', icon: '' });
    setDialogOpen(true);
  };

  const handleSave = async () => {
    if (!formData.name) return;
    try {
      if (editingCat) {
        await adminService.updateCategory(editingCat._id || editingCat.id, formData);
        toast.success('Category updated');
      } else {
        await adminService.createCategory(formData);
        toast.success('Category created');
      }
      setDialogOpen(false);
      fetchCategories();
    } catch (err) { toast.error(err.message || 'Failed to save category'); }
  };

  const handleDelete = async () => {
    if (!deleteTarget) return;
    try {
      await adminService.deleteCategory(deleteTarget._id || deleteTarget.id);
      toast.success('Category deleted');
      setDeleteDialogOpen(false);
      setDeleteTarget(null);
      fetchCategories();
    } catch (err) { toast.error(err.message || 'Failed to delete'); }
  };

  const openSkills = async (cat) => {
    setSkillsCat(cat);
    try {
      const { data } = await adminService.getCategorySkills(cat._id || cat.id);
      setSkills(data.skills || data || []);
    } catch { setSkills([]); }
    setSkillsDialogOpen(true);
  };

  const addSkill = async () => {
    if (!newSkill.trim() || !skillsCat) return;
    const updatedSkills = [...skills, { name: newSkill.trim() }];
    try {
      await adminService.updateCategorySkills(skillsCat._id || skillsCat.id, { skills: updatedSkills });
      setSkills(updatedSkills);
      setNewSkill('');
      toast.success('Skill added');
    } catch (err) { toast.error('Failed to add skill'); }
  };

  const removeSkill = async (index) => {
    const updatedSkills = skills.filter((_, i) => i !== index);
    try {
      await adminService.updateCategorySkills(skillsCat._id || skillsCat.id, { skills: updatedSkills });
      setSkills(updatedSkills);
      toast.success('Skill removed');
    } catch (err) { toast.error('Failed to remove skill'); }
  };

  return (
    <Box>
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h5" sx={{ fontWeight: 700, color: '#F1F5F9' }}>Category Management</Typography>
        <Button variant="contained" startIcon={<AddIcon />} onClick={() => openEdit(null)}
          sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Add Category</Button>
      </Box>

      {error && <Alert severity="error" sx={{ mb: 2, borderRadius: 2, bgcolor: 'rgba(248,113,113,0.15)', color: '#F87171' }}>{error}</Alert>}

      {loading ? (
        <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>Loading categories...</Typography>
      ) : categories.length === 0 ? (
        <Typography sx={{ color: '#64748B', textAlign: 'center', py: 8 }}>No categories yet. Create your first category.</Typography>
      ) : (
        <Grid container spacing={2}>
          {categories.map((cat, index) => (
            <Grid item xs={12} sm={6} md={4} key={cat._id || cat.id || index}>
              <Card sx={{ bgcolor: '#1E293B', borderRadius: 3 }}>
                <CardContent sx={{ p: 3 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                      <DragIndicatorIcon sx={{ color: '#64748B', cursor: 'grab' }} />
                      <Avatar src={cat.icon} sx={{ width: 48, height: 48, bgcolor: 'rgba(129,140,248,0.15)', color: '#818CF8' }}>
                        {cat.name?.[0]?.toUpperCase()}
                      </Avatar>
                    </Box>
                    <Box>
                      <IconButton size="small" onClick={() => openEdit(cat)} sx={{ color: '#60A5FA' }}><EditIcon fontSize="small" /></IconButton>
                      <IconButton size="small" onClick={() => { setDeleteTarget(cat); setDeleteDialogOpen(true); }} sx={{ color: '#F87171' }}><DeleteIcon fontSize="small" /></IconButton>
                    </Box>
                  </Box>
                  <Typography variant="subtitle1" sx={{ fontWeight: 600, color: '#F1F5F9', mb: 0.5 }}>{cat.name}</Typography>
                  <Typography variant="body2" sx={{ color: '#64748B', mb: 1.5 }}>{cat.description || 'No description'}</Typography>
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <Chip label={`${cat.skills?.length || 0} skills`} size="small" onClick={() => openSkills(cat)}
                      sx={{ bgcolor: 'rgba(96,165,250,0.15)', color: '#60A5FA', cursor: 'pointer' }} />
                    <Chip label={`Sort: ${cat.sortOrder || index + 1}`} size="small" sx={{ bgcolor: 'rgba(255,255,255,0.06)', color: '#64748B' }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}

      <Dialog open={dialogOpen} onClose={() => setDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>{editingCat ? 'Edit Category' : 'Add Category'}</DialogTitle>
        <DialogContent>
          <TextField fullWidth label="Category Name" value={formData.name} onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            sx={{ mt: 2, mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Description" multiline rows={3} value={formData.description} onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            sx={{ mb: 2, '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
          <TextField fullWidth label="Icon URL (optional)" value={formData.icon} onChange={(e) => setFormData({ ...formData, icon: e.target.value })}
            sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } }, '& .MuiInputLabel-root': { color: '#64748B' } }} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleSave} disabled={!formData.name} variant="contained" sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' } }}>Save</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={skillsDialogOpen} onClose={() => setSkillsDialogOpen(false)} maxWidth="sm" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Skills - {skillsCat?.name}</DialogTitle>
        <DialogContent>
          <Box sx={{ display: 'flex', gap: 1, mb: 2 }}>
            <TextField fullWidth size="small" placeholder="Add a skill..." value={newSkill} onChange={(e) => setNewSkill(e.target.value)}
              onKeyDown={(e) => { if (e.key === 'Enter') { e.preventDefault(); addSkill(); } }}
              sx={{ '& .MuiOutlinedInput-root': { color: '#F1F5F9', '& fieldset': { borderColor: 'rgba(255,255,255,0.12)' } } }} />
            <Button variant="contained" onClick={addSkill} disabled={!newSkill.trim()}
              sx={{ bgcolor: '#818CF8', '&:hover': { bgcolor: '#6366F1' }, flexShrink: 0 }}>Add</Button>
          </Box>
          {skills.length > 0 ? (
            <List>
              {skills.map((skill, i) => (
                <ListItem key={i} sx={{ px: 0, '&:hover': { bgcolor: 'rgba(255,255,255,0.03)', borderRadius: 2 } }}
                  secondaryAction={
                    <IconButton edge="end" size="small" onClick={() => removeSkill(i)} sx={{ color: '#F87171' }}>
                      <DeleteIcon fontSize="small" />
                    </IconButton>
                  }>
                  <ListItemText primary={skill.name || skill} primaryTypographyProps={{ color: '#F1F5F9' }} />
                </ListItem>
              ))}
            </List>
          ) : (
            <Typography variant="body2" sx={{ color: '#64748B', textAlign: 'center', py: 2 }}>No skills added yet</Typography>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSkillsDialogOpen(false)} sx={{ color: '#94A3B8' }}>Close</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)} maxWidth="xs" fullWidth
        PaperProps={{ sx: { bgcolor: '#1E293B', color: '#F1F5F9', borderRadius: 3 } }}>
        <DialogTitle>Delete Category</DialogTitle>
        <DialogContent>
          <Typography variant="body2" sx={{ color: '#94A3B8' }}>Are you sure you want to delete &quot;{deleteTarget?.name}&quot;? This action cannot be undone.</Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)} sx={{ color: '#94A3B8' }}>Cancel</Button>
          <Button onClick={handleDelete} color="error" sx={{ color: '#F87171' }}>Delete</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
