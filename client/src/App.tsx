import { useState, useEffect, useCallback } from 'react';
import './App.css';
import AddJobForm from './components/AddJobForm';
import EditJobForm from './components/EditJobForm';

interface Job {
  job_id: number;
  department: string;
  shift: string;
}

function App() {
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
    await fetch(`/api/jobs/${idToDelete}`, {
      method: 'DELETE',
    });
    fetchJobs();
  };

  const handleJobUpdated = () => {
    setEditingJob(null); // Hide the edit form
    fetchJobs(); // Refresh the jobs list
  };

  return (
    <div>
      <h1>HR Management System</h1>
      <hr />

      {/* Conditionally render the forms */}
      {/* If we are editing a job, show the Edit form. */}
      {/* Otherwise, show the Add form. */}
      {editingJob ? (
        <EditJobForm 
          jobToEdit={editingJob} 
          onJobUpdated={handleJobUpdated}
          onCancel={() => setEditingJob(null)} 
        />
      ) : (
        <AddJobForm onJobAdded={fetchJobs} />
      )}

      <hr />
      <h2>Available Jobs</h2>
      <ul>
        {jobs.map(job => (
          <li key={job.job_id}>
            {job.department} - {job.shift || 'N/A'}

            {/* Add an Edit button for each job */}
            <button onClick={() => setEditingJob(job)} style={{ marginLeft: '10px' }}>
              Edit
            </button>

            <button onClick={() => handleDelete(job.job_id)} style={{ marginLeft: '10px' }}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;