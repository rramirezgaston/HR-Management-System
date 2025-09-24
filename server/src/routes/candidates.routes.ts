import { Router } from 'express';
import { getAllCandidates, createCandidate, updateCandidate, deleteCandidate } from '../controllers/candidates.controller';

const router = Router();

router.get('/', getAllCandidates);
router.post('/', createCandidate);
router.put('/:id', updateCandidate);
router.delete('/:id', deleteCandidate);

export default router;