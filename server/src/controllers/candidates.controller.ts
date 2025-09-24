import { Request, Response } from 'express';
import db from '../database';

export const getAllCandidates = async (req: Request, res: Response) => {
  try {
    const candidates = await db('Candidates').select('*');
    res.json(candidates);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch candidates.' });
  }
};

export const createCandidate = async (req: Request, res: Response) => {
  try {
    const newCandidate = await db('Candidates').insert(req.body).returning('*');
    res.status(201).json(newCandidate[0]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create candidate.' });
  }
};

export const updateCandidate = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updatedCandidate = await db('Candidates')
      .where({ candidate_id: id })
      .update(req.body)
      .returning('*');

    if (updatedCandidate.length > 0) {
      res.json(updatedCandidate[0]);
    } else {
      res.status(404).json({ error: 'Candidate not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to update candidate.' });
  }
};

export const deleteCandidate = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const deletedCount = await db('Candidates').where({ candidate_id: id }).del();

    if (deletedCount > 0) {
      res.status(204).send();
    } else {
      res.status(404).json({ error: 'Candidate not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete candidate.' });
  }
};