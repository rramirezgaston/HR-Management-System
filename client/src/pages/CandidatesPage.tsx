import { useState, useEffect, useCallback } from 'react';
import AddCandidateForm from '../components/AddCandidateForm';
import EditCandidateForm from '../components/EditCandidateForm';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

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
      <Typography variant="h4" gutterBottom>Manage Candidates</Typography>
      
      {editingCandidate ? (
        <EditCandidateForm
          candidateToEdit={editingCandidate}
          onCandidateUpdated={handleCandidateUpdated}
          onCancel={() => setEditingCandidate(null)}
        />
      ) : (
        <AddCandidateForm onCandidateAdded={fetchCandidates} />
      )}

      <Typography variant="h5" sx={{ mt: 4 }}>Current Candidates</Typography>
      <List>
        {candidates.map(candidate => (
          <ListItem key={candidate.candidate_id}>
            {candidate.first_name} {candidate.last_name} ({candidate.candidate_status})
           
            <IconButton edge="end" aria-label="edit" onClick={() => setEditingCandidate(candidate)} style={{ marginLeft: '10px' }}>
              <EditIcon />
            </IconButton>
            <IconButton edge="end" aria-label="edit" onClick={() => handleDelete(candidate.candidate_id)} style={{ marginLeft: '10px' }}>
              <DeleteIcon />
            </IconButton>
          </ListItem>
        ))}
      </List>
    </div>
  );
}

export default CandidatesPage;