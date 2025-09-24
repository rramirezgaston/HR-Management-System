import { useState } from 'react';

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
        <form onSubmit={handleSubmit}>
            <h3>Edit Hiring Class</h3>
            <div>
                <label>Class Date:</label>
                <input
                    type="date"
                    value={classDate}
                    onChange={(e) => setClassDate(e.target.value)}
                    required
                />
            </div>
            <button type="submit">Update Hiring Class</button>
            <button type="button" onClick={onCancel}>Cancel</button>
        </form>
    );
}

export default EditHiringClassForm;