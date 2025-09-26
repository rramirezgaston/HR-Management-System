import { useState, useEffect, useCallback } from 'react';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import ListItemText from '@mui/material/ListItemText';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';
import Box from '@mui/material/Box';
import AddInterviewerForm from '../components/AddInterviewerForm';
import EditInterviewerForm from '../components/EditInterviewerForm';

interface Interviewer {
    interviewer_id: number;
    interviewer_name: string;
}

function InterviewersPage() {
    const [interviewers, setInterviewers] = useState<Interviewer[]>([]);
    // State to track which interviewer is being edited
    const [editingInterviewer, setEditingInterviewer] = useState<Interviewer | null>(null);

    const fetchInterviewers = useCallback(async () => {
        const response = await fetch('/api/interviewers');
        const data = await response.json();
        setInterviewers(data);
    }, []);

    useEffect(() => {
        fetchInterviewers();
    }, [fetchInterviewers]);

    // Handler for deleting an interviewer
    const handleDelete = async (idToDelete: number) => {
        await fetch(`/api/interviewers/${idToDelete}`, {
            method: 'DELETE',
        });
        fetchInterviewers(); // Refresh the list
    };

    // Handler that runs after an interviewer is updated
    const handleInterviewerUpdated = () => {
        setEditingInterviewer(null); // Hide the edit form
        fetchInterviewers(); // Refresh the list
    };

return (
    <Box>
      <Typography variant="h4" gutterBottom>Manage Interviewers</Typography>
      
      
      {editingInterviewer ? (
        <EditInterviewerForm
          interviewerToEdit={editingInterviewer}
          onInterviewerUpdated={handleInterviewerUpdated}
          onCancel={() => setEditingInterviewer(null)}
        />
      ) : (
        <AddInterviewerForm onInterviewerAdded={fetchInterviewers} />
      )}

      <Typography variant="h5" sx={{ mt: 4 }}>Current Interviewers</Typography>
      <List>
        {interviewers.map(interviewer => (
          <ListItem
            key={interviewer.interviewer_id}
            secondaryAction={
              <>
                <IconButton edge="end" aria-label="edit" onClick={() => setEditingInterviewer(interviewer)}>
                  <EditIcon />
                </IconButton>
                <IconButton edge="end" aria-label="delete" onClick={() => handleDelete(interviewer.interviewer_id)}>
                  <DeleteIcon />
                </IconButton>
              </>
            }
          >
            <ListItemText
              primary={interviewer.interviewer_name}
            />
          </ListItem>
        ))}
      </List>
    </Box>
  );
}


export default InterviewersPage;