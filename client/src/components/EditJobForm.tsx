import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

interface Job {
  job_id: number; department: string; shift: string;
}
interface EditJobFormProps {
  jobToEdit: Job;
  onJobUpdated: () => void;
  onCancel: () => void;
}

function EditJobForm({ jobToEdit, onJobUpdated, onCancel }: EditJobFormProps) {
  const [department, setDepartment] = useState('');
  const [shift, setShift] = useState('');

  useEffect(() => {
    setDepartment(jobToEdit.department);
    setShift(jobToEdit.shift || '');
  }, [jobToEdit]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await fetch(`/api/jobs/${jobToEdit.job_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ department, shift }),
    });
    onJobUpdated();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
      <Typography variant="h6">Edit Job: {jobToEdit.department}</Typography>
      <TextField
        label="Department"
        value={department}
        onChange={(e) => setDepartment(e.target.value)}
        required
        fullWidth
        margin="normal"
      />
      <TextField
        label="Shift"
        value={shift}
        onChange={(e) => setShift(e.target.value)}
        fullWidth
        margin="normal"
      />
      <Box sx={{ mt: 1 }}>
        <Button type="submit" variant="contained" sx={{ mr: 1 }}>Save Changes</Button>
        <Button type="button" variant="outlined" onClick={onCancel}>Cancel</Button>
      </Box>
    </Box>
  );
}

export default EditJobForm;