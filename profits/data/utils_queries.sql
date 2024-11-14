/* 
Postgres Portfolio DB uswful scripts
*/

-- Shows public tables defined in the database
SELECT tablename FROM pg_tables WHERE schemaname = 'public';