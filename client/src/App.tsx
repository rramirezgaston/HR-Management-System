import { useState, useEffect, useCallback } from 'react';
import './App.css';
import AddJobForm from './components/AddJobForm'; // 1. Import the new component

interface Job {
  job_id: number;
  department: string;
  shift: string;
}

function App() {
  const [jobs, setJobs] = useState<Job[]>([]);

  // Create a function to fetch the jobs list.
  // We use useCallback to prevent it from being recreated on every render.
  const fetchJobs = useCallback(async () => {
    const response = await fetch('/api/jobs');
    const data = await response.json();
    setJobs(data);
  }, []);

  // useEffect now calls our fetchJobs function when the component loads.
  useEffect(() => {
    fetchJobs();
  }, [fetchJobs]);

  return (
    <div>
      <h1>HR Management System</h1>
      <hr />
      {/* 2. Display the new form component */}
      {/* We pass the fetchJobs function down to the form as a "prop" */}
      <AddJobForm onJobAdded={fetchJobs} />
      <hr />
      <h2>Available Jobs</h2>
      <ul>
        {jobs.map(job => (
          <li key={job.job_id}>
            {job.department} - {job.shift || 'N/A'}
          </li>
        ))}
      </ul>
    </div>
  );
}

export default App;