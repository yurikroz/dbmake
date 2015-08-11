--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

SET search_path = public, pg_catalog;

ALTER TABLE ONLY public.td_customers DROP CONSTRAINT td_customers_pkey;
ALTER TABLE public.td_customers ALTER COLUMN id DROP DEFAULT;
ALTER TABLE public._dbmake_migrations ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE public.td_customers_id_seq;
DROP TABLE public.td_customers;
DROP SEQUENCE public._dbmake_migrations_id_seq;
DROP TABLE public._dbmake_migrations;
DROP EXTENSION plpgsql;
DROP SCHEMA public;
--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

CREATE SCHEMA public;


ALTER SCHEMA public OWNER TO postgres;

--
-- Name: SCHEMA public; Type: COMMENT; Schema: -; Owner: postgres
--

COMMENT ON SCHEMA public IS 'standard public schema';


--
-- Name: plpgsql; Type: EXTENSION; Schema: -; Owner: 
--

CREATE EXTENSION IF NOT EXISTS plpgsql WITH SCHEMA pg_catalog;


--
-- Name: EXTENSION plpgsql; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION plpgsql IS 'PL/pgSQL procedural language';


SET search_path = public, pg_catalog;

SET default_tablespace = '';

SET default_with_oids = false;

--
-- Name: _dbmake_migrations; Type: TABLE; Schema: public; Owner: splanger; Tablespace: 
--

CREATE TABLE _dbmake_migrations (
    id integer NOT NULL,
    version character varying(100) NOT NULL,
    file character varying(100),
    create_date timestamp without time zone DEFAULT now() NOT NULL
);


ALTER TABLE public._dbmake_migrations OWNER TO splanger;

--
-- Name: _dbmake_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: splanger
--

CREATE SEQUENCE _dbmake_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public._dbmake_migrations_id_seq OWNER TO splanger;

--
-- Name: _dbmake_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splanger
--

ALTER SEQUENCE _dbmake_migrations_id_seq OWNED BY _dbmake_migrations.id;


--
-- Name: td_customers; Type: TABLE; Schema: public; Owner: splanger; Tablespace: 
--

CREATE TABLE td_customers (
    id integer NOT NULL,
    first_name character varying(80),
    last_name character varying(45),
    age integer,
    update_date timestamp without time zone DEFAULT now() NOT NULL,
    create_date timestamp without time zone DEFAULT now() NOT NULL,
    email character varying(128) DEFAULT ''::character varying NOT NULL,
    CONSTRAINT td_customers_age_check CHECK ((age > 0))
);


ALTER TABLE public.td_customers OWNER TO splanger;

--
-- Name: td_customers_id_seq; Type: SEQUENCE; Schema: public; Owner: splanger
--

CREATE SEQUENCE td_customers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.td_customers_id_seq OWNER TO splanger;

--
-- Name: td_customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splanger
--

ALTER SEQUENCE td_customers_id_seq OWNED BY td_customers.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: splanger
--

ALTER TABLE ONLY _dbmake_migrations ALTER COLUMN id SET DEFAULT nextval('_dbmake_migrations_id_seq'::regclass);


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: splanger
--

ALTER TABLE ONLY td_customers ALTER COLUMN id SET DEFAULT nextval('td_customers_id_seq'::regclass);


--
-- Name: td_customers_pkey; Type: CONSTRAINT; Schema: public; Owner: splanger; Tablespace: 
--

ALTER TABLE ONLY td_customers
    ADD CONSTRAINT td_customers_pkey PRIMARY KEY (id);


--
-- Name: public; Type: ACL; Schema: -; Owner: postgres
--

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM postgres;
GRANT ALL ON SCHEMA public TO postgres;
GRANT ALL ON SCHEMA public TO PUBLIC;


--
-- PostgreSQL database dump complete
--

