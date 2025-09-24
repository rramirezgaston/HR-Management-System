import { useState, useEffect } from 'react';

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
    <form onSubmit={handleSubmit}>
      <h3>Add New Candidate</h3>
      <div>
        <label>First Name:</label>
        <input
          type="text"
          value={firstName}
          onChange={(e) => setFirstName(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Last Name:</label>
        <input
          type="text"
          value={lastName}
          onChange={(e) => setLastName(e.target.value)}
          required
        />
      </div>
      {/* Dropdown for Jobs */}
      <div>
        <label>Job:</label>
        <select value={fkJobId} onChange={(e) => setFkJobId(e.target.value)}>
          <option value="">-- Select a Job --</option>
          {jobs.map(job => (
            <option key={job.job_id} value={job.job_id}>
              {job.department} - {job.shift || 'N/A'}
            </option>
          ))}
        </select>
      </div>
      {/* Dropdown for Hiring Classes */}
      <div>
        <label>Hiring Class:</label>
        <select value={fkClassId} onChange={(e) => setFkClassId(e.target.value)}>
          <option value="">-- Select a Class --</option>
          {hiringClasses.map(hc => (
            <option key={hc.class_id} value={hc.class_id}>
              {new Date(hc.class_date).toLocaleDateString('en-US', { timeZone: 'UTC' })}
            </option>
          ))}
        </select>
      </div>
      <button type="submit">Add Candidate</button>
    </form>
  );
}

export default AddCandidateForm;