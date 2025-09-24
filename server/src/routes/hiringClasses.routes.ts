import { Router } from 'express';
import { getAllHiringClasses, createHiringClass, updateHiringClass, deleteHiringClass } from '../controllers/hiringClasses.controller';

const router = Router();

router.get('/', getAllHiringClasses);
router.post('/', createHiringClass);
router.put('/:id', updateHiringClass);
router.delete('/:id', deleteHiringClass);

export default router;