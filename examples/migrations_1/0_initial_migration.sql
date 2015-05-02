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

ALTER TABLE ONLY td_customers ALTER COLUMN id SET DEFAULT nextval('td_customers_id_seq'::regclass);


--
-- Name: td_customers_pkey; Type: CONSTRAINT; Schema: public; Owner: splanger; Tablespace: 
--

ALTER TABLE ONLY td_customers
    ADD CONSTRAINT td_customers_pkey PRIMARY KEY (id);


--
-- PostgreSQL database dump complete
--

