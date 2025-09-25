import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

interface AddJobFormProps {
  onJobAdded: () => void;
}

function AddJobForm({ onJobAdded }: AddJobFormProps) {
  const [department, setDepartment] = useState('');
  const [shift, setShift] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await fetch('/api/jobs', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ department, shift }),
    });
    setDepartment('');
    setShift('');
    onJobAdded();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
      <Typography variant="h6">Add New Job</Typography>
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
      <Button type="submit" variant="contained">Add Job</Button>
    </Box>
  );
}

export default AddJobForm;