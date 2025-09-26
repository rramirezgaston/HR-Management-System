import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

interface AddInterviewerFormProps {
  onInterviewerAdded: () => void;
}

function AddInterviewerForm({ onInterviewerAdded }: AddInterviewerFormProps) {
  const [name, setName] = useState('');

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await fetch('/api/interviewers', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interviewer_name: name }),
    });
    setName('');
    onInterviewerAdded();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
      <Typography variant="h6">Add New Interviewer</Typography>
      <TextField
        label="Interviewer Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
        fullWidth
        margin="normal"
      />
      <Button type="submit" variant="contained">Add Interviewer</Button>
    </Box>
  );
}

export default AddInterviewerForm;