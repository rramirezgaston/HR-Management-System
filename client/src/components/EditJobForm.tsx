import { useState, useEffect } from 'react';

// Define the shape of a Job object
interface Job {
  job_id: number;
  department: string;
  shift: string;
}

// Define the props our component will accept
interface EditJobFormProps {
  jobToEdit: Job;
  onJobUpdated: () => void;
  onCancel: () => void;
}

function EditJobForm({ jobToEdit, onJobUpdated, onCancel }: EditJobFormProps) {
  // State to manage the form inputs
  const [department, setDepartment] = useState('');
  const [shift, setShift] = useState('');

  // This useEffect hook runs whenever the 'jobToEdit' prop changes.
  // It pre-populates the form with the current job's data.
  useEffect(() => {
    setDepartment(jobToEdit.department);
    setShift(jobToEdit.shift || '');
  }, [jobToEdit]);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();

    // Send a PUT request to our back-end API
    await fetch(`/api/jobs/${jobToEdit.job_id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ department, shift }),
    });

    // Tell the parent component that the update is complete
    onJobUpdated();
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Edit Job: {jobToEdit.department}</h3>
      <div>
        <label>Department:</label>
        <input
          type="text"
          value={department}
          onChange={(e) => setDepartment(e.target.value)}
          required
        />
      </div>
      <div>
        <label>Shift:</label>
        <input
          type="text"
          value={shift}
          onChange={(e) => setShift(e.target.value)}
        />
      </div>
      <button type="submit">Save Changes</button>
      {/* The cancel button simply calls the onCancel function from the parent */}
      <button type="button" onClick={onCancel}>Cancel</button>
    </form>
  );
}

export default EditJobForm;