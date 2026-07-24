'use client';
import { useState, useMemo } from 'react';
import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  TablePagination,
  TableSortLabel,
  Paper,
  Checkbox,
  Box,
  Typography,
} from '@mui/material';
import LoadingSpinner from './LoadingSpinner';
import EmptyState from './EmptyState';

export default function DataTable({
  columns = [],
  rows = [],
  loading = false,
  error = null,
  onRetry,
  selectable = false,
  selected = [],
  onSelectionChange,
  defaultSortBy,
  defaultSortOrder = 'asc',
  page = 0,
  rowsPerPage = 10,
  total = 0,
  onPageChange,
  onRowsPerPageChange,
  emptyTitle,
  emptyDescription,
  emptyIcon,
  stickyHeader = true,
  sx,
}) {
  const [sortBy, setSortBy] = useState(defaultSortBy || '');
  const [sortOrder, setSortOrder] = useState(defaultSortOrder);

  const handleSort = (column) => {
    if (sortBy === column) {
      setSortOrder((prev) => (prev === 'asc' ? 'desc' : 'asc'));
    } else {
      setSortBy(column);
      setSortOrder('asc');
    }
  };

  const sortedRows = useMemo(() => {
    if (!sortBy) return rows;
    return [...rows].sort((a, b) => {
      const aVal = a[sortBy];
      const bVal = b[sortBy];
      if (aVal == null) return 1;
      if (bVal == null) return -1;
      if (typeof aVal === 'string') {
        return sortOrder === 'asc' ? aVal.localeCompare(bVal) : bVal.localeCompare(aVal);
      }
      return sortOrder === 'asc' ? aVal - bVal : bVal - aVal;
    });
  }, [rows, sortBy, sortOrder]);

  const handleSelectAll = (checked) => {
    if (!onSelectionChange) return;
    if (checked) {
      onSelectionChange(sortedRows.map((r) => r._id || r.id));
    } else {
      onSelectionChange([]);
    }
  };

  const handleSelect = (id) => {
    if (!onSelectionChange) return;
    const newSelected = selected.includes(id)
      ? selected.filter((s) => s !== id)
      : [...selected, id];
    onSelectionChange(newSelected);
  };

  const handleChangePage = (_, newPage) => {
    if (onPageChange) onPageChange(newPage);
  };

  const handleChangeRowsPerPage = (event) => {
    if (onRowsPerPageChange) onRowsPerPageChange(parseInt(event.target.value, 10));
  };

  if (loading) return <LoadingSpinner message="Loading data..." fullPage={false} />;

  if (error) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}>
        <Typography color="error">{error}</Typography>
      </Box>
    );
  }

  if (!rows.length) {
    return (
      <EmptyState
        title={emptyTitle || 'No data found'}
        description={emptyDescription || 'There are no items to display.'}
        icon={emptyIcon}
        onAction={onRetry}
        actionLabel="Refresh"
      />
    );
  }

  return (
    <Paper
      sx={{
        width: '100%',
        overflow: 'hidden',
        borderRadius: 3,
        boxShadow: '0 1px 3px rgba(0,0,0,0.06)',
        ...sx,
      }}
    >
      <TableContainer sx={{ maxHeight: 600 }}>
        <Table stickyHeader={stickyHeader}>
          <TableHead>
            <TableRow>
              {selectable && (
                <TableCell padding="checkbox" sx={{ bgcolor: 'action.hover' }}>
                  <Checkbox
                    indeterminate={selected.length > 0 && selected.length < rows.length}
                    checked={rows.length > 0 && selected.length === rows.length}
                    onChange={(e) => handleSelectAll(e.target.checked)}
                    sx={{ color: 'text.disabled' }}
                  />
                </TableCell>
              )}
              {columns.map((col) => (
                <TableCell
                  key={col.key}
                  align={col.align || 'left'}
                  sx={{
                    fontWeight: 600,
                    fontSize: '0.8125rem',
                    textTransform: 'uppercase',
                    letterSpacing: '0.05em',
                    whiteSpace: 'nowrap',
                    ...col.sx,
                  }}
                >
                  {col.sortable ? (
                    <TableSortLabel
                      active={sortBy === col.key}
                      direction={sortBy === col.key ? sortOrder : 'asc'}
                      onClick={() => handleSort(col.key)}
                    >
                      {col.label}
                    </TableSortLabel>
                  ) : (
                    col.label
                  )}
                </TableCell>
              ))}
            </TableRow>
          </TableHead>
          <TableBody>
            {sortedRows.map((row) => {
              const rowId = row._id || row.id;
              return (
                <TableRow
                  key={rowId}
                  hover
                  selected={selected.includes(rowId)}
                  sx={{ cursor: 'pointer', '&:last-child td': { border: 0 } }}
                >
                  {selectable && (
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selected.includes(rowId)}
                        onChange={() => handleSelect(rowId)}
                      />
                    </TableCell>
                  )}
                  {columns.map((col) => (
                    <TableCell
                      key={col.key}
                      align={col.align || 'left'}
                      sx={{ whiteSpace: col.nowrap ? 'nowrap' : 'normal', ...col.cellSx }}
                    >
                      {col.render ? col.render(row) : row[col.key]}
                    </TableCell>
                  ))}
                </TableRow>
              );
            })}
          </TableBody>
        </Table>
      </TableContainer>
      {total > 0 && (
        <TablePagination
          component="div"
          count={total}
          page={page}
          onPageChange={handleChangePage}
          rowsPerPage={rowsPerPage}
          onRowsPerPageChange={handleChangeRowsPerPage}
          rowsPerPageOptions={[10, 25, 50, 100]}
          sx={{ borderTop: '1px solid', borderColor: 'divider' }}
        />
      )}
    </Paper>
  );
}
