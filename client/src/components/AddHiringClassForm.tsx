import { useState } from 'react';

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
        <form onSubmit={handleSubmit}>
            <h3>Add New Hiring Class</h3>
            <div>
                <label>Class Date:</label>
                <input
                    type="date"
                    value={classDate}
                    onChange={(e) => setClassDate(e.target.value)}
                    required
                />
            </div>
            <button type="submit">Add Hiring Class</button>
        </form>
    );
}

export default AddHiringClassForm;