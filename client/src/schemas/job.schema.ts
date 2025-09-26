import { z } from 'zod';

export const createJobSchema = z.object({
  body: z.object({
    department: z.string({
      required_error: 'Department is required',
    }).min(1, 'Department cannot be empty'),

    shift: z.string().optional(),
  }),
});