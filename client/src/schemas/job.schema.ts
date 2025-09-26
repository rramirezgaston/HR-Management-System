import { z } from 'zod';

/**
 * Zod schema for validating the request body when creating a new job.
 * This schema is based directly on the "Jobs" table in the database.
 */
export const createJobSchema = z.object({
  body: z.object({
    
    /**
     * The department for the job. This is the only mandatory field.
     * It must be a string containing at least one character.
     */
    department: z.string().min(1, 'Department is required'),

    /**
     * The shift for the job (e.g., "1st", "2nd"). This field is optional.
     */
    shift: z.string().optional(),

    /**
     * The employment type (e.g., "Full-time", "Part-time"). This field is optional.
     */
    employment_type: z.string().optional(),

    /**
     * The pay structure (e.g., "Hourly", "Salary"). This field is optional.
     */
    pay_structure: z.string().optional(),
  }),
});

/**
 * Infers a TypeScript type from the schema for the request body.
 * This provides type-safety and autocompletion in your controllers.
 */
export type CreateJobBody = z.infer<typeof createJobSchema.shape.body>;