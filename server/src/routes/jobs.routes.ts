import { Router } from 'express';
import { getAllJobs, createJob, updateJob, deleteJob } from '../controllers/jobs.controller';

const router = Router();

router.get('/', getAllJobs);
router.post('/', createJob);
router.put('/:id', updateJob);
router.delete('/:id', deleteJob);

export default router;