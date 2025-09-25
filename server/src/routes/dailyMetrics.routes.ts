import { Router } from 'express';
import { getMetrics, upsertMetrics } from '../controllers/dailyMetrics.controller';

const router = Router();

// A GET request to / will get metrics based on query parameters
router.get('/', getMetrics);
// A POST request to / will create or update metrics
router.post('/', upsertMetrics);

export default router;