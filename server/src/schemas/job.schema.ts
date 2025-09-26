import { z } from 'zod';

// Schema for creating a new job, matching the "Jobs" table.
export const createJobSchema = z.object({
  body: z.object({
    // department is the only required field.
    department: z.string().min(1, 'Department is required'),

    // All other fields are optional strings.
    shift: z.string().optional(),
    employment_type: z.string().optional(),
    pay_structure: z.string().optional(),
  }),
});

// Infer the TypeScript type for the request body.
export type CreateJobBody = z.infer<typeof createJobSchema.shape.body>;