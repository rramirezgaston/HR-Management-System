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

// Define the shapes of the data we'll be fetching
interface Job {
  job_id: number;
  department: string;
  shift: string;
}

interface HiringClass {
  class_id: number;
  class_date: string;
}

interface AddCandidateFormProps {
  onCandidateAdded: () => void;
}

function AddCandidateForm({ onCandidateAdded }: AddCandidateFormProps) {
  // State for the form inputs
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [fkJobId, setFkJobId] = useState(''); // State for the selected job ID
  const [fkClassId, setFkClassId] = useState(''); // State for the selected class ID

  // State to hold the lists of jobs and classes for the dropdowns
  const [jobs, setJobs] = useState<Job[]>([]);
  const [hiringClasses, setHiringClasses] = useState<HiringClass[]>([]);

  // useEffect hook to fetch data when the component first loads
  useEffect(() => {
    // Fetch the list of jobs
    const fetchJobs = async () => {
      const response = await fetch('/api/jobs');
      setJobs(await response.json());
    };

    // Fetch the list of hiring classes
    const fetchHiringClasses = async () => {
      const response = await fetch('/api/hiring-classes');
      setHiringClasses(await response.json());
    };

    fetchJobs();
    fetchHiringClasses();
  }, []); // The empty array ensures this runs only once

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    await fetch('/api/candidates', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      // Send all the data, including the selected foreign keys
      body: JSON.stringify({ 
        first_name: firstName, 
        last_name: lastName, 
        candidate_status: 'Pending',
        fk_job_id: fkJobId ? parseInt(fkJobId) : null,
        fk_class_id: fkClassId ? parseInt(fkClassId) : null,
      }),
    });

    // Reset the form
    setFirstName('');
    setLastName('');
    setFkJobId('');
    setFkClassId('');
    onCandidateAdded();
  };

   return (
    <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
      <Typography variant="h6">Add New Candidate</Typography>
      <TextField
      label="First Name"
      value={firstName} onChange={(e) => setFirstName(e.target.value)}
      required
      fullWidth
      margin="normal"
      />
      <TextField
      label="Last Name"
      value={lastName} onChange={(e) => setLastName(e.target.value)}
      required
      fullWidth
      margin="normal"
      />

      <FormControl fullWidth margin="normal">
        <InputLabel id="job-select-label">Job</InputLabel>
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

      <Button type="submit" variant="contained">Add Candidate</Button>
    </Box>
  );
}

export default AddCandidateForm;