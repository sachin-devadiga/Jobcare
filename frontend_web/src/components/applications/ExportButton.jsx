'use client';
import { useState, useCallback } from 'react';
import {
  Button, Menu, MenuItem, Dialog, DialogTitle, DialogContent, DialogActions,
  FormControlLabel, Checkbox, Typography, Box, LinearProgress, IconButton,
  List, ListItem, ListItemText, Chip, Stack
} from '@mui/material';
import FileDownloadIcon from '@mui/icons-material/FileDownload';
import CloseIcon from '@mui/icons-material/Close';
import PictureAsPdfIcon from '@mui/icons-material/PictureAsPdf';
import TableChartIcon from '@mui/icons-material/TableChart';
import GridOnIcon from '@mui/icons-material/GridOn';
import { toast } from 'react-toastify';

const FORMAT_OPTIONS = [
  { value: 'xlsx', label: 'Excel (.xlsx)', icon: <GridOnIcon fontSize="small" />, mime: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' },
  { value: 'csv', label: 'CSV (.csv)', icon: <TableChartIcon fontSize="small" />, mime: 'text/csv' },
  { value: 'pdf', label: 'PDF (.pdf)', icon: <PictureAsPdfIcon fontSize="small" />, mime: 'application/pdf' },
];

const DEFAULT_COLUMNS = [
  { key: 'name', label: 'Name' },
  { key: 'email', label: 'Email' },
  { key: 'phone', label: 'Phone' },
  { key: 'position', label: 'Position' },
  { key: 'status', label: 'Status' },
  { key: 'matchScore', label: 'Match Score' },
  { key: 'skills', label: 'Skills' },
  { key: 'experience', label: 'Experience' },
  { key: 'location', label: 'Location' },
  { key: 'appliedDate', label: 'Applied Date' },
];

export default function ExportButton({
  data = [],
  filename = 'export',
  columns = DEFAULT_COLUMNS,
  onBeforeExport,
  disabled = false,
  size = 'medium',
  variant = 'outlined',
}) {
  const [anchorEl, setAnchorEl] = useState(null);
  const [columnDialogOpen, setColumnDialogOpen] = useState(false);
  const [selectedFormat, setSelectedFormat] = useState(null);
  const [selectedColumns, setSelectedColumns] = useState(columns.map((c) => c.key));
  const [exporting, setExporting] = useState(false);
  const [progress, setProgress] = useState(0);

  const handleFormatSelect = (format) => {
    setAnchorEl(null);
    setSelectedFormat(format);
    setColumnDialogOpen(true);
  };

  const toggleColumn = (key) => {
    setSelectedColumns((prev) =>
      prev.includes(key) ? prev.filter((k) => k !== key) : [...prev, key]
    );
  };

  const selectAllColumns = () => {
    setSelectedColumns(columns.map((c) => c.key));
  };

  const handleExport = useCallback(async () => {
    if (selectedColumns.length === 0) {
      toast.warning('Please select at least one column');
      return;
    }
    setExporting(true);
    setProgress(0);

    try {
      if (onBeforeExport) await onBeforeExport();

      const filteredData = data.map((row) => {
        const obj = {};
        selectedColumns.forEach((key) => {
          const col = columns.find((c) => c.key === key);
          obj[col?.label || key] = row[key] != null ? row[key] : '';
        });
        return obj;
      });

      const totalRows = filteredData.length;

      switch (selectedFormat) {
        case 'xlsx':
          await exportXLSX(filteredData, totalRows);
          break;
        case 'csv':
          await exportCSV(filteredData, totalRows);
          break;
        case 'pdf':
          await exportPDF(filteredData, totalRows);
          break;
        default:
          toast.error('Unsupported export format');
      }

      setColumnDialogOpen(false);
      toast.success(`Exported ${totalRows} records as ${selectedFormat.toUpperCase()}`);
    } catch (err) {
      toast.error(err.message || 'Export failed');
    } finally {
      setExporting(false);
      setProgress(0);
    }
  }, [data, selectedColumns, selectedFormat, columns, onBeforeExport]);

  const updateProgress = (current, total) => {
    const pct = Math.min(Math.round((current / total) * 100), 99);
    setProgress(pct);
  };

  const exportXLSX = async (jsonData, total) => {
    const XLSX = await import('xlsx');
    const ws = XLSX.utils.json_to_sheet(jsonData);
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Sheet1');
    const wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
    updateProgress(total, total);
    const { saveAs } = await import('file-saver');
    const blob = new Blob([wbout], { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' });
    saveAs(blob, `${filename}.xlsx`);
    setProgress(100);
  };

  const exportCSV = async (jsonData, total) => {
    const headers = Object.keys(jsonData[0] || {});
    const csvRows = [headers.join(',')];
    for (let i = 0; i < jsonData.length; i++) {
      const row = jsonData[i];
      const values = headers.map((h) => {
        const val = row[h]?.toString() || '';
        return val.includes(',') || val.includes('"') || val.includes('\n')
          ? `"${val.replace(/"/g, '""')}"`
          : val;
      });
      csvRows.push(values.join(','));
      if (i % 50 === 0) updateProgress(i, total);
    }
    updateProgress(total, total);
    const { saveAs } = await import('file-saver');
    const blob = new Blob([csvRows.join('\n')], { type: 'text/csv;charset=utf-8' });
    saveAs(blob, `${filename}.csv`);
    setProgress(100);
  };

  const exportPDF = async (jsonData, total) => {
    const { default: jsPDF } = await import('jspdf');
    const { default: autoTable } = await import('jspdf-autotable');
    const doc = new jsPDF({ orientation: jsonData.length > 15 ? 'landscape' : 'portrait' });
    const headers = Object.keys(jsonData[0] || {});
    const rows = jsonData.map((row) => headers.map((h) => row[h]?.toString() || ''));
    autoTable(doc, {
      head: [headers],
      body: rows,
      styles: { fontSize: 8, cellPadding: 2 },
      headStyles: { fillColor: [99, 102, 241], fontSize: 8, fontStyle: 'bold' },
      didDrawPage: () => updateProgress(Math.min(doc.getNumberOfPages() * 20, total), total),
    });
    updateProgress(total, total);
    const { saveAs } = await import('file-saver');
    const blob = doc.output('blob');
    saveAs(blob, `${filename}.pdf`);
    setProgress(100);
  };

  return (
    <>
      <Button
        variant={variant}
        size={size}
        startIcon={<FileDownloadIcon />}
        onClick={(e) => setAnchorEl(e.currentTarget)}
        disabled={disabled || exporting || data.length === 0}
      >
        Export
      </Button>

      <Menu anchorEl={anchorEl} open={Boolean(anchorEl)} onClose={() => setAnchorEl(null)}>
        {FORMAT_OPTIONS.map((fmt) => (
          <MenuItem key={fmt.value} onClick={() => handleFormatSelect(fmt.value)} dense>
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5 }}>
              {fmt.icon}
              <Typography variant="body2">{fmt.label}</Typography>
            </Box>
          </MenuItem>
        ))}
      </Menu>

      <Dialog open={columnDialogOpen} onClose={() => !exporting && setColumnDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>Select Columns to Export</Typography>
          {!exporting && (
            <IconButton size="small" onClick={() => setColumnDialogOpen(false)}>
              <CloseIcon fontSize="small" />
            </IconButton>
          )}
        </DialogTitle>
        <DialogContent dividers>
          {exporting ? (
            <Box sx={{ py: 4, textAlign: 'center' }}>
              <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                Exporting {data.length} records as {selectedFormat?.toUpperCase()}...
              </Typography>
              <LinearProgress variant="determinate" value={progress} sx={{ height: 8, borderRadius: 4 }} />
              <Typography variant="caption" color="text.secondary" sx={{ mt: 1, display: 'block' }}>
                {progress}%
              </Typography>
            </Box>
          ) : (
            <>
              <Box sx={{ mb: 2, display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Typography variant="body2" color="text.secondary">
                  {selectedColumns.length} of {columns.length} selected
                </Typography>
                <Chip label="Select All" size="small" onClick={selectAllColumns} clickable variant="outlined" />
              </Box>
              <List dense disablePadding>
                {columns.map((col) => (
                  <ListItem key={col.key} disableGutters sx={{ py: 0.25 }}>
                    <FormControlLabel
                      control={
                        <Checkbox
                          checked={selectedColumns.includes(col.key)}
                          onChange={() => toggleColumn(col.key)}
                          size="small"
                        />
                      }
                      label={<Typography variant="body2">{col.label}</Typography>}
                      sx={{ width: '100%' }}
                    />
                  </ListItem>
                ))}
              </List>
            </>
          )}
        </DialogContent>
        {!exporting && (
          <DialogActions sx={{ px: 3, py: 2 }}>
            <Button onClick={() => setColumnDialogOpen(false)} color="inherit">Cancel</Button>
            <Button onClick={handleExport} variant="contained" disabled={selectedColumns.length === 0}>
              Export as {selectedFormat?.toUpperCase()}
            </Button>
          </DialogActions>
        )}
      </Dialog>
    </>
  );
}
