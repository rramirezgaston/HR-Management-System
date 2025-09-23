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

app.put('/api/jobs/:id', async (req, res) => {
  try {
    const {id} = req.params;
    const {department, shift} = req.body;

    const updatedJob = await db('Jobs')
      .where({job_id: id})
      .update({department, shift})
      .returning('*');

    if (updatedJob.length > 0) {
      res.json(updatedJob[0]);
    } else {
      res.status(404).json({error: 'Job not found.'});
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({error: 'Failed to update job.'});
  }
});

app.delete('/api/jobs/:id', async (req, res) => {
  try {
    const {id} = req.params;
    const deletedCount = await db('Jobs').where({job_id: id}).del();

    if (deletedCount > 0) {
      res.status(204).send();
    } else {
      res.status(404).json({error: 'Job nor found.'});
    }
  } catch (error) {
    console.error(error);
    res.status(500).json({error: 'Failed to delete job.'});
  }
});

app.listen(port, () => {
  console.log(`Server is listening on http://localhost:${port}`);
});