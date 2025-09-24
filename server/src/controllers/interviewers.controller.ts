import { Request, Response } from 'express';
import db from '../database';

export const getAllInterviewers = async (req: Request, res: Response) => {
  try {
    const interviewers = await db('Interviewers').select('*');
    res.json(interviewers);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch interviewers.' });
  }
};

export const createInterviewer = async (req: Request, res: Response) => {
  try {
    const newInterviewer = await db('Interviewers').insert(req.body).returning('*');
    res.status(201).json(newInterviewer[0]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create interviewer.' });
  }
};

export const updateInterviewer = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updatedInterviewer = await db('Interviewers')
      .where({ interviewer_id: id })
      .update(req.body)
      .returning('*');

    if (updatedInterviewer.length > 0) {
      res.json(updatedInterviewer[0]);
    } else {
      res.status(404).json({ error: 'Interviewer not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to update interviewer.' });
  }
};

export const deleteInterviewer = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const deletedCount = await db('Interviewers').where({ interviewer_id: id }).del();

    if (deletedCount > 0) {
      res.status(204).send();
    } else {
      res.status(404).json({ error: 'Interviewer not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete interviewer.' });
  }
};