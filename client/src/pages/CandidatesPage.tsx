import { useState, useEffect, useCallback } from 'react';
import '../App.css';
import AddCandidateForm from '../components/AddCandidateForm';
import EditCandidateForm from '../components/EditCandidateForm';

interface Candidate {
  candidate_id: number;
  first_name: string;
  last_name: string;
  candidate_status: string;
  fk_job_id: number | null;
  fk_class_id: number | null;
}

function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  // State to track which candidate is being edited
  const [editingCandidate, setEditingCandidate] = useState<Candidate | null>(null);

  const fetchCandidates = useCallback(async () => {
    const response = await fetch('/api/candidates');
    const data = await response.json();
    setCandidates(data);
  }, []);

  useEffect(() => {
    fetchCandidates();
  }, [fetchCandidates]);

  // Handler for deleting a candidate
  const handleDelete = async (idToDelete: number) => {
    await fetch(`/api/candidates/${idToDelete}`, {
      method: 'DELETE',
    });
    fetchCandidates(); // Refresh the list
  };

  // Handler that runs after a candidate is updated
  const handleCandidateUpdated = () => {
    setEditingCandidate(null); // Hide the edit form
    fetchCandidates(); // Refresh the list
  };

  return (
    <div>
      <h2>Manage Candidates</h2>
      <hr />

      {/* Conditionally render the Add or Edit form */}
      {editingCandidate ? (
        <EditCandidateForm
          candidateToEdit={editingCandidate}
          onCandidateUpdated={handleCandidateUpdated}
          onCancel={() => setEditingCandidate(null)}
        />
      ) : (
        <AddCandidateForm onCandidateAdded={fetchCandidates} />
      )}

      <hr />
      <h3>Current Candidates</h3>
      <ul>
        {candidates.map(candidate => (
          <li key={candidate.candidate_id}>
            {candidate.first_name} {candidate.last_name} ({candidate.candidate_status})

            {/* Add Edit and Delete buttons */}
            <button onClick={() => setEditingCandidate(candidate)} style={{ marginLeft: '10px' }}>
              Edit
            </button>
            <button onClick={() => handleDelete(candidate.candidate_id)} style={{ marginLeft: '10px' }}>
              Delete
            </button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default CandidatesPage;