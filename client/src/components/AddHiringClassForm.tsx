import { useState } from 'react';
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import Button from '@mui/material/Button';
import Typography from '@mui/material/Typography';

interface AddHiringClassFormProps {
    onHiringClassAdded: () => void;
}

function AddHiringClassForm({ onHiringClassAdded }: AddHiringClassFormProps) {
    // Create state variable to hold the value of our form input
    const [classDate, setClassDate] = useState('');

    // This function runs when the form is submitted
    const handleSubmit = async (event: React.FormEvent) => {
        event.preventDefault(); // Prevent the default browser form submission

        // Send a POST request to our back-end API
        await fetch('/api/hiring-classes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ class_date: classDate }),
        });

        // Clear the form input after submission
        setClassDate('');

        // Call the function passed down from the parent to signal that we're done
        onHiringClassAdded();
    };

    return (
        <Box component="form" onSubmit={handleSubmit} sx={{ mb: 2 }}>
            <Typography variant="h6">Add New Hiring Class</Typography>
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
            <Button type="submit" variant="contained">Add Hiring Class</Button>
        </Box>
    );
}

export default AddHiringClassForm;