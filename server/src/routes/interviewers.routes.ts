import { Router } from 'express';
import { getAllInterviewers, createInterviewer, updateInterviewer, deleteInterviewer } from '../controllers/interviewers.controller';

const router = Router();

router.get('/', getAllInterviewers);
router.post('/', createInterviewer);
router.put('/:id', updateInterviewer);
router.delete('/:id', deleteInterviewer);

export default router;