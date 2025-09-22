import { useState, useEffect } from 'react';
import './App.css';

// Define a TypeScript "type" for our Job object to ensure type safety.
interface Job {
  job_id: number;
  department: string;
  shift: string;
}

function App() {
  // Create a state variable 'jobs' to hold our array of jobs.
  // It starts as an empty array [].
  const [jobs, setJobs] = useState<Job[]>([]);

  // useEffect runs when the component first loads.
  // The empty array [] at the end means it only runs once.
  useEffect(() => {
    // Fetch data from our back-end API.
    fetch('http://localhost:3001/api/jobs')
      .then(response => response.json())
      .then(data => setJobs(data)); // Update the 'jobs' state with the fetched data
  }, []);

  return (
    <div>
      <h1>HR Management System</h1>
      <h2>Available Jobs</h2>
      <ul>
        {/* Map over the 'jobs' array and create a list item for each one */}
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