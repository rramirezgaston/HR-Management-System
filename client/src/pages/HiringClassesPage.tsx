import { useState, useEffect, useCallback } from 'react';
import AddHiringClassForm from '../components/AddHiringClassForm';
import EditHiringClassForm from '../components/EditHiringClassForm';
import Typography from '@mui/material/Typography';
import List from '@mui/material/List';
import ListItem from '@mui/material/ListItem';
import IconButton from '@mui/material/IconButton';
import EditIcon from '@mui/icons-material/Edit';
import DeleteIcon from '@mui/icons-material/Delete';

interface HiringClass {
  class_id: number;
  class_date: string;
}

function HiringClassesPage() {
  const [hiringClasses, setHiringClasses] = useState<HiringClass[]>([]);
  // State to track which hiring class is being edited
  const [editingHiringClass, setEditingHiringClass] = useState<HiringClass | null>(null);

  const fetchHiringClasses = useCallback(async () => {
    const response = await fetch('/api/hiring-classes');
    const data = await response.json();
    setHiringClasses(data);
  }, []);

  useEffect(() => {
    fetchHiringClasses();
  }, [fetchHiringClasses]);

  // Handler for deleting a hiring class
  const handleDelete = async (idToDelete: number) => {
    await fetch(`/api/hiring-classes/${idToDelete}`, {
      method: 'DELETE',
    });
    fetchHiringClasses(); // Refresh the list
  };

  // Handler that runs after a hiring class is updated
  const handleHiringClassUpdated = () => {
    setEditingHiringClass(null); // Hide the edit form
    fetchHiringClasses(); // Refresh the list
  };

  return (
    <div>
      <Typography>Manage Hiring Classes</Typography>
      
      {editingHiringClass ? (
        <EditHiringClassForm
          hiringClassToEdit={editingHiringClass}
          onHiringClassUpdated={handleHiringClassUpdated}
          onCancel={() => setEditingHiringClass(null)}
        />
      ) : (
        <AddHiringClassForm onHiringClassAdded={fetchHiringClasses} />
      )}

      <Typography variant="h5" sx={{ mt: 4 }}>Current Hiring Classes</Typography>
      <List>
        {hiringClasses.map((hc) => (
          <ListItem key={hc.class_id}>
            {new Date(hc.class_date).toLocaleDateString('en-US', { timeZone: 'UTC' })}
            <IconButton edge="end" aria-label="edit" onClick={() => setEditingHiringClass(hc)}>
              <EditIcon />
            </IconButton>
            <IconButton edge="end" aria-label="edit" onClick={() => handleDelete(hc.class_id)}>
              <DeleteIcon />
            </IconButton>
          </ListItem>
        ))}
      </List>
    </div>
  );
}

export default HiringClassesPage;