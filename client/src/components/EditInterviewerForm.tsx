import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

interface Interviewer {
  interviewer_id: number;
  interviewer_name: string;
}
interface EditInterviewerFormProps {
  interviewerToEdit: Interviewer;
  onInterviewerUpdated: () => void;
  onCancel: () => void;
}

function EditInterviewerForm({ interviewerToEdit, onInterviewerUpdated, onCancel }: EditInterviewerFormProps) {
  const [name, setName] = useState('');

  useEffect(() => {
    setName(interviewerToEdit.interviewer_name);
  }, [interviewerToEdit]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    await fetch(`/api/interviewers/${interviewerToEdit.interviewer_id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ interviewer_name: name }),
    });
    onInterviewerUpdated();
  };

  return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
      <Typography variant="h6">Edit Interviewer</Typography>
      <TextField
        label="Interviewer Name"
        value={name}
        onChange={(e) => setName(e.target.value)}
        required
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

export default EditInterviewerForm;