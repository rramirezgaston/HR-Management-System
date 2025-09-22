import express from 'express';
import db from './database'; // Our database connection
import cors from 'cors'; // Import CORS middleware

const app = express();
const port = 3001;

app.use(cors()); // Enable CORS for all routes
// Define our API endpoint at the URL '/api/jobs'
app.get('/api/jobs', async (req, res) => {
  try {
    // Use Knex to build a query: SELECT * FROM "Jobs"
    const jobs = await db('Jobs').select('*');

    // Send the list of jobs back as a JSON response
    res.json(jobs);

  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to fetch jobs.' });
  }
});

app.listen(port, () => {
  console.log(`Server is listening on http://localhost:${port}`);
});