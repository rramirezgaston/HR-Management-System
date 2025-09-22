import knex from 'knex';

// Configuration for our new PostgreSQL server
const dbConfig = {
  client: 'pg', // Specify the 'pg' (PostgreSQL) driver
  connection: {
    host: 'db', // The service name we defined in docker-compose.yml
    user: 'vscode', // The username we defined
    password: 'password', // The password we defined
    database: 'hr_db', // The database name we defined
  },
};

const db = knex(dbConfig);

export default db;