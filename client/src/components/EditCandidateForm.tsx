import { useState, useEffect } from 'react';

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
    <form onSubmit={handleSubmit}>
      <h3>Edit Candidate: {candidateToEdit.first_name} {candidateToEdit.last_name}</h3>
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
      <button type="submit">Save Changes</button>
      <button type="button" onClick={onCancel}>Cancel</button>
    </form>
  );
}

export default EditCandidateForm;