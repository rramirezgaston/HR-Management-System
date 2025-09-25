import express from 'express';
import candidatesRouter from './routes/candidates.routes';
import interviewersRouter from './routes/interviewers.routes';
import hiringClassesRouter from './routes/hiringClasses.routes';
import jobsRouter from './routes/jobs.routes';
import dailyMetricsRouter from './routes/dailyMetrics.routes';

const app = express();
const port = 3001;

app.use(express.json());

app.use('/api/jobs', jobsRouter); 
app.use('/api/interviewers', interviewersRouter);
app.use('/api/candidates', candidatesRouter);
app.use('/api/hiring-classes', hiringClassesRouter);
app.use('/api/metrics', dailyMetricsRouter);


app.listen(port, () => {
  console.log(`Server is listening on http://localhost:${port}`);
});