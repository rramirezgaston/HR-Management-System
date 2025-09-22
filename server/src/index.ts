import express from 'express';
import db from './database'; // Import our new database connection

const app = express();
const port = 3001;

// We change this route handler to be an 'async' function
// so we can use 'await' for our database query.
app.get('/', async (req, res) => {
  try {
    // Use our 'db' object to run a raw SQL query.
    // This query simply asks the database for its version number.
    const result = await db.raw('SELECT sqlite_version()');

    // Send the result back as a JSON object
    res.json({ message: 'Server is connected to the database!', sqliteVersion: result });

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to connect to the database.' });
  }
});

app.listen(port, () => {
  console.log(`Server is listening on http://localhost:${port}`);
});