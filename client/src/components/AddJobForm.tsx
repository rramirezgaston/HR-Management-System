import { useState } from 'react';

// We define a "prop" for our component. It will be a function that
// this component can call to tell its parent (App.tsx) that a new
// job has been added, so the list can be refreshed.
interface AddJobFormProps {
  onJobAdded: () => void;
}

function AddJobForm({ onJobAdded }: AddJobFormProps) {
  // Create state variables to hold the values of our form inputs
  const [department, setDepartment] = useState('');
  const [shift, setShift] = useState('');

  // This function runs when the form is submitted
  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault(); // Prevent the default browser form submission

    // Send a POST request to our back-end API
    await fetch('/api/jobs', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ department, shift }),
    });

    // Clear the form inputs after submission
    setDepartment('');
    setShift('');

    // Call the function passed down from the parent to signal that we're done
    onJobAdded();
  };

  return (
    <form onSubmit={handleSubmit}>
      <h3>Add New Job</h3>
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
      <button type="submit">Add Job</button>
    </form>
  );
}

export default AddJobForm;