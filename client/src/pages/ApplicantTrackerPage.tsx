import { useState, useEffect, useCallback } from 'react';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Select, { type SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Grid from '@mui/material/Grid';
import Paper from '@mui/material/Paper';

// --- Data Interfaces ---
interface Breakdown { category: string; reason: string; count: number; }
interface MetricsData { apps_reviewed: number; interviews_scheduled: number; hires_confirmed: number; breakdowns: Breakdown[]; }

// --- Main Component ---
export default function ApplicantTrackerPage() {
  // --- State Management ---
  const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split('T')[0]);
  const [departments, setDepartments] = useState<string[]>([]);
  const [selectedDepartment, setSelectedDepartment] = useState('');
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);

  // --- Data Fetching ---
  useEffect(() => {
    const depts = ["Selectors", "Shipping", "Receiving"];
    setDepartments(depts);
    if(depts.length > 0) setSelectedDepartment(depts[0]);
  }, []);

  const fetchMetrics = useCallback(async () => {
    if (!selectedDate || !selectedDepartment) return;
    const response = await fetch(`/api/metrics?date=${selectedDate}&department=${selectedDepartment}`);
    const data = await response.json();
    setMetricsData(data);
  }, [selectedDate, selectedDepartment]);

  useEffect(() => {
    fetchMetrics();
  }, [fetchMetrics]);

  // --- Event Handlers ---
  const handleMetricChange = (field: keyof Omit<MetricsData, 'breakdowns'>, value: string) => {
    if (!metricsData) return;
    const numberValue = parseInt(value) || 0;
    setMetricsData({ ...metricsData, [field]: numberValue });
  };

  const handleBreakdownChange = (category: string, reason: string, value: string) => {
    if (!metricsData) return;
    const numberValue = parseInt(value) || 0;
    const newBreakdowns = [...(metricsData.breakdowns || [])];
    const existing = newBreakdowns.find(b => b.category === category && b.reason === reason);
    if (existing) {
      existing.count = numberValue;
    } else {
      newBreakdowns.push({ category, reason, count: numberValue });
    }
    setMetricsData({ ...metricsData, breakdowns: newBreakdowns });
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!metricsData) return;
    await fetch('/api/metrics', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date: selectedDate, department: selectedDepartment, ...metricsData }),
    });
    alert('Metrics saved successfully!');
  };

  const getBreakdownValue = (category: string, reason: string) => {
    return metricsData?.breakdowns?.find(b => b.category === category && b.reason === reason)?.count || 0;
  }

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="h4" gutterBottom>Applicant Tracker</Typography>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Grid container spacing={2} alignItems="center">
          <Grid size={{xs:12, sm:4}}>
            <TextField type="date" label="Select Date" value={selectedDate} onChange={(e) => setSelectedDate(e.target.value)} fullWidth InputLabelProps={{ shrink: true }} />
          </Grid>
          <Grid size={{xs:12, sm:4}}>
            <FormControl fullWidth>
              <InputLabel id="dept-select-label">Department</InputLabel>
              <Select labelId="dept-select-label" value={selectedDepartment} label="Department" onChange={(e: SelectChangeEvent) => setSelectedDepartment(e.target.value)}>
                {departments.map(dept => <MenuItem key={dept} value={dept}>{dept}</MenuItem>)}
              </Select>
            </FormControl>
          </Grid>
        </Grid>
      </Paper>

      <Paper sx={{ p: 2, mb: 3 }}>
        <Typography variant="h6" gutterBottom>Daily Metrics</Typography>
        <Grid container spacing={2}>
          <Grid size={{xs:4}}><TextField type="number" label="Apps Reviewed" value={metricsData?.apps_reviewed || 0} onChange={(e) => handleMetricChange('apps_reviewed', e.target.value)} fullWidth /></Grid>
          <Grid size={{xs:4}}><TextField type="number" label="Interviews Scheduled" value={metricsData?.interviews_scheduled || 0} onChange={(e) => handleMetricChange('interviews_scheduled', e.target.value)} fullWidth /></Grid>
          <Grid size={{xs:4}}><TextField type="number" label="Hires Confirmed" value={metricsData?.hires_confirmed || 0} onChange={(e) => handleMetricChange('hires_confirmed', e.target.value)} fullWidth /></Grid>
        </Grid>
      </Paper>

      <Grid container spacing={3}>
        <Grid size={{xs:12, sm:6}}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Rejections</Typography>
            <TextField sx={{ mb: 1 }} type="number" label="Pre-Interview: Not eligible for Rehire" value={getBreakdownValue('pre_interview_rejection', 'Not eligible for Rehire')} onChange={(e) => handleBreakdownChange('pre_interview_rejection', 'Not eligible for Rehire', e.target.value)} fullWidth />
            <TextField sx={{ mb: 1 }} type="number" label="Post-Interview: NCNS" value={getBreakdownValue('post_interview_rejection', 'NCNS')} onChange={(e) => handleBreakdownChange('post_interview_rejection', 'NCNS', e.target.value)} fullWidth />
          </Paper>
        </Grid>
        <Grid size={{xs:12, sm:6}}>
          <Paper sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom>Withdrawals</Typography>
            <TextField sx={{ mb: 1 }} type="number" label="Pre-Interview: Other Job Offer" value={getBreakdownValue('pre_interview_withdrawal', 'Other Job Offer')} onChange={(e) => handleBreakdownChange('pre_interview_withdrawal', 'Other Job Offer', e.target.value)} fullWidth />
            <TextField sx={{ mb: 1 }} type="number" label="Post-Interview: Pay" value={getBreakdownValue('post_interview_withdrawal', 'Pay')} onChange={(e) => handleBreakdownChange('post_interview_withdrawal', 'Pay', e.target.value)} fullWidth />
          </Paper>
        </Grid>
      </Grid>

      <Button type="submit" variant="contained" sx={{ mt: 3 }}>Save Metrics</Button>
    </Box>
  );
}