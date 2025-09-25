import { Request, Response } from 'express';
import db from '../database';

// GET metrics for a specific date and department from query parameters
export const getMetrics = async (req: Request, res: Response) => {
  try {
    const { date, department } = req.query;
    if (!date || !department) {
      return res.status(400).json({ error: 'Date and department are required.' });
    }

    // Find the main metric record
    const metric = await db('Daily_Metrics').where({ metric_date: date as string, department: department as string }).first();

    if (!metric) {
      // If no record exists for that day, return a default structure
      return res.json({
        metric_id: null,
        apps_reviewed: 0,
        interviews_scheduled: 0,
        hires_confirmed: 0,
        breakdowns: []
      });
    }

    // If a record was found, find its associated breakdowns
    const breakdowns = await db('Daily_Breakdowns').where({ fk_metric_id: metric.metric_id });
    res.json({ ...metric, breakdowns });
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch daily metrics.' });
  }
};

// CREATE or UPDATE metrics for a specific date and department
export const upsertMetrics = async (req: Request, res: Response) => {
  const { date, department, apps_reviewed, interviews_scheduled, hires_confirmed, breakdowns } = req.body;

  try {
    // Use a transaction to ensure all operations succeed or none do
    await db.transaction(async (trx) => {
      // Check if a metric for this date/dept already exists
      const existingMetric = await trx('Daily_Metrics').where({ metric_date: date, department: department }).first();

      let metric_id;

      if (existingMetric) {
        // --- UPDATE PATH ---
        metric_id = existingMetric.metric_id;
        // Update the main metric counts
        await trx('Daily_Metrics').where({ metric_id }).update({ apps_reviewed, interviews_scheduled, hires_confirmed });
        // Delete the old breakdowns to replace them with the new ones
        await trx('Daily_Breakdowns').where({ fk_metric_id: metric_id }).del();
      } else {
        // --- INSERT PATH ---
        // Insert the new main metric record and get its ID
        const newMetric = await trx('Daily_Metrics').insert({
          metric_date: date,
          department,
          apps_reviewed,
          interviews_scheduled,
          hires_confirmed
        }).returning('metric_id');
        metric_id = newMetric[0].metric_id;
      }

      // If there are any breakdowns to add, insert them
      if (breakdowns && breakdowns.length > 0) {
        const breakdownsToInsert = breakdowns.map((b: any) => ({
          fk_metric_id: metric_id,
          category: b.category,
          reason: b.reason,
          count: b.count,
        }));
        await trx('Daily_Breakdowns').insert(breakdownsToInsert);
      }
    });

    res.status(200).json({ success: true });
  } catch (error) {
    res.status(500).json({ error: 'Failed to save daily metrics.' });
  }
};