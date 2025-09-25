import { useState, useEffect } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';
import Select from '@mui/material/Select';
import type { SelectChangeEvent } from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';


// Define the shapes of our data objects
interface Candidate {
  candidate_id: number;
  first_name: string;
  last_name: string;
  candidate_status: string;
  fk_job_id: number | null;
  fk_class_id: number | null;
}

interface Job {
  job_id: number;
  department: string;
  shift: string;
}

interface HiringClass {
  class_id: number;
  class_date: string;
}

interface EditCandidateFormProps {
  candidateToEdit: Candidate;
  onCandidateUpdated: () => void;
  onCancel: () => void;
}

function EditCandidateForm({ candidateToEdit, onCandidateUpdated, onCancel }: EditCandidateFormProps) {
  // State for form inputs
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [fkJobId, setFkJobId] = useState<string>('');
  const [fkClassId, setFkClassId] = useState<string>('');

  // State to hold the lists for the dropdowns
  const [jobs, setJobs] = useState<Job[]>([]);
  const [hiringClasses, setHiringClasses] = useState<HiringClass[]>([]);

  // useEffect to fetch data for dropdowns when the component loads
  useEffect(() => {
    const fetchJobs = async () => {
      const response = await fetch('/api/jobs');
      setJobs(await response.json());
    };
    const fetchHiringClasses = async () => {
      const response = await fetch('/api/hiring-classes');
      setHiringClasses(await response.json());
    };
    fetchJobs();
    fetchHiringClasses();
  }, []);

  // useEffect to pre-populate the form when a candidate is selected for editing
  useEffect(() => {
    if (candidateToEdit) {
      setFirstName(candidateToEdit.first_name);
      setLastName(candidateToEdit.last_name);
      // Set the dropdowns to the candidate's current job/class, or empty if null
      setFkJobId(candidateToEdit.fk_job_id?.toString() || '');
      setFkClassId(candidateToEdit.fk_class_id?.toString() || '');
    }
  }, [candidateToEdit]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    await fetch(`/api/candidates/${candidateToEdit.candidate_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        first_name: firstName,
        last_name: lastName,
        fk_job_id: fkJobId ? parseInt(fkJobId) : null,
        fk_class_id: fkClassId ? parseInt(fkClassId) : null,
      }),
    });

    onCandidateUpdated();
  };

  return (
    <Box component="form" onSubmit={handleSubmit}>
      <Typography variant="h6">Edit Candidate: {candidateToEdit.first_name} {candidateToEdit.last_name}</Typography>
        <TextField
          label="First Name"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
          fullWidth
          margin="normal"
        />
        <TextField
          label="Last Name"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
          fullWidth
          margin="normal"
        />
      <FormControl fullWidth margin="normal">
        <InputLabel id="job-select-label">Job:</InputLabel>
        <Select labelId="job-select-label" value={fkJobId} label="Job" onChange={(e: SelectChangeEvent) => setFkJobId(e.target.value)}>
          {jobs.map(job => (
            <MenuItem key={job.job_id} value={job.job_id}>
              {job.department} - {job.shift || 'N/A'}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <FormControl fullWidth margin="normal">
        <InputLabel id="class-select-label">Hiring Class</InputLabel>
        <Select labelId="class-select-label" value={fkClassId} label="Hiring Class" onChange={(e: SelectChangeEvent) => setFkClassId(e.target.value)}>
          {hiringClasses.map(hc => (
            <MenuItem key={hc.class_id} value={hc.class_id}>
              {new Date(hc.class_date).toLocaleDateString('en-US', { timeZone: 'UTC' })}
            </MenuItem>
          ))}
        </Select>
      </FormControl>
      <Button type="submit" variant="contained">Save Changes</Button>
      <Button type="button" variant="contained" onClick={onCancel}>Cancel</Button>
    </Box>
  );
}

export default EditCandidateForm;