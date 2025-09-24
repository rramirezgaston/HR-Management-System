import { Request, Response } from 'express';
import db from '../database';

export const getAllHiringClasses = async (req: Request, res: Response) => {
  try {
    const hiringClasses = await db('Hiring_Classes').select('*');
    res.json(hiringClasses);
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch hiring classes.' });
  }
};

export const createHiringClass = async (req: Request, res: Response) => {
  try {
    const newHiringClass = await db('Hiring_Classes').insert(req.body).returning('*');
    res.status(201).json(newHiringClass[0]);
  } catch (error) {
    res.status(500).json({ error: 'Failed to create hiring class.' });
  }
};

export const updateHiringClass = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const updatedHiringClass = await db('Hiring_Classes')
      .where({ class_id: id })
      .update(req.body)
      .returning('*');

    if (updatedHiringClass.length > 0) {
      res.json(updatedHiringClass[0]);
    } else {
      res.status(404).json({ error: 'Hiring class not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to update hiring class.' });
  }
};

export const deleteHiringClass = async (req: Request, res: Response) => {
  try {
    const { id } = req.params;
    const deletedCount = await db('Hiring_Classes').where({ class_id: id }).del();

    if (deletedCount > 0) {
      res.status(204).send();
    } else {
      res.status(404).json({ error: 'Hiring class not found.' });
    }
  } catch (error) {
    res.status(500).json({ error: 'Failed to delete hiring class.' });
  }
};