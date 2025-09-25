import { useState, useEffect, useCallback } from 'react';
import AddJobForm from '../components/AddJobForm';
import EditJobForm from '../components/EditJobForm';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

interface Job {
  job_id: number; department: string; shift: string;
}

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [editingJob, setEditingJob] = useState<Job | null>(null);

  const fetchJobs = useCallback(async () => {
    const response = await fetch('/api/jobs');
    const data = await response.json();
    setJobs(data);
  }, []);

  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  const handleDelete = async (idToDelete: number) => {
    await fetch(`/api/jobs/${idToDelete}`, { method: 'DELETE' });
    fetchJobs();
  };

  const handleJobUpdated = () => {
    setEditingJob(null);
    fetchJobs();
  };

  return (
    <div>
      <Typography variant="h4" gutterBottom>Manage Jobs</Typography>

      {editingJob ? (
        <EditJobForm
          jobToEdit={editingJob}
          onJobUpdated={handleJobUpdated}
          onCancel={() => setEditingJob(null)}
        />
      ) : (
        <AddJobForm onJobAdded={fetchJobs} />
      )}

      <Typography variant="h5" sx={{ mt: 4 }}>Current Jobs</Typography>
      <List>
        {jobs.map(job => (
          <ListItem
            key={job.job_id}
            secondaryAction={
              <>
                <IconButton edge="end" aria-label="edit" onClick={() => setEditingJob(job)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" aria-label="delete" onClick={() => handleDelete(job.job_id)}>
                  <DeleteIcon />
                </IconButton>
              </>
            }
          >
            <ListItemText
              primary={job.department}
              secondary={job.shift || 'N/A'}
            />
          </ListItem>
        ))}
      </List>
    </div>
  );
}