import { useState, useCallback } from 'react';
import {
  Box, Typography, Grid, TextField, MenuItem, Pagination, Chip,
  InputAdornment, Button, Checkbox, FormControlLabel, Badge,
  IconButton, Tooltip, Drawer, Stack, Select, Divider, Avatar,
  Card, CardContent, LinearProgress, Collapse, ToggleButtonGroup,
  ToggleButton, Menu, ListItemIcon, ListItemText, Alert,
} from '@mui/material';
import DashboardLayout from '@/components/layout/DashboardLayout';
import ApplicantCard from '@/components/applications/ApplicantCard';
import StatusBadge from '@/components/common/StatusBadge';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import ErrorState from '@/components/common/ErrorState';
import EmptyState from '@/components/common/EmptyState';
import ExportButton from '@/components/applications/ExportButton';
import { useApplications } from '@/hooks/useApplications';
import { APPLICATION_STATUS, APPLICATION_PIPELINE_STAGES } from '@/utils/constants';
import { formatDate, formatRelativeTime } from '@/utils/formatters';
import { getInitials, getAvatarColor } from '@/utils/helpers';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ViewListIcon from '@mui/icons-material/ViewList';
import ViewKanbanIcon from '@mui/icons-material/ViewKanban';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import CalendarTodayIcon from '@mui/icons-material/CalendarToday';
import SortIcon from '@mui/icons-material/Sort';
import MoreVertIcon from '@mui/icons-material/MoreVert';
import ArrowUpwardIcon from '@mui/icons-material/ArrowUpward';
import ArrowDownwardIcon from '@mui/icons-material/ArrowDownward';
import { toast } from 'react-toastify';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  ...Object.entries(APPLICATION_STATUS).map(([key, val]) => ({
    value: val,
    label: val.replace(/_/g, ' ').replace(/\b\w/g, (l) => l.toUpperCase()),
  })),
];

const sortOptions = [
  { value: 'newest', label: 'Newest First' },
  { value: 'oldest', label: 'Oldest First' },
  { value: 'matchScore_desc', label: 'Match Score (High)' },
  { value: 'matchScore_asc', label: 'Match Score (Low)' },
  { value: 'name_asc', label: 'Name (A-Z)' },
  { value: 'name_desc', label: 'Name (Z-A)' },
];

const BULK_ACTIONS = [
  { value: 'shortlisted', label: 'Shortlist', color: 'success' },
  { value: 'interview_scheduled', label: 'Move to Interview', color: 'warning' },
  { value: 'rejected', label: 'Reject', color: 'error' },
  { value: 'hired', label: 'Mark Hired', color: 'info' },
];

export default function ApplicantsPage() {
  const {
    applications,
    loading,
    error,
    pagination,
    updateStatus,
    setPage,
    setFilters,
    refresh,
  } = useApplications();

  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('newest');
  const [viewMode, setViewMode] = useState('list');
  const [selectedIds, setSelectedIds] = useState([]);
  const [filterDrawerOpen, setFilterDrawerOpen] = useState(false);
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [minMatchScore, setMinMatchScore] = useState('');
  const [skillsFilter, setSkillsFilter] = useState('');
  const [bulkAnchorEl, setBulkAnchorEl] = useState(null);
  const [applyingBulk, setApplyingBulk] = useState(false);

  const handleSearch = (e) => {
    const val = e.target.value;
    setSearch(val);
    applyFilters({ search: val });
  };

  const handleStatusFilter = (e) => {
    const val = e.target.value;
    setStatusFilter(val);
    applyFilters({ status: val });
  };

  const handleSortChange = (e) => {
    const val = e.target.value;
    setSortBy(val);
    applyFilters({ sort: val });
  };

  const applyFilters = useCallback((overrides = {}) => {
    const filters = {
      search,
      status: statusFilter,
      sort: sortBy,
      dateFrom,
      dateTo,
      minMatchScore: minMatchScore || undefined,
      skills: skillsFilter || undefined,
      ...overrides,
    };
    Object.keys(filters).forEach((k) => { if (!filters[k]) delete filters[k]; });
    setFilters(filters);
  }, [search, statusFilter, sortBy, dateFrom, dateTo, minMatchScore, skillsFilter, setFilters]);

  const clearFilters = () => {
    setSearch('');
    setStatusFilter('');
    setSortBy('newest');
    setDateFrom('');
    setDateTo('');
    setMinMatchScore('');
    setSkillsFilter('');
    setFilters({});
  };

  const handleSelectAll = (e) => {
    if (e.target.checked) {
      setSelectedIds(applications.map((a) => a._id || a.id));
    } else {
      setSelectedIds([]);
    }
  };

  const handleSelectOne = (id) => {
    setSelectedIds((prev) =>
      prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
    );
  };

  const handleBulkAction = async (newStatus) => {
    if (selectedIds.length === 0) {
      toast.warning('No applicants selected');
      return;
    }
    setApplyingBulk(true);
    setBulkAnchorEl(null);
    try {
      await Promise.all(selectedIds.map((id) => updateStatus(id, newStatus)));
      toast.success(`Updated ${selectedIds.length} applicants to ${newStatus.replace(/_/g, ' ')}`);
      setSelectedIds([]);
      refresh();
    } catch {
      toast.error('Failed to update some applicants');
    } finally {
      setApplyingBulk(false);
    }
  };

  const activeFilters = [search, statusFilter, dateFrom, dateTo, minMatchScore, skillsFilter].filter(Boolean).length;
  const pipelineStages = APPLICATION_PIPELINE_STAGES;

  const getStageApplications = (stageKey) =>
    applications.filter((a) => (a.status || '').toLowerCase() === stageKey);

  const exportColumns = [
    { key: 'name', label: 'Name' },
    { key: 'email', label: 'Email' },
    { key: 'phone', label: 'Phone' },
    { key: 'currentPosition', label: 'Current Position' },
    { key: 'status', label: 'Status' },
    { key: 'matchScore', label: 'Match Score' },
    { key: 'skills', label: 'Skills' },
    { key: 'experience', label: 'Experience' },
    { key: 'location', label: 'Location' },
    { key: 'appliedDate', label: 'Applied Date' },
  ];

  const exportData = applications.map((a) => ({
    name: a.name || a.fullName || 'Unknown',
    email: a.email || '',
    phone: a.phone || '',
    currentPosition: a.currentPosition || a.headline || '',
    status: a.status || '',
    matchScore: a.matchScore || a.aiScore || 0,
    skills: (a.skills || []).join(', '),
    experience: a.experience || '',
    location: a.location || '',
    appliedDate: a.createdAt || a.appliedAt || '',
  }));

  if (error && !applications.length) {
    return (
      <DashboardLayout>
        <ErrorState message={error} onRetry={refresh} />
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <Box sx={{ mb: 3, display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: 2 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 700, mb: 0.5 }}>Applicants</Typography>
          <Typography variant="body2" color="text.secondary">
            {pagination.total} applicant{pagination.total !== 1 ? 's' : ''} total
            {activeFilters > 0 && ` • ${activeFilters} filter${activeFilters !== 1 ? 's' : ''} active`}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1, alignItems: 'center' }}>
          <ToggleButtonGroup
            value={viewMode}
            exclusive
            onChange={(_, val) => val && setViewMode(val)}
            size="small"
          >
            <ToggleButton value="list" sx={{ px: 1.5 }}>
              <Tooltip title="List View"><ViewListIcon fontSize="small" /></Tooltip>
            </ToggleButton>
            <ToggleButton value="pipeline" sx={{ px: 1.5 }}>
              <Tooltip title="Pipeline View"><ViewKanbanIcon fontSize="small" /></Tooltip>
            </ToggleButton>
          </ToggleButtonGroup>
          <ExportButton
            data={exportData}
            filename="applicants_export"
            columns={exportColumns}
            disabled={applications.length === 0}
            size="small"
          />
        </Box>
      </Box>

      <Box sx={{ display: 'flex', gap: 2, mb: 3, flexWrap: 'wrap', alignItems: 'center' }}>
        <TextField
          size="small"
          placeholder="Search by name, skills..."
          value={search}
          onChange={handleSearch}
          sx={{ minWidth: 260 }}
          InputProps={{
            startAdornment: <InputAdornment position="start"><SearchIcon sx={{ fontSize: 20, color: 'text.secondary' }} /></InputAdornment>,
          }}
        />
        <TextField
          select
          size="small"
          label="Status"
          value={statusFilter}
          onChange={handleStatusFilter}
          sx={{ minWidth: 150 }}
        >
          {statusOptions.map((opt) => (
            <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
          ))}
        </TextField>
        <TextField
          select
          size="small"
          label="Sort by"
          value={sortBy}
          onChange={handleSortChange}
          sx={{ minWidth: 170 }}
        >
          {sortOptions.map((opt) => (
            <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
          ))}
        </TextField>
        <Badge badgeContent={activeFilters} color="primary" invisible={activeFilters === 0}>
          <Button
            variant="outlined"
            size="small"
            startIcon={<FilterListIcon />}
            onClick={() => setFilterDrawerOpen(true)}
          >
            Filters
          </Button>
        </Badge>
        {activeFilters > 0 && (
          <Chip label={`Clear all (${activeFilters})`} onDelete={clearFilters} size="small" />
        )}
      </Box>

      {selectedIds.length > 0 && viewMode === 'list' && (
        <Box
          sx={{
            display: 'flex', alignItems: 'center', gap: 2, mb: 2, p: 1.5,
            bgcolor: 'primary.main', color: '#fff', borderRadius: 2,
          }}
        >
          <Checkbox
            checked={selectedIds.length === applications.length}
            indeterminate={selectedIds.length > 0 && selectedIds.length < applications.length}
            onChange={handleSelectAll}
            sx={{ color: '#fff', '&.Mui-checked': { color: '#fff' } }}
          />
          <Typography variant="body2" sx={{ fontWeight: 600 }}>
            {selectedIds.length} selected
          </Typography>
          <Box sx={{ flex: 1 }} />
          <Button
            variant="contained"
            size="small"
            color="inherit"
            sx={{ color: 'primary.main', bgcolor: '#fff', '&:hover': { bgcolor: 'grey.100' } }}
            onClick={(e) => setBulkAnchorEl(e.currentTarget)}
            disabled={applyingBulk}
          >
            Update Status
          </Button>
          <Button
            variant="text"
            size="small"
            sx={{ color: '#fff' }}
            onClick={() => setSelectedIds([])}
          >
            Clear
          </Button>
        </Box>
      )}

      <Menu anchorEl={bulkAnchorEl} open={Boolean(bulkAnchorEl)} onClose={() => setBulkAnchorEl(null)}>
        {BULK_ACTIONS.map((action) => (
          <MenuItem key={action.value} onClick={() => handleBulkAction(action.value)} dense>
            <ListItemIcon>
              {action.value === 'rejected' ? <CancelIcon fontSize="small" color="error" />
                : action.value === 'shortlisted' ? <CheckCircleIcon fontSize="small" color="success" />
                : <CalendarTodayIcon fontSize="small" color="warning" />}
            </ListItemIcon>
            <ListItemText>{action.label}</ListItemText>
          </MenuItem>
        ))}
      </Menu>

      {loading && viewMode === 'list' ? (
        <LoadingSpinner message="Loading applicants..." fullPage={false} />
      ) : viewMode === 'pipeline' ? (
        <Box
          sx={{
            display: 'flex', gap: 2, overflowX: 'auto', pb: 2,
            minHeight: 500,
          }}
        >
          {pipelineStages.map((stage) => {
            const stageApps = getStageApplications(stage.key);
            return (
              <Box
                key={stage.key}
                sx={{
                  minWidth: 260, maxWidth: 300, flex: 1,
                  bgcolor: 'action.hover', borderRadius: 3, p: 2,
                  display: 'flex', flexDirection: 'column',
                }}
              >
                <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Box sx={{ width: 10, height: 10, borderRadius: '50%', bgcolor: stage.color }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>{stage.label}</Typography>
                  </Box>
                  <Chip label={stageApps.length} size="small" sx={{ fontWeight: 600, minWidth: 28 }} />
                </Box>
                <Box sx={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: 1.5 }}>
                  {stageApps.length === 0 ? (
                    <Box sx={{ py: 3, textAlign: 'center' }}>
                      <Typography variant="caption" color="text.disabled">No applicants</Typography>
                    </Box>
                  ) : (
                    stageApps.map((app) => (
                      <Card key={app._id || app.id} sx={{ borderRadius: 2, cursor: 'pointer', '&:hover': { boxShadow: 3 } }}>
                        <CardContent sx={{ p: 1.5, '&:last-child': { pb: 1.5 } }}>
                          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 1 }}>
                            <Avatar sx={{ width: 28, height: 28, fontSize: '0.7rem', bgcolor: getAvatarColor(app.name || app.fullName || 'U') }}>
                              {getInitials(app.name || app.fullName || 'Unknown')}
                            </Avatar>
                            <Box sx={{ minWidth: 0, flex: 1 }}>
                              <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', truncate: true }}>
                                {app.name || app.fullName || 'Unknown'}
                              </Typography>
                              <Typography variant="caption" color="text.secondary">
                                {app.currentPosition || app.headline || ''}
                              </Typography>
                            </Box>
                          </Box>
                          <Box sx={{ display: 'flex', gap: 0.5, flexWrap: 'wrap', mb: 1 }}>
                            {(app.skills || []).slice(0, 2).map((s) => (
                              <Chip key={s} label={s} size="small" variant="outlined" sx={{ fontSize: '0.65rem', height: 20 }} />
                            ))}
                          </Box>
                          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                            <Typography variant="caption" color="text.secondary">
                              {formatRelativeTime(app.createdAt || app.appliedAt)}
                            </Typography>
                            {(app.matchScore || app.aiScore) > 0 && (
                              <Typography variant="caption" sx={{ fontWeight: 700, color: (app.matchScore || app.aiScore) >= 70 ? 'success.main' : 'warning.main' }}>
                                {app.matchScore || app.aiScore}%
                              </Typography>
                            )}
                          </Box>
                        </CardContent>
                      </Card>
                    ))
                  )}
                </Box>
              </Box>
            );
          })}
        </Box>
      ) : applications.length === 0 ? (
        <EmptyState
          title="No applicants found"
          description={search || statusFilter || activeFilters > 0 ? 'Try adjusting your filters.' : 'No applications have been submitted yet.'}
        />
      ) : (
        <>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 2 }}>
            <Checkbox
              checked={selectedIds.length === applications.length && applications.length > 0}
              indeterminate={selectedIds.length > 0 && selectedIds.length < applications.length}
              onChange={handleSelectAll}
              size="small"
            />
            <Typography variant="caption" color="text.secondary">
              Select All
            </Typography>
          </Box>
          <Grid container spacing={3}>
            {applications.map((app) => {
              const appId = app._id || app.id;
              return (
                <Grid item xs={12} sm={6} lg={4} key={appId}>
                  <Box sx={{ position: 'relative' }}>
                    <Box
                      sx={{
                        position: 'absolute', top: 8, left: 8, zIndex: 10,
                      }}
                      onClick={(e) => e.stopPropagation()}
                    >
                      <Checkbox
                        checked={selectedIds.includes(appId)}
                        onChange={() => handleSelectOne(appId)}
                        size="small"
                        sx={{ bgcolor: 'background.paper', borderRadius: 1 }}
                      />
                    </Box>
                    <ApplicantCard applicant={app} />
                  </Box>
                </Grid>
              );
            })}
          </Grid>

          {pagination.totalPages > 1 && (
            <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
              <Pagination
                count={pagination.totalPages}
                page={pagination.page}
                onChange={(_, p) => setPage(p)}
                color="primary"
                shape="rounded"
              />
            </Box>
          )}
        </>
      )}

      <Drawer anchor="right" open={filterDrawerOpen} onClose={() => setFilterDrawerOpen(false)}>
        <Box sx={{ width: 320, p: 3 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 3 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>Advanced Filters</Typography>
            <Button size="small" onClick={clearFilters} color="inherit">Clear</Button>
          </Box>

          <Stack spacing={2.5}>
            <Box>
              <Typography variant="caption" sx={{ fontWeight: 600, mb: 1, display: 'block', color: 'text.secondary' }}>
                Date Range
              </Typography>
              <Grid container spacing={1}>
                <Grid item xs={6}>
                  <TextField
                    size="small"
                    type="date"
                    label="From"
                    value={dateFrom}
                    onChange={(e) => setDateFrom(e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    fullWidth
                  />
                </Grid>
                <Grid item xs={6}>
                  <TextField
                    size="small"
                    type="date"
                    label="To"
                    value={dateTo}
                    onChange={(e) => setDateTo(e.target.value)}
                    InputLabelProps={{ shrink: true }}
                    fullWidth
                  />
                </Grid>
              </Grid>
            </Box>

            <Box>
              <Typography variant="caption" sx={{ fontWeight: 600, mb: 1, display: 'block', color: 'text.secondary' }}>
                Minimum Match Score
              </Typography>
              <TextField
                size="small"
                type="number"
                placeholder="e.g. 70"
                value={minMatchScore}
                onChange={(e) => setMinMatchScore(e.target.value)}
                InputProps={{ inputProps: { min: 0, max: 100 } }}
                fullWidth
              />
            </Box>

            <Box>
              <Typography variant="caption" sx={{ fontWeight: 600, mb: 1, display: 'block', color: 'text.secondary' }}>
                Skills
              </Typography>
              <TextField
                size="small"
                placeholder="e.g. React, Python"
                value={skillsFilter}
                onChange={(e) => setSkillsFilter(e.target.value)}
                fullWidth
              />
            </Box>

            <Divider />

            <Button
              variant="contained"
              fullWidth
              onClick={() => { applyFilters(); setFilterDrawerOpen(false); }}
            >
              Apply Filters
            </Button>
          </Stack>
        </Box>
      </Drawer>
    </DashboardLayout>
  );
}
