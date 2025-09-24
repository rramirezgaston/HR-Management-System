import { Request, Response } from 'express';
import db from '../database';

export const getAllJobs = async (req: Request, res: Response) => {
  try {
    const jobs = await db('Jobs').select('*');
    res.json(jobs);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch jobs.' });
  }
};

export const createJob = async (req: Request, res: Response) => {
  try {
    const { department, shift } = req.body;
    const newJob = await db('Jobs').insert({ department, shift }).returning('*');
    res.status(201).json(newJob[0]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create job.' });
  }
};

export const updateJob = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const { department, shift } = req.body;
    const updatedJob = await db('Jobs').where({ job_id: id }).update({ department, shift }).returning('*');
    if (updatedJob.length > 0) {
      res.json(updatedJob[0]);
    } else {
      res.status(404).json({ error: 'Job not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to update job.' });
  }
};

export const deleteJob = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const deletedCount = await db('Jobs').where({ job_id: id }).del();
    if (deletedCount > 0) {
      res.status(204).send();
    } else {
      res.status(404).json({ error: 'Job not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete job.' });
  }
};