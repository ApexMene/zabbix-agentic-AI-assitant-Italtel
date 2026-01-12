import {
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  IconButton,
  Box,
  Typography,
  Tooltip,
  TextField,
  InputAdornment,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import { 
  CheckCircle, 
  Search, 
  Warning as WarningIcon,
  Error as ErrorIcon,
  Info as InfoIcon,
} from '@mui/icons-material';
import { useEffect, useState } from 'react';
import { useAlarmStore } from '@/stores/alarmStore';
import { useInstanceStore } from '@/stores/instanceStore';
import { api } from '@/services/api';
import { severityColors } from '@/theme/darkTheme';
import { Alarm } from '@/types';

export default function AlarmTable() {
  const { alarms, setAlarms, updateLastPollTime } = useAlarmStore();
  const { selectedInstanceId, setSelectedInstance, instances } = useInstanceStore();
  const [searchText, setSearchText] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string[]>([]);

  const loadAlarms = async () => {
    try {
      const filterParams = {
        instance_id: selectedInstanceId || undefined,
        severity: severityFilter.length > 0 ? severityFilter : undefined,
        host: searchText || undefined,
      };
      
      const data = await api.getAlarms(filterParams);
      setAlarms(data);
      updateLastPollTime();
    } catch (error) {
      console.error('Failed to load alarms:', error);
    }
  };

  useEffect(() => {
    loadAlarms();
    const interval = setInterval(loadAlarms, 30000);
    return () => clearInterval(interval);
  }, [selectedInstanceId, severityFilter, searchText]);

  const getSeverityColor = (severity: string) => {
    return severityColors[severity as keyof typeof severityColors] || severityColors.not_classified;
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'disaster':
      case 'high':
        return <ErrorIcon fontSize="small" />;
      case 'average':
      case 'warning':
        return <WarningIcon fontSize="small" />;
      default:
        return <InfoIcon fontSize="small" />;
    }
  };

  const handleAcknowledge = async (alarm: Alarm) => {
    try {
      await api.acknowledgeAlarm(alarm.id, alarm.instance_id, 'Acknowledged from NOC');
      await loadAlarms();
    } catch (error) {
      console.error('Failed to acknowledge alarm:', error);
      alert('Failed to acknowledge alarm');
    }
  };

  const criticalCount = Array.isArray(alarms) ? alarms.filter(a => ['disaster', 'high'].includes(a.severity)).length : 0;
  const unacknowledgedCount = Array.isArray(alarms) ? alarms.filter(a => !a.acknowledged).length : 0;

  return (
    <Box>
      {/* Header with stats */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
        <Box>
          <Typography variant="h5" sx={{ fontWeight: 600 }}>
            Active Alarms
            {selectedInstanceId && (
              <Chip 
                label={`Filtered by: ${instances.find(i => i.id === selectedInstanceId)?.name || selectedInstanceId}`}
                onDelete={() => setSelectedInstance(null)}
                size="small"
                color="primary"
                sx={{ ml: 2, fontWeight: 'bold' }}
              />
            )}
          </Typography>
          <Box sx={{ display: 'flex', gap: 2, mt: 1 }}>
            <Chip 
              label={`Total: ${alarms.length}`} 
              size="small" 
              sx={{ fontWeight: 'bold' }}
            />
            <Chip 
              label={`Critical: ${criticalCount}`} 
              size="small" 
              color="error"
              sx={{ fontWeight: 'bold' }}
            />
            <Chip 
              label={`Unacknowledged: ${unacknowledgedCount}`} 
              size="small" 
              color="warning"
              sx={{ fontWeight: 'bold' }}
            />
          </Box>
        </Box>
        
        {/* Filters */}
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <TextField
            size="small"
            placeholder="Search host..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <Search fontSize="small" />
                </InputAdornment>
              ),
            }}
            sx={{ width: 200 }}
          />
          
          <FormControl size="small" sx={{ minWidth: 150 }}>
            <InputLabel>Severity</InputLabel>
            <Select
              multiple
              value={severityFilter}
              onChange={(e) => setSeverityFilter(e.target.value as string[])}
              label="Severity"
              renderValue={(selected) => `${selected.length} selected`}
            >
              <MenuItem value="disaster">Disaster</MenuItem>
              <MenuItem value="high">High</MenuItem>
              <MenuItem value="average">Average</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="information">Information</MenuItem>
            </Select>
          </FormControl>
        </Box>
      </Box>
      
      {/* Alarm Table */}
      <TableContainer component={Paper} sx={{ maxHeight: 'calc(100vh - 350px)' }}>
        <Table stickyHeader size="small">
          <TableHead>
            <TableRow>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a' }}>SEVERITY</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a' }}>INSTANCE</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a' }}>HOST</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a' }}>PROBLEM DESCRIPTION</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a' }}>DURATION</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a', textAlign: 'center' }}>ACK</TableCell>
              <TableCell sx={{ fontWeight: 'bold', bgcolor: '#2a2a2a', textAlign: 'center' }}>ACTIONS</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {!Array.isArray(alarms) || alarms.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} align="center" sx={{ py: 4 }}>
                  <Typography color="text.secondary" variant="h6">
                    ✓ No Active Alarms
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    All systems operational
                  </Typography>
                </TableCell>
              </TableRow>
            ) : (
              alarms.map((alarm) => (
                <TableRow
                  key={`${alarm.instance_id}-${alarm.id}`}
                  sx={{
                    backgroundColor: alarm.is_synthetic ? 'rgba(244, 67, 54, 0.1)' : 'inherit',
                    borderLeft: alarm.is_synthetic ? '4px solid #f44336' : alarm.acknowledged ? '4px solid #4caf50' : 'none',
                    '&:hover': { bgcolor: 'action.hover' },
                  }}
                >
                  <TableCell>
                    <Chip
                      icon={getSeverityIcon(alarm.severity)}
                      label={alarm.severity.toUpperCase()}
                      size="small"
                      sx={{
                        bgcolor: getSeverityColor(alarm.severity),
                        color: ['warning', 'average'].includes(alarm.severity) ? '#000' : '#fff',
                        fontWeight: 'bold',
                        fontSize: '0.7rem',
                      }}
                    />
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontWeight: 500 }}>
                      {alarm.instance_name}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace', fontWeight: 500 }}>
                      {alarm.host}
                    </Typography>
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2">
                      {alarm.description}
                    </Typography>
                    {alarm.is_synthetic && (
                      <Chip label="SYSTEM ALERT" size="small" color="error" sx={{ mt: 0.5, fontSize: '0.65rem' }} />
                    )}
                  </TableCell>
                  <TableCell>
                    <Typography variant="body2" sx={{ fontFamily: 'monospace' }}>
                      {alarm.duration}
                    </Typography>
                  </TableCell>
                  <TableCell align="center">
                    {alarm.acknowledged && (
                      <Tooltip title="Acknowledged">
                        <CheckCircle color="success" fontSize="small" />
                      </Tooltip>
                    )}
                  </TableCell>
                  <TableCell align="center">
                    <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                      <Tooltip title="Investigate with AI">
                        <IconButton size="small" color="primary">
                          <Search fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      {!alarm.acknowledged && !alarm.is_synthetic && (
                        <Tooltip title="Acknowledge">
                          <IconButton
                            size="small"
                            color="success"
                            onClick={(e) => {
                              e.stopPropagation();
                              handleAcknowledge(alarm);
                            }}
                          >
                            <CheckCircle fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      )}
                    </Box>
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </TableContainer>
    </Box>
  );
}
