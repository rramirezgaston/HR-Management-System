import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';


interface EditHiringClassFormProps {
    hiringClassToEdit: {
        class_id: number;
        class_date: string;
    };
    onHiringClassUpdated: () => void;
    onCancel: () => void;
}

function EditHiringClassForm({ hiringClassToEdit, onHiringClassUpdated, onCancel }: EditHiringClassFormProps) {
    // Create state variable to hold the value of our form input, initialized with the current class date
    const [classDate, setClassDate] = useState(hiringClassToEdit.class_date);

    // This function runs when the form is submitted
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault(); // Prevent the default browser form submission

        // Send a PUT request to our back-end API to update the hiring class
        await fetch(`/api/hiring-classes/${hiringClassToEdit.class_id}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ class_date: classDate }),
        });

        // Call the function passed down from the parent to signal that we're done
        onHiringClassUpdated();
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
            <Typography variant="h6">Edit Hiring Class</Typography>
            <Box>
                <TextField
                type="date"
                value={classDate}
                onChange={(e) => setClassDate(e.target.value)}
                required
                fullWidth
                margin='normal'
                />
            </Box>
            <Button type="submit" variant="contained" sx={{ mr: 1 }}>Update Hiring Class</Button>
            <Button type="submit" variant="contained" sx={{ mr: 1 }} onClick={onCancel}>Cancel</Button>
        </Box>
    );
}

export default EditHiringClassForm;