'use client';
import { useState, useMemo } from 'react';
import {
  Table, TableBody, TableCell, TableContainer, TableHead, TableRow,
  TablePagination, TableSortLabel, Paper, Checkbox, Box, Typography, Button,
} from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import LoadingSpinner from '@/components/common/LoadingSpinner';
import EmptyState from '@/components/common/EmptyState';

export default function DataTable({
  columns = [], rows = [], loading = false, error = null, onRetry,
  selectable = false, selected = [], onSelectionChange,
  defaultSortBy, defaultSortOrder = 'asc',
  page = 0, rowsPerPage = 10, total = 0,
  onPageChange, onRowsPerPageChange,
  emptyTitle, emptyDescription, emptyIcon,
  stickyHeader = true, onExport, exportLabel = 'Export',
  bulkActions, sx, onRowClick,
}) {
  const [sortBy, setSortBy] = useState(defaultSortBy || '');
  const [sortOrder, setSortOrder] = useState(defaultSortOrder);

  const handleSort = (column) => {
    if (sortBy === column) { setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc')); }
    else { setSortBy(column); setSortOrder('asc'); }
  };

  const sortedRows = useMemo(() => {
    if (!sortBy) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortBy], bVal = b[sortBy];
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'string') return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });
  }, [rows, sortBy, sortOrder]);

  const handleSelectAll = (checked) => {
    if (!onSelectionChange) return;
    onSelectionChange(checked ? sortedRows.map((r) => r._id || r.id) : []);
  };

  const handleSelect = (id) => {
    if (!onSelectionChange) return;
    const newSelected = selected.includes(id) ? selected.filter((s) => s !== id) : [...selected, id];
    onSelectionChange(newSelected);
  };

  const handleRowClick = (row) => {
    if (onRowClick) onRowClick(row);
  };

  if (loading) return <LoadingSpinner message="Loading data..." fullPage={false} />;

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <Typography color="#F87171">{error}</Typography>
      </Box>
    );
  }

  if (!rows.length) {
    return <EmptyState title={emptyTitle || 'No data found'} description={emptyDescription || 'There are no items to display.'} icon={emptyIcon} onAction={onRetry} actionLabel="Refresh" />;
  }

  return (
    <Paper sx={{ width: '100%', overflow: 'hidden', borderRadius: 3, bgcolor: '#1E293B', ...sx }}>
      {(selectable || onExport || bulkActions) && (
        <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', px: 2, py: 1.5, borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            {selectable && selected.length > 0 && (
              <Typography variant="body2" sx={{ color: '#94A3B8' }}>{selected.length} selected</Typography>
            )}
            {bulkActions && selected.length > 0 && bulkActions}
          </Box>
          {onExport && (
            <Button size="small" startIcon={<FileDownloadIcon />} onClick={onExport}
              sx={{ color: '#94A3B8', '&:hover': { color: '#818CF8' } }}>
              {exportLabel}
            </Button>
          )}
        </Box>
      )}
      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader={stickyHeader}>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox" sx={{ bgcolor: '#0F172A', borderBottom: '1px solid rgba(255,255,255,0.06)' }}>
                  <Checkbox indeterminate={selected.length > 0 && selected.length < rows.length}
                    checked={rows.length > 0 && selected.length === rows.length}
                    onChange={(e) => handleSelectAll(e.target.checked)} sx={{ color: '#64748B' }} />
                </TableCell>
              )}
              {columns.map((col) => (
                <TableCell key={col.key} align={col.align || 'left'}
                  sx={{ fontWeight: 600, fontSize: '0.8125rem', textTransform: 'uppercase', letterSpacing: '0.05em', whiteSpace: 'nowrap', color: '#64748B', bgcolor: '#0F172A', borderBottom: '1px solid rgba(255,255,255,0.06)', ...col.sx }}>
                  {col.sortable ? (
                    <TableSortLabel active={sortBy === col.key} direction={sortBy === col.key ? sortOrder : 'asc'} onClick={() => handleSort(col.key)}
                      sx={{ color: '#64748B !important', '&.Mui-active': { color: '#818CF8 !important' }, '& .MuiTableSortLabel-icon': { color: '#818CF8 !important' } }}>
                      {col.label}
                    </TableSortLabel>
                  ) : col.label}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
                  {sortedRows.map((row) => {
              const rowId = row._id || row.id;
              return (
                <TableRow key={rowId} hover selected={selected.includes(rowId)}
                  onClick={() => handleRowClick(row)}
                  sx={{ cursor: 'pointer', '&:hover': { bgcolor: 'rgba(255,255,255,0.03)' }, '&.Mui-selected': { bgcolor: 'rgba(129,140,248,0.08)' }, '&:last-child td': { border: 0 } }}>
                  {selectable && (
                    <TableCell padding="checkbox" sx={{ borderBottom: '1px solid rgba(255,255,255,0.04)' }}>
                      <Checkbox checked={selected.includes(rowId)} onChange={() => handleSelect(rowId)} sx={{ color: '#64748B' }} />
                    </TableCell>
                  )}
                  {columns.map((col) => (
                    <TableCell key={col.key} align={col.align || 'left'}
                      sx={{ color: '#F1F5F9', borderBottom: '1px solid rgba(255,255,255,0.04)', whiteSpace: col.nowrap ? 'nowrap' : 'normal', ...col.cellSx }}>
                      {col.render ? col.render(row) : row[col.key] ?? '-'}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      {total > 0 && (
        <TablePagination component="div" count={total} page={page} onPageChange={(_, p) => onPageChange?.(p)}
          rowsPerPage={rowsPerPage} onRowsPerPageChange={(e) => onRowsPerPageChange?.(parseInt(e.target.value, 10))}
          rowsPerPageOptions={[10, 25, 50, 100]}
          sx={{ borderTop: '1px solid rgba(255,255,255,0.06)', color: '#94A3B8', '& .MuiTablePagination-selectIcon': { color: '#64748B' }, '& .MuiIconButton-root': { color: '#94A3B8' } }} />
      )}
    </Paper>
  );
}
