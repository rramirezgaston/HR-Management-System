import { Router } from 'express';
import { getAllJobs, createJob, updateJob, deleteJob } from '../controllers/jobs.controller';
import validate from '../middleware/validateResource';
import { createJobSchema } from '../schemas/job.schema';

const router = Router();

// GET all jobs
router.get('/', getAllJobs);

// POST a new job (now with validation)
router.post('/', validate(createJobSchema), createJob);

// PUT to update a job by ID
router.put('/:id', updateJob);

// DELETE a job by ID
router.delete('/:id', deleteJob);

export default router;