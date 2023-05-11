-- settings.sql
CREATE DATABASE fitness_app;
CREATE USER fitness WITH PASSWORD 'fitness';
GRANT ALL PRIVILEGES ON DATABASE fitness_app TO fitness;