import express from 'express';
import db from './database';

const app = express();
const port = 3001;

// Middleware to parse JSON bodies
app.use(express.json());

// GET endpoint
app.get('/api/jobs', async (req, res) => {
  try {
    const jobs = await db('Jobs').select('*');
    res.json(jobs);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to fetch jobs.' });
  }
});

// POST endpoint
app.post('/api/jobs', async (req, res) => {
  try {
    const { department, shift } = req.body;
    const newJob = await db('Jobs').insert({ department, shift }).returning('*');
    res.status(201).json(newJob[0]);
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'Failed to create job.' });
  }
});

app.listen(port, () => {
  console.log(`Server is listening on http://localhost:${port}`);
});