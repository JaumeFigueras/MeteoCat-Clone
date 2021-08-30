-- database_init.sql
SET timezone='UTC';

DO
$do$
BEGIN
	IF NOT EXISTS (
		SELECT FROM pg_catalog.pg_roles  -- SELECT list can be empty for this
    	WHERE  rolname = 'gisfireuser') THEN

		CREATE ROLE gisfireuser WITH PASSWORD '1234';
		GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO gisfireuser;
   END IF;
END
$do$;

CREATE EXTENSION postgis;

ALTER DATABASE test OWNER TO gisfireuser;
SET SESSION AUTHORIZATION 'gisfireuser';
