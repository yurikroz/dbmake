--
-- PostgreSQL database dump
--

SET statement_timeout = 0;
SET lock_timeout = 0;
SET client_encoding = 'LATIN1';
SET standard_conforming_strings = on;
SET check_function_bodies = false;
SET client_min_messages = warning;

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
-- Name: customers; Type: TABLE; Schema: public; Owner: splanger; Tablespace: 
--

CREATE TABLE customers (
    id integer NOT NULL,
    name character varying(45)
);


ALTER TABLE public.customers OWNER TO splanger;

--
-- Name: customers_id_seq; Type: SEQUENCE; Schema: public; Owner: splanger
--

CREATE SEQUENCE customers_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.customers_id_seq OWNER TO splanger;

--
-- Name: customers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: splanger
--

ALTER SEQUENCE customers_id_seq OWNED BY customers.id;


--
-- Name: id; Type: DEFAULT; Schema: public; Owner: splanger
--

ALTER TABLE ONLY customers ALTER COLUMN id SET DEFAULT nextval('customers_id_seq'::regclass);


--
-- Name: customers_pkey; Type: CONSTRAINT; Schema: public; Owner: splanger; Tablespace: 
--

ALTER TABLE ONLY customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

