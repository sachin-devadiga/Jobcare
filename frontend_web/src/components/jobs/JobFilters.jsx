'use client';
import { useState } from 'react';
import {
  Box, TextField, MenuItem, Chip, Select, InputLabel, FormControl,
  OutlinedInput, IconButton, Collapse,
} from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import FilterListIcon from '@mui/icons-material/FilterList';
import ClearIcon from '@mui/icons-material/Clear';
import { JOB_STATUS, JOB_TYPES, EXPERIENCE_LEVELS } from '@/utils/constants';

const statusOptions = [
  { value: '', label: 'All Statuses' },
  ...Object.entries(JOB_STATUS).map(([key, val]) => ({ value: val, label: val.charAt(0).toUpperCase() + val.slice(1) })),
];

const typeOptions = [
  { value: '', label: 'All Types' },
  ...Object.entries(JOB_TYPES).map(([key, val]) => ({ value: val, label: val.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()) })),
];

const levelOptions = [
  { value: '', label: 'All Levels' },
  ...Object.entries(EXPERIENCE_LEVELS).map(([key, val]) => ({ value: val, label: val.charAt(0).toUpperCase() + val.slice(1) })),
];

export default function JobFilters({ filters, onFilterChange, onSearch }) {
  const [showFilters, setShowFilters] = useState(false);

  const handleChange = (field, value) => {
    onFilterChange({ ...filters, [field]: value });
  };

  const clearFilters = () => {
    onFilterChange({});
    onSearch('');
  };

  const hasActiveFilters = filters?.status || filters?.type || filters?.experienceLevel || filters?.search;

  return (
    <Box>
      <Box sx={{ display: 'flex', alignItems: 'center', gap: 2, mb: 2, flexWrap: 'wrap' }}>
        <TextField
          size="small"
          placeholder="Search jobs..."
          value={filters?.search || ''}
          onChange={(e) => onSearch?.(e.target.value)}
          sx={{ minWidth: 280 }}
          InputProps={{
            startAdornment: <SearchIcon sx={{ mr: 1, color: 'text.secondary', fontSize: 20 }} />,
          }}
        />
        <FormControl size="small" sx={{ minWidth: 140 }}>
          <Select
            value={filters?.status || ''}
            onChange={(e) => handleChange('status', e.target.value)}
            displayEmpty
          >
            {statusOptions.map((opt) => (
              <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
            ))}
          </Select>
        </FormControl>
        <IconButton
          onClick={() => setShowFilters(!showFilters)}
          color={showFilters || hasActiveFilters ? 'primary' : 'default'}
          sx={{ border: '1px solid', borderColor: 'divider', borderRadius: 2 }}
        >
          <FilterListIcon />
        </IconButton>
        {hasActiveFilters && (
          <Chip
            label="Clear filters"
            onDelete={clearFilters}
            size="small"
            sx={{ borderRadius: 2 }}
          />
        )}
      </Box>

      <Collapse in={showFilters}>
        <Box sx={{ display: 'flex', gap: 2, mb: 2, flexWrap: 'wrap' }}>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <Select
              value={filters?.type || ''}
              onChange={(e) => handleChange('type', e.target.value)}
              displayEmpty
            >
              {typeOptions.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
          <FormControl size="small" sx={{ minWidth: 160 }}>
            <Select
              value={filters?.experienceLevel || ''}
              onChange={(e) => handleChange('experienceLevel', e.target.value)}
              displayEmpty
            >
              {levelOptions.map((opt) => (
                <MenuItem key={opt.value} value={opt.value}>{opt.label}</MenuItem>
              ))}
            </Select>
          </FormControl>
        </Box>
      </Collapse>
    </Box>
  );
}
