import knex from 'knex';
import path from 'path';

// Create a configuration object for our database connection
const dbConfig = {
  client: 'sqlite3', // Specify that we are using the sqlite3 driver
  connection: {
    // We use path.resolve to build a correct path to our database file.
    filename: path.resolve(__dirname, '../data/HR_Hiring_DB.db'),
  },
  // SQLite does not have a default value for fields, so this is a required setting.
  useNullAsDefault: true,
};

// Initialize Knex with our configuration
const db = knex(dbConfig);

// Export the configured db object so we can use it in other files
export default db;