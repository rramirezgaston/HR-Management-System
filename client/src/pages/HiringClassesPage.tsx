import { useState, useEffect, useCallback } from 'react';
import '../App.css';
import AddHiringClassForm from '../components/AddHiringClassForm';
import EditHiringClassForm from '../components/EditHiringClassForm';

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
      <h2>Manage Hiring Classes</h2>
      <hr />

      {/* Conditionally render the Add or Edit form */}
      {editingHiringClass ? (
        <EditHiringClassForm
          hiringClassToEdit={editingHiringClass}
          onHiringClassUpdated={handleHiringClassUpdated}
          onCancel={() => setEditingHiringClass(null)}
        />
      ) : (
        <AddHiringClassForm onHiringClassAdded={fetchHiringClasses} />
      )}

      <hr />
      <h3>Current Hiring Classes</h3>
      <ul>
        {hiringClasses.map((hc) => (
          <li key={hc.class_id}>
            {new Date(hc.class_date).toLocaleDateString('en-US', { timeZone: 'UTC' })}
            <button onClick={() => setEditingHiringClass(hc)}>Edit</button>{' '}
            <button onClick={() => handleDelete(hc.class_id)}>Delete</button>
          </li>
        ))}
      </ul>
    </div>
  );
}

export default HiringClassesPage;