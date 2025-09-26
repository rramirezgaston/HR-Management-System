import { Request, Response, NextFunction } from 'express';
// Use 'z' to access Zod's members, including ZodError for type checking.
import { z, ZodObject } from 'zod';

// This function takes a Zod schema and returns Express middleware.
const validate = (schema: ZodObject<any>) => (req: Request, res: Response, next: NextFunction) => {
  try {
    // .parse() validates the request data. It throws an error on failure.
    schema.parse({
      body: req.body,
      query: req.query,
      params: req.params,
    });
    
    // If validation succeeds, pass control to the next handler.
    next();
  } catch (e) {
    // Check if the error is a Zod validation error.
    if (e instanceof z.ZodError) {
      return res.status(400).send(e.issues);
    }
    // Handle other unexpected errors.
    return res.status(500).send({ message: 'Internal Server Error' });
  }
};

export default validate;