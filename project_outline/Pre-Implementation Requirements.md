# KiTraderBot Pre-Implementation Analysis

## 1. Database Information
### PostgreSQL Version & Status
```
psql (PostgreSQL) 16.4 (Ubuntu 16.4-1build1)

● postgresql.service - PostgreSQL RDBMS
     Loaded: loaded (/usr/lib/systemd/system/postgresql.service; enabled; preset: enabled)
     Active: active (exited) since Tue 2024-11-26 17:53:57 UTC; 1 day 6h ago
 Invocation: 9d151ae5191a489ba15f9dcc8e173a87
   Main PID: 25818 (code=exited, status=0/SUCCESS)
   Mem peak: 1.5M
        CPU: 7ms

Nov 26 17:53:57 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Starting postgresql.service - PostgreSQL RDBMS...  
Nov 26 17:53:57 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Finished postgresql.service - PostgreSQL RDBMS.


[Output will go here]
```

### Database Schema
```sql
[--
-- PostgreSQL database dump
--

-- Dumped from database version 16.4 (Ubuntu 16.4-1build1)
-- Dumped by pg_dump version 16.4 (Ubuntu 16.4-1build1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: trades; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.trades (
    trade_id integer NOT NULL,
    user_id integer,
    symbol character varying(20) NOT NULL,
    entry_price numeric(20,8) NOT NULL,
    exit_price numeric(20,8),
    position_size numeric(20,8) NOT NULL,
    trade_type character varying(10) NOT NULL,
    trade_status character varying(20) DEFAULT 'open'::character varying,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    closed_at timestamp without time zone,
    pnl numeric(20,8)
);


ALTER TABLE public.trades OWNER TO postgres;

--
-- Name: trades_trade_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.trades_trade_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trades_trade_id_seq OWNER TO postgres;

--
-- Name: trades_trade_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.trades_trade_id_seq OWNED BY public.trades.trade_id;


--
-- Name: user_settings; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_settings (
    user_id integer NOT NULL,
    notification_preferences jsonb DEFAULT '{}'::jsonb,
    risk_settings jsonb DEFAULT '{}'::jsonb,
    ui_preferences jsonb DEFAULT '{}'::jsonb,
    created_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.user_settings OWNER TO postgres;

--
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id integer NOT NULL,
    telegram_id bigint NOT NULL,
    username character varying(255),
    role character varying(50) DEFAULT 'basic'::character varying,
    registration_date timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    last_active timestamp without time zone,
    account_status character varying(50) DEFAULT 'active'::character varying
);


ALTER TABLE public.users OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.users_user_id_seq OWNER TO postgres;

--
-- Name: users_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;


--
-- Name: trades trade_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades ALTER COLUMN trade_id SET DEFAULT nextval('public.trades_trade_id_seq'::regclass);    


--
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);        


--
-- Name: trades trades_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT trades_pkey PRIMARY KEY (trade_id);


--
-- Name: user_settings user_settings_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT user_settings_pkey PRIMARY KEY (user_id);


--
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);


--
-- Name: users users_telegram_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_telegram_id_key UNIQUE (telegram_id);


--
-- Name: trades fk_trades_users; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.trades
    ADD CONSTRAINT fk_trades_users FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- Name: user_settings user_settings_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_settings
    ADD CONSTRAINT user_settings_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- PostgreSQL database dump complete
--
]
```

### Table Details & Relationships
```
[                                              List of relations
 Schema |        Name         |   Type   |  Owner   | Persistence | Access method |    Size    | Description
--------+---------------------+----------+----------+-------------+---------------+------------+-------------        
 public | trades              | table    | postgres | permanent   | heap          | 0 bytes    |
 public | trades_trade_id_seq | sequence | postgres | permanent   |               | 8192 bytes |
 public | user_settings       | table    | postgres | permanent   | heap          | 8192 bytes |
 public | users               | table    | postgres | permanent   | heap          | 0 bytes    |
 public | users_user_id_seq   | sequence | postgres | permanent   |               | 8192 bytes |
(5 rows)


                List of installed extensions
  Name   | Version |   Schema   |         Description
---------+---------+------------+------------------------------
 plpgsql | 1.0     | pg_catalog | PL/pgSQL procedural language
(1 row)

                                                                       Table "public.users"
      Column       |            Type             | Collation | Nullable |                Default                 | Storage  | Compression | Stats target | Description
-------------------+-----------------------------+-----------+----------+----------------------------------------+----------+-------------+--------------+-------------
 user_id           | integer                     |           | not null | nextval('users_user_id_seq'::regclass) | plain    |             |              |
 telegram_id       | bigint                      |           | not null |                                        | plain    |             |              |
 username          | character varying(255)      |           |          |                                        | extended |             |              |
 role              | character varying(50)       |           |          | 'basic'::character varying             | extended |             |              |
 registration_date | timestamp without time zone |           |          | CURRENT_TIMESTAMP                      | plain    |             |              |
 last_active       | timestamp without time zone |           |          |                                        | plain    |             |              |
 account_status    | character varying(50)       |           |          | 'active'::character varying            | extended |             |              |
Indexes:
    "users_pkey" PRIMARY KEY, btree (user_id)
    "users_telegram_id_key" UNIQUE CONSTRAINT, btree (telegram_id)
Referenced by:
    TABLE "trades" CONSTRAINT "fk_trades_users" FOREIGN KEY (user_id) REFERENCES users(user_id)
    TABLE "user_settings" CONSTRAINT "user_settings_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(user_id)    
Access method: heap

(END)



                                                              Table "public.user_settings"
          Column          |            Type             | Collation | Nullable |      Default      | Storage  | Compression | Stats target | Description
--------------------------+-----------------------------+-----------+----------+-------------------+----------+-------------+--------------+-------------
 user_id                  | integer                     |           | not null |                   | plain    |      
       |              |
 notification_preferences | jsonb                       |           |          | '{}'::jsonb       | extended |      
       |              |
 risk_settings            | jsonb                       |           |          | '{}'::jsonb       | extended |      
       |              |
 ui_preferences           | jsonb                       |           |          | '{}'::jsonb       | extended |      
       |              |
 created_at               | timestamp without time zone |           |          | CURRENT_TIMESTAMP | plain    |      
       |              |
 updated_at               | timestamp without time zone |           |          | CURRENT_TIMESTAMP | plain    |      
       |              |
Indexes:
    "user_settings_pkey" PRIMARY KEY, btree (user_id)
Foreign-key constraints:
    "user_settings_user_id_fkey" FOREIGN KEY (user_id) REFERENCES users(user_id)
Access method: heap

(END)
 

                                                                        Table "public.trades"
    Column     |            Type             | Collation | Nullable |                 Default                  | Storage  | Compression | Stats target | Description
---------------+-----------------------------+-----------+----------+------------------------------------------+----------+-------------+--------------+-------------
 trade_id      | integer                     |           | not null | nextval('trades_trade_id_seq'::regclass) | plain    |             |              |
 user_id       | integer                     |           |          |                                          | plain    |             |              |
 symbol        | character varying(20)       |           | not null |                                          | extended |             |              |
 entry_price   | numeric(20,8)               |           | not null |                                          | main     |             |              |
 exit_price    | numeric(20,8)               |           |          |                                          | main     |             |              |
 position_size | numeric(20,8)               |           | not null |                                          | main     |             |              |
 trade_type    | character varying(10)       |           | not null |                                          | extended |             |              |
 trade_status  | character varying(20)       |           |          | 'open'::character varying                | extended |             |              |
 created_at    | timestamp without time zone |           |          | CURRENT_TIMESTAMP                        | plai
n    |             |              | 
 closed_at     | timestamp without time zone |           |          |                                          | plain    |             |              |
 pnl           | numeric(20,8)               |           |          |                                          | main     |             |              |
Indexes:
    "trades_pkey" PRIMARY KEY, btree (trade_id)
Foreign-key constraints:
    "fk_trades_users" FOREIGN KEY (user_id) REFERENCES users(user_id)
Access method: heap

(END)
]
```

### Indexes & Constraints
```
[               List of relations
 Schema |         Name          | Type  |  Owner   |     Table
--------+-----------------------+-------+----------+---------------
 public | trades_pkey           | index | postgres | trades
 public | user_settings_pkey    | index | postgres | user_settings
 public | users_pkey            | index | postgres | users
 public | users_telegram_id_key | index | postgres | users
(4 rows)
]
```

## 2. Project Structure
### Directory Tree
```
[    │           │   │   │   │   │   ├── tags.py
    │           │   │   │   │   │   ├── utils.py
    │           │   │   │   │   │   └── version.py
    │           │   │   │   │   └── vendor.txt
    │           │   │   │   └── wheelfile.py
    │           │   │   ├── wheel-0.43.0.dist-info
    │           │   │   │   ├── INSTALLER
    │           │   │   │   ├── LICENSE.txt
    │           │   │   │   ├── METADATA
    │           │   │   │   ├── RECORD
    │           │   │   │   ├── REQUESTED
    │           │   │   │   ├── WHEEL
    │           │   │   │   └── entry_points.txt
    │           │   │   ├── zipp
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   └── glob.cpython-312.pyc
    │           │   │   │   ├── compat
    │           │   │   │   │   ├── __init__.py
    │           │   │   │   │   ├── __pycache__
    │           │   │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   │   └── py310.cpython-312.pyc
    │           │   │   │   │   └── py310.py
    │           │   │   │   └── glob.py
    │           │   │   └── zipp-3.19.2.dist-info
    │           │   │       ├── INSTALLER
    │           │   │       ├── LICENSE
    │           │   │       ├── METADATA
    │           │   │       ├── RECORD
    │           │   │       ├── REQUESTED
    │           │   │       ├── WHEEL
    │           │   │       └── top_level.txt
    │           │   ├── archive_util.py
    │           │   ├── build_meta.py
    │           │   ├── cli-32.exe
    │           │   ├── cli-64.exe
    │           │   ├── cli-arm64.exe
    │           │   ├── cli.exe
    │           │   ├── command
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── _requirestxt.cpython-312.pyc
    │           │   │   │   ├── alias.cpython-312.pyc
    │           │   │   │   ├── bdist_egg.cpython-312.pyc
    │           │   │   │   ├── bdist_rpm.cpython-312.pyc
    │           │   │   │   ├── bdist_wheel.cpython-312.pyc
    │           │   │   │   ├── build.cpython-312.pyc
    │           │   │   │   ├── build_clib.cpython-312.pyc
    │           │   │   │   ├── build_ext.cpython-312.pyc
    │           │   │   │   ├── build_py.cpython-312.pyc
    │           │   │   │   ├── develop.cpython-312.pyc
    │           │   │   │   ├── dist_info.cpython-312.pyc
    │           │   │   │   ├── easy_install.cpython-312.pyc
    │           │   │   │   ├── editable_wheel.cpython-312.pyc
    │           │   │   │   ├── egg_info.cpython-312.pyc
    │           │   │   │   ├── install.cpython-312.pyc
    │           │   │   │   ├── install_egg_info.cpython-312.pyc
    │           │   │   │   ├── install_lib.cpython-312.pyc
    │           │   │   │   ├── install_scripts.cpython-312.pyc
    │           │   │   │   ├── rotate.cpython-312.pyc
    │           │   │   │   ├── saveopts.cpython-312.pyc
    │           │   │   │   ├── sdist.cpython-312.pyc
    │           │   │   │   ├── setopt.cpython-312.pyc
    │           │   │   │   └── test.cpython-312.pyc
    │           │   │   ├── _requirestxt.py
    │           │   │   ├── alias.py
    │           │   │   ├── bdist_egg.py
    │           │   │   ├── bdist_rpm.py
    │           │   │   ├── bdist_wheel.py
    │           │   │   ├── build.py
    │           │   │   ├── build_clib.py
    │           │   │   ├── build_ext.py
    │           │   │   ├── build_py.py
    │           │   │   ├── develop.py
    │           │   │   ├── dist_info.py
    │           │   │   ├── easy_install.py
    │           │   │   ├── editable_wheel.py
    │           │   │   ├── egg_info.py
    │           │   │   ├── install.py
    │           │   │   ├── install_egg_info.py
    │           │   │   ├── install_lib.py
    │           │   │   ├── install_scripts.py
    │           │   │   ├── launcher manifest.xml
    │           │   │   ├── rotate.py
    │           │   │   ├── saveopts.py
    │           │   │   ├── sdist.py
    │           │   │   ├── setopt.py
    │           │   │   └── test.py
    │           │   ├── compat
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── py310.cpython-312.pyc
    │           │   │   │   ├── py311.cpython-312.pyc
    │           │   │   │   ├── py312.cpython-312.pyc
    │           │   │   │   └── py39.cpython-312.pyc
    │           │   │   ├── py310.py
    │           │   │   ├── py311.py
    │           │   │   ├── py312.py
    │           │   │   └── py39.py
    │           │   ├── config
    │           │   │   ├── NOTICE
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── _apply_pyprojecttoml.cpython-312.pyc
    │           │   │   │   ├── expand.cpython-312.pyc
    │           │   │   │   ├── pyprojecttoml.cpython-312.pyc
    │           │   │   │   └── setupcfg.cpython-312.pyc
    │           │   │   ├── _apply_pyprojecttoml.py
    │           │   │   ├── _validate_pyproject
    │           │   │   │   ├── NOTICE
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   ├── error_reporting.cpython-312.pyc
    │           │   │   │   │   ├── extra_validations.cpython-312.pyc
    │           │   │   │   │   ├── fastjsonschema_exceptions.cpython-312.pyc
    │           │   │   │   │   ├── fastjsonschema_validations.cpython-312.pyc
    │           │   │   │   │   └── formats.cpython-312.pyc
    │           │   │   │   ├── error_reporting.py
    │           │   │   │   ├── extra_validations.py
    │           │   │   │   ├── fastjsonschema_exceptions.py
    │           │   │   │   ├── fastjsonschema_validations.py
    │           │   │   │   └── formats.py
    │           │   │   ├── distutils.schema.json
    │           │   │   ├── expand.py
    │           │   │   ├── pyprojecttoml.py
    │           │   │   ├── setupcfg.py
    │           │   │   └── setuptools.schema.json
    │           │   ├── depends.py
    │           │   ├── discovery.py
    │           │   ├── dist.py
    │           │   ├── errors.py
    │           │   ├── extension.py
    │           │   ├── glob.py
    │           │   ├── gui-32.exe
    │           │   ├── gui-64.exe
    │           │   ├── gui-arm64.exe
    │           │   ├── gui.exe
    │           │   ├── installer.py
    │           │   ├── launch.py
    │           │   ├── logging.py
    │           │   ├── modified.py
    │           │   ├── monkey.py
    │           │   ├── msvc.py
    │           │   ├── namespaces.py
    │           │   ├── package_index.py
    │           │   ├── sandbox.py
    │           │   ├── script (dev).tmpl
    │           │   ├── script.tmpl
    │           │   ├── tests
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── contexts.cpython-312.pyc
    │           │   │   │   ├── environment.cpython-312.pyc
    │           │   │   │   ├── fixtures.cpython-312.pyc
    │           │   │   │   ├── mod_with_constant.cpython-312.pyc
    │           │   │   │   ├── namespaces.cpython-312.pyc
    │           │   │   │   ├── script-with-bom.cpython-312.pyc
    │           │   │   │   ├── server.cpython-312.pyc
    │           │   │   │   ├── test_archive_util.cpython-312.pyc
    │           │   │   │   ├── test_bdist_deprecations.cpython-312.pyc
    │           │   │   │   ├── test_bdist_egg.cpython-312.pyc
    │           │   │   │   ├── test_bdist_wheel.cpython-312.pyc
    │           │   │   │   ├── test_build.cpython-312.pyc
    │           │   │   │   ├── test_build_clib.cpython-312.pyc
    │           │   │   │   ├── test_build_ext.cpython-312.pyc
    │           │   │   │   ├── test_build_meta.cpython-312.pyc
    │           │   │   │   ├── test_build_py.cpython-312.pyc
    │           │   │   │   ├── test_config_discovery.cpython-312.pyc
    │           │   │   │   ├── test_core_metadata.cpython-312.pyc
    │           │   │   │   ├── test_depends.cpython-312.pyc
    │           │   │   │   ├── test_develop.cpython-312.pyc
    │           │   │   │   ├── test_dist.cpython-312.pyc
    │           │   │   │   ├── test_dist_info.cpython-312.pyc
    │           │   │   │   ├── test_distutils_adoption.cpython-312.pyc
    │           │   │   │   ├── test_easy_install.cpython-312.pyc
    │           │   │   │   ├── test_editable_install.cpython-312.pyc
    │           │   │   │   ├── test_egg_info.cpython-312.pyc
    │           │   │   │   ├── test_extern.cpython-312.pyc
    │           │   │   │   ├── test_find_packages.cpython-312.pyc
    │           │   │   │   ├── test_find_py_modules.cpython-312.pyc
    │           │   │   │   ├── test_glob.cpython-312.pyc
    │           │   │   │   ├── test_install_scripts.cpython-312.pyc
    │           │   │   │   ├── test_logging.cpython-312.pyc
    │           │   │   │   ├── test_manifest.cpython-312.pyc
    │           │   │   │   ├── test_namespaces.cpython-312.pyc
    │           │   │   │   ├── test_packageindex.cpython-312.pyc
    │           │   │   │   ├── test_sandbox.cpython-312.pyc
    │           │   │   │   ├── test_sdist.cpython-312.pyc
    │           │   │   │   ├── test_setopt.cpython-312.pyc
    │           │   │   │   ├── test_setuptools.cpython-312.pyc
    │           │   │   │   ├── test_shutil_wrapper.cpython-312.pyc
    │           │   │   │   ├── test_unicode_utils.cpython-312.pyc
    │           │   │   │   ├── test_virtualenv.cpython-312.pyc
    │           │   │   │   ├── test_warnings.cpython-312.pyc
    │           │   │   │   ├── test_wheel.cpython-312.pyc
    │           │   │   │   ├── test_windows_wrappers.cpython-312.pyc
    │           │   │   │   ├── text.cpython-312.pyc
    │           │   │   │   └── textwrap.cpython-312.pyc
    │           │   │   ├── compat
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   └── py39.cpython-312.pyc
    │           │   │   │   └── py39.py
    │           │   │   ├── config
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   ├── test_apply_pyprojecttoml.cpython-312.pyc
    │           │   │   │   │   ├── test_expand.cpython-312.pyc
    │           │   │   │   │   ├── test_pyprojecttoml.cpython-312.pyc
    │           │   │   │   │   ├── test_pyprojecttoml_dynamic_deps.cpython-312.pyc
    │           │   │   │   │   └── test_setupcfg.cpython-312.pyc
    │           │   │   │   ├── downloads
    │           │   │   │   │   ├── __init__.py
    │           │   │   │   │   ├── __pycache__
    │           │   │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   │   └── preload.cpython-312.pyc
    │           │   │   │   │   └── preload.py
    │           │   │   │   ├── setupcfg_examples.txt
    │           │   │   │   ├── test_apply_pyprojecttoml.py
    │           │   │   │   ├── test_expand.py
    │           │   │   │   ├── test_pyprojecttoml.py
    │           │   │   │   ├── test_pyprojecttoml_dynamic_deps.py
    │           │   │   │   └── test_setupcfg.py
    │           │   │   ├── contexts.py
    │           │   │   ├── environment.py
    │           │   │   ├── fixtures.py
    │           │   │   ├── indexes
    │           │   │   │   └── test_links_priority
    │           │   │   │       ├── external.html
    │           │   │   │       └── simple
    │           │   │   │           └── foobar
    │           │   │   │               └── index.html
    │           │   │   ├── integration
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   ├── helpers.cpython-312.pyc
    │           │   │   │   │   └── test_pip_install_sdist.cpython-312.pyc
    │           │   │   │   ├── helpers.py
    │           │   │   │   └── test_pip_install_sdist.py
    │           │   │   ├── mod_with_constant.py
    │           │   │   ├── namespaces.py
    │           │   │   ├── script-with-bom.py
    │           │   │   ├── server.py
    │           │   │   ├── test_archive_util.py
    │           │   │   ├── test_bdist_deprecations.py
    │           │   │   ├── test_bdist_egg.py
    │           │   │   ├── test_bdist_wheel.py
    │           │   │   ├── test_build.py
    │           │   │   ├── test_build_clib.py
    │           │   │   ├── test_build_ext.py
    │           │   │   ├── test_build_meta.py
    │           │   │   ├── test_build_py.py
    │           │   │   ├── test_config_discovery.py
    │           │   │   ├── test_core_metadata.py
    │           │   │   ├── test_depends.py
    │           │   │   ├── test_develop.py
    │           │   │   ├── test_dist.py
    │           │   │   ├── test_dist_info.py
    │           │   │   ├── test_distutils_adoption.py
    │           │   │   ├── test_easy_install.py
    │           │   │   ├── test_editable_install.py
    │           │   │   ├── test_egg_info.py
    │           │   │   ├── test_extern.py
    │           │   │   ├── test_find_packages.py
    │           │   │   ├── test_find_py_modules.py
    │           │   │   ├── test_glob.py
    │           │   │   ├── test_install_scripts.py
    │           │   │   ├── test_logging.py
    │           │   │   ├── test_manifest.py
    │           │   │   ├── test_namespaces.py
    │           │   │   ├── test_packageindex.py
    │           │   │   ├── test_sandbox.py
    │           │   │   ├── test_sdist.py
    │           │   │   ├── test_setopt.py
    │           │   │   ├── test_setuptools.py
    │           │   │   ├── test_shutil_wrapper.py
    │           │   │   ├── test_unicode_utils.py
    │           │   │   ├── test_virtualenv.py
    │           │   │   ├── test_warnings.py
    │           │   │   ├── test_wheel.py
    │           │   │   ├── test_windows_wrappers.py
    │           │   │   ├── text.py
    │           │   │   └── textwrap.py
    │           │   ├── unicode_utils.py
    │           │   ├── version.py
    │           │   ├── warnings.py
    │           │   ├── wheel.py
    │           │   └── windows_support.py
    │           ├── setuptools-75.6.0.dist-info
    │           │   ├── INSTALLER
    │           │   ├── LICENSE
    │           │   ├── METADATA
    │           │   ├── RECORD
    │           │   ├── WHEEL
    │           │   ├── entry_points.txt
    │           │   └── top_level.txt
    │           ├── six-1.16.0.dist-info
    │           │   ├── INSTALLER
    │           │   ├── LICENSE
    │           │   ├── METADATA
    │           │   ├── RECORD
    │           │   ├── REQUESTED
    │           │   ├── WHEEL
    │           │   └── top_level.txt
    │           ├── six.py
    │           ├── telegram
    │           │   ├── __init__.py
    │           │   ├── __main__.py
    │           │   ├── __pycache__
    │           │   │   ├── __init__.cpython-312.pyc
    │           │   │   ├── __main__.cpython-312.pyc
    │           │   │   ├── base.cpython-312.pyc
    │           │   │   ├── bot.cpython-312.pyc
    │           │   │   ├── botcommand.cpython-312.pyc
    │           │   │   ├── botcommandscope.cpython-312.pyc
    │           │   │   ├── callbackquery.cpython-312.pyc
    │           │   │   ├── chat.cpython-312.pyc
    │           │   │   ├── chataction.cpython-312.pyc
    │           │   │   ├── chatinvitelink.cpython-312.pyc
    │           │   │   ├── chatlocation.cpython-312.pyc
    │           │   │   ├── chatmember.cpython-312.pyc
    │           │   │   ├── chatmemberupdated.cpython-312.pyc
    │           │   │   ├── chatpermissions.cpython-312.pyc
    │           │   │   ├── choseninlineresult.cpython-312.pyc
    │           │   │   ├── constants.cpython-312.pyc
    │           │   │   ├── dice.cpython-312.pyc
    │           │   │   ├── error.cpython-312.pyc
    │           │   │   ├── forcereply.cpython-312.pyc
    │           │   │   ├── keyboardbutton.cpython-312.pyc
    │           │   │   ├── keyboardbuttonpolltype.cpython-312.pyc
    │           │   │   ├── loginurl.cpython-312.pyc
    │           │   │   ├── message.cpython-312.pyc
    │           │   │   ├── messageautodeletetimerchanged.cpython-312.pyc
    │           │   │   ├── messageentity.cpython-312.pyc
    │           │   │   ├── messageid.cpython-312.pyc
    │           │   │   ├── parsemode.cpython-312.pyc
    │           │   │   ├── poll.cpython-312.pyc
    │           │   │   ├── proximityalerttriggered.cpython-312.pyc
    │           │   │   ├── replykeyboardmarkup.cpython-312.pyc
    │           │   │   ├── replykeyboardremove.cpython-312.pyc
    │           │   │   ├── replymarkup.cpython-312.pyc
    │           │   │   ├── update.cpython-312.pyc
    │           │   │   ├── user.cpython-312.pyc
    │           │   │   ├── userprofilephotos.cpython-312.pyc
    │           │   │   ├── version.cpython-312.pyc
    │           │   │   ├── voicechat.cpython-312.pyc
    │           │   │   └── webhookinfo.cpython-312.pyc
    │           │   ├── base.py
    │           │   ├── bot.py
    │           │   ├── botcommand.py
    │           │   ├── botcommandscope.py
    │           │   ├── callbackquery.py
    │           │   ├── chat.py
    │           │   ├── chataction.py
    │           │   ├── chatinvitelink.py
    │           │   ├── chatlocation.py
    │           │   ├── chatmember.py
    │           │   ├── chatmemberupdated.py
    │           │   ├── chatpermissions.py
    │           │   ├── choseninlineresult.py
    │           │   ├── constants.py
    │           │   ├── dice.py
    │           │   ├── error.py
    │           │   ├── ext
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── basepersistence.cpython-312.pyc
    │           │   │   │   ├── callbackcontext.cpython-312.pyc
    │           │   │   │   ├── callbackdatacache.cpython-312.pyc
    │           │   │   │   ├── callbackqueryhandler.cpython-312.pyc
    │           │   │   │   ├── chatmemberhandler.cpython-312.pyc
    │           │   │   │   ├── choseninlineresulthandler.cpython-312.pyc
    │           │   │   │   ├── commandhandler.cpython-312.pyc
    │           │   │   │   ├── contexttypes.cpython-312.pyc
    │           │   │   │   ├── conversationhandler.cpython-312.pyc
    │           │   │   │   ├── defaults.cpython-312.pyc
    │           │   │   │   ├── dictpersistence.cpython-312.pyc
    │           │   │   │   ├── dispatcher.cpython-312.pyc
    │           │   │   │   ├── extbot.cpython-312.pyc
    │           │   │   │   ├── filters.cpython-312.pyc
    │           │   │   │   ├── handler.cpython-312.pyc
    │           │   │   │   ├── inlinequeryhandler.cpython-312.pyc
    │           │   │   │   ├── jobqueue.cpython-312.pyc
    │           │   │   │   ├── messagehandler.cpython-312.pyc
    │           │   │   │   ├── messagequeue.cpython-312.pyc
    │           │   │   │   ├── picklepersistence.cpython-312.pyc
    │           │   │   │   ├── pollanswerhandler.cpython-312.pyc
    │           │   │   │   ├── pollhandler.cpython-312.pyc
    │           │   │   │   ├── precheckoutqueryhandler.cpython-312.pyc
    │           │   │   │   ├── regexhandler.cpython-312.pyc
    │           │   │   │   ├── shippingqueryhandler.cpython-312.pyc
    │           │   │   │   ├── stringcommandhandler.cpython-312.pyc
    │           │   │   │   ├── stringregexhandler.cpython-312.pyc
    │           │   │   │   ├── typehandler.cpython-312.pyc
    │           │   │   │   └── updater.cpython-312.pyc
    │           │   │   ├── basepersistence.py
    │           │   │   ├── callbackcontext.py
    │           │   │   ├── callbackdatacache.py
    │           │   │   ├── callbackqueryhandler.py
    │           │   │   ├── chatmemberhandler.py
    │           │   │   ├── choseninlineresulthandler.py
    │           │   │   ├── commandhandler.py
    │           │   │   ├── contexttypes.py
    │           │   │   ├── conversationhandler.py
    │           │   │   ├── defaults.py
    │           │   │   ├── dictpersistence.py
    │           │   │   ├── dispatcher.py
    │           │   │   ├── extbot.py
    │           │   │   ├── filters.py
    │           │   │   ├── handler.py
    │           │   │   ├── inlinequeryhandler.py
    │           │   │   ├── jobqueue.py
    │           │   │   ├── messagehandler.py
    │           │   │   ├── messagequeue.py
    │           │   │   ├── picklepersistence.py
    │           │   │   ├── pollanswerhandler.py
    │           │   │   ├── pollhandler.py
    │           │   │   ├── precheckoutqueryhandler.py
    │           │   │   ├── regexhandler.py
    │           │   │   ├── shippingqueryhandler.py
    │           │   │   ├── stringcommandhandler.py
    │           │   │   ├── stringregexhandler.py
    │           │   │   ├── typehandler.py
    │           │   │   ├── updater.py
    │           │   │   └── utils
    │           │   │       ├── __init__.py
    │           │   │       ├── __pycache__
    │           │   │       │   ├── __init__.cpython-312.pyc
    │           │   │       │   ├── promise.cpython-312.pyc
    │           │   │       │   ├── types.cpython-312.pyc
    │           │   │       │   └── webhookhandler.cpython-312.pyc
    │           │   │       ├── promise.py
    │           │   │       ├── types.py
    │           │   │       └── webhookhandler.py
    │           │   ├── files
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── animation.cpython-312.pyc
    │           │   │   │   ├── audio.cpython-312.pyc
    │           │   │   │   ├── chatphoto.cpython-312.pyc
    │           │   │   │   ├── contact.cpython-312.pyc
    │           │   │   │   ├── document.cpython-312.pyc
    │           │   │   │   ├── file.cpython-312.pyc
    │           │   │   │   ├── inputfile.cpython-312.pyc
    │           │   │   │   ├── inputmedia.cpython-312.pyc
    │           │   │   │   ├── location.cpython-312.pyc
    │           │   │   │   ├── photosize.cpython-312.pyc
    │           │   │   │   ├── sticker.cpython-312.pyc
    │           │   │   │   ├── venue.cpython-312.pyc
    │           │   │   │   ├── video.cpython-312.pyc
    │           │   │   │   ├── videonote.cpython-312.pyc
    │           │   │   │   └── voice.cpython-312.pyc
    │           │   │   ├── animation.py
    │           │   │   ├── audio.py
    │           │   │   ├── chatphoto.py
    │           │   │   ├── contact.py
    │           │   │   ├── document.py
    │           │   │   ├── file.py
    │           │   │   ├── inputfile.py
    │           │   │   ├── inputmedia.py
    │           │   │   ├── location.py
    │           │   │   ├── photosize.py
    │           │   │   ├── sticker.py
    │           │   │   ├── venue.py
    │           │   │   ├── video.py
    │           │   │   ├── videonote.py
    │           │   │   └── voice.py
    │           │   ├── forcereply.py
    │           │   ├── games
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── callbackgame.cpython-312.pyc
    │           │   │   │   ├── game.cpython-312.pyc
    │           │   │   │   └── gamehighscore.cpython-312.pyc
    │           │   │   ├── callbackgame.py
    │           │   │   ├── game.py
    │           │   │   └── gamehighscore.py
    │           │   ├── inline
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── inlinekeyboardbutton.cpython-312.pyc
    │           │   │   │   ├── inlinekeyboardmarkup.cpython-312.pyc
    │           │   │   │   ├── inlinequery.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresult.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultarticle.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultaudio.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedaudio.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcacheddocument.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedgif.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedmpeg4gif.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedphoto.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedsticker.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedvideo.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcachedvoice.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultcontact.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultdocument.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultgame.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultgif.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultlocation.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultmpeg4gif.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultphoto.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultvenue.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultvideo.cpython-312.pyc
    │           │   │   │   ├── inlinequeryresultvoice.cpython-312.pyc
    │           │   │   │   ├── inputcontactmessagecontent.cpython-312.pyc
    │           │   │   │   ├── inputinvoicemessagecontent.cpython-312.pyc
    │           │   │   │   ├── inputlocationmessagecontent.cpython-312.pyc
    │           │   │   │   ├── inputmessagecontent.cpython-312.pyc
    │           │   │   │   ├── inputtextmessagecontent.cpython-312.pyc
    │           │   │   │   └── inputvenuemessagecontent.cpython-312.pyc
    │           │   │   ├── inlinekeyboardbutton.py
    │           │   │   ├── inlinekeyboardmarkup.py
    │           │   │   ├── inlinequery.py
    │           │   │   ├── inlinequeryresult.py
    │           │   │   ├── inlinequeryresultarticle.py
    │           │   │   ├── inlinequeryresultaudio.py
    │           │   │   ├── inlinequeryresultcachedaudio.py
    │           │   │   ├── inlinequeryresultcacheddocument.py
    │           │   │   ├── inlinequeryresultcachedgif.py
    │           │   │   ├── inlinequeryresultcachedmpeg4gif.py
    │           │   │   ├── inlinequeryresultcachedphoto.py
    │           │   │   ├── inlinequeryresultcachedsticker.py
    │           │   │   ├── inlinequeryresultcachedvideo.py
    │           │   │   ├── inlinequeryresultcachedvoice.py
    │           │   │   ├── inlinequeryresultcontact.py
    │           │   │   ├── inlinequeryresultdocument.py
    │           │   │   ├── inlinequeryresultgame.py
    │           │   │   ├── inlinequeryresultgif.py
    │           │   │   ├── inlinequeryresultlocation.py
    │           │   │   ├── inlinequeryresultmpeg4gif.py
    │           │   │   ├── inlinequeryresultphoto.py
    │           │   │   ├── inlinequeryresultvenue.py
    │           │   │   ├── inlinequeryresultvideo.py
    │           │   │   ├── inlinequeryresultvoice.py
    │           │   │   ├── inputcontactmessagecontent.py
    │           │   │   ├── inputinvoicemessagecontent.py
    │           │   │   ├── inputlocationmessagecontent.py
    │           │   │   ├── inputmessagecontent.py
    │           │   │   ├── inputtextmessagecontent.py
    │           │   │   └── inputvenuemessagecontent.py
    │           │   ├── keyboardbutton.py
    │           │   ├── keyboardbuttonpolltype.py
    │           │   ├── loginurl.py
    │           │   ├── message.py
    │           │   ├── messageautodeletetimerchanged.py
    │           │   ├── messageentity.py
    │           │   ├── messageid.py
    │           │   ├── parsemode.py
    │           │   ├── passport
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── credentials.cpython-312.pyc
    │           │   │   │   ├── data.cpython-312.pyc
    │           │   │   │   ├── encryptedpassportelement.cpython-312.pyc
    │           │   │   │   ├── passportdata.cpython-312.pyc
    │           │   │   │   ├── passportelementerrors.cpython-312.pyc
    │           │   │   │   └── passportfile.cpython-312.pyc
    │           │   │   ├── credentials.py
    │           │   │   ├── data.py
    │           │   │   ├── encryptedpassportelement.py
    │           │   │   ├── passportdata.py
    │           │   │   ├── passportelementerrors.py
    │           │   │   └── passportfile.py
    │           │   ├── payment
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── invoice.cpython-312.pyc
    │           │   │   │   ├── labeledprice.cpython-312.pyc
    │           │   │   │   ├── orderinfo.cpython-312.pyc
    │           │   │   │   ├── precheckoutquery.cpython-312.pyc
    │           │   │   │   ├── shippingaddress.cpython-312.pyc
    │           │   │   │   ├── shippingoption.cpython-312.pyc
    │           │   │   │   ├── shippingquery.cpython-312.pyc
    │           │   │   │   └── successfulpayment.cpython-312.pyc
    │           │   │   ├── invoice.py
    │           │   │   ├── labeledprice.py
    │           │   │   ├── orderinfo.py
    │           │   │   ├── precheckoutquery.py
    │           │   │   ├── shippingaddress.py
    │           │   │   ├── shippingoption.py
    │           │   │   ├── shippingquery.py
    │           │   │   └── successfulpayment.py
    │           │   ├── poll.py
    │           │   ├── proximityalerttriggered.py
    │           │   ├── py.typed
    │           │   ├── replykeyboardmarkup.py
    │           │   ├── replykeyboardremove.py
    │           │   ├── replymarkup.py
    │           │   ├── update.py
    │           │   ├── user.py
    │           │   ├── userprofilephotos.py
    │           │   ├── utils
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── deprecate.cpython-312.pyc
    │           │   │   │   ├── helpers.cpython-312.pyc
    │           │   │   │   ├── promise.cpython-312.pyc
    │           │   │   │   ├── request.cpython-312.pyc
    │           │   │   │   ├── types.cpython-312.pyc
    │           │   │   │   └── webhookhandler.cpython-312.pyc
    │           │   │   ├── deprecate.py
    │           │   │   ├── helpers.py
    │           │   │   ├── promise.py
    │           │   │   ├── request.py
    │           │   │   ├── types.py
    │           │   │   └── webhookhandler.py
    │           │   ├── vendor
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   └── __init__.cpython-312.pyc
    │           │   │   └── ptb_urllib3
    │           │   │       ├── __init__.py
    │           │   │       ├── __pycache__
    │           │   │       │   └── __init__.cpython-312.pyc
    │           │   │       └── urllib3
    │           │   │           ├── __init__.py
    │           │   │           ├── __pycache__
    │           │   │           │   ├── __init__.cpython-312.pyc
    │           │   │           │   ├── _collections.cpython-312.pyc
    │           │   │           │   ├── connection.cpython-312.pyc
    │           │   │           │   ├── connectionpool.cpython-312.pyc
    │           │   │           │   ├── exceptions.cpython-312.pyc
    │           │   │           │   ├── fields.cpython-312.pyc
    │           │   │           │   ├── filepost.cpython-312.pyc
    │           │   │           │   ├── poolmanager.cpython-312.pyc
    │           │   │           │   ├── request.cpython-312.pyc
    │           │   │           │   └── response.cpython-312.pyc
    │           │   │           ├── _collections.py
    │           │   │           ├── connection.py
    │           │   │           ├── connectionpool.py
    │           │   │           ├── contrib
    │           │   │           │   ├── __init__.py
    │           │   │           │   ├── __pycache__
    │           │   │           │   │   ├── __init__.cpython-312.pyc
    │           │   │           │   │   ├── appengine.cpython-312.pyc
    │           │   │           │   │   ├── ntlmpool.cpython-312.pyc
    │           │   │           │   │   ├── pyopenssl.cpython-312.pyc
    │           │   │           │   │   └── socks.cpython-312.pyc
    │           │   │           │   ├── appengine.py
    │           │   │           │   ├── ntlmpool.py
    │           │   │           │   ├── pyopenssl.py
    │           │   │           │   └── socks.py
    │           │   │           ├── exceptions.py
    │           │   │           ├── fields.py
    │           │   │           ├── filepost.py
    │           │   │           ├── packages
    │           │   │           │   ├── __init__.py
    │           │   │           │   ├── __pycache__
    │           │   │           │   │   ├── __init__.cpython-312.pyc
    │           │   │           │   │   ├── ordered_dict.cpython-312.pyc
    │           │   │           │   │   └── six.cpython-312.pyc
    │           │   │           │   ├── backports
    │           │   │           │   │   ├── __init__.py
    │           │   │           │   │   ├── __pycache__
    │           │   │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │           │   │   │   └── makefile.cpython-312.pyc
    │           │   │           │   │   └── makefile.py
    │           │   │           │   ├── ordered_dict.py
    │           │   │           │   ├── six.py
    │           │   │           │   └── ssl_match_hostname
    │           │   │           │       ├── __init__.py
    │           │   │           │       ├── __pycache__
    │           │   │           │       │   ├── __init__.cpython-312.pyc
    │           │   │           │       │   └── _implementation.cpython-312.pyc
    │           │   │           │       └── _implementation.py
    │           │   │           ├── poolmanager.py
    │           │   │           ├── request.py
    │           │   │           ├── response.py
    │           │   │           └── util
    │           │   │               ├── __init__.py
    │           │   │               ├── __pycache__
    │           │   │               │   ├── __init__.cpython-312.pyc
    │           │   │               │   ├── connection.cpython-312.pyc
    │           │   │               │   ├── request.cpython-312.pyc
    │           │   │               │   ├── response.cpython-312.pyc
    │           │   │               │   ├── retry.cpython-312.pyc
    │           │   │               │   ├── selectors.cpython-312.pyc
    │           │   │               │   ├── ssl_.cpython-312.pyc
    │           │   │               │   ├── timeout.cpython-312.pyc
    │           │   │               │   ├── url.cpython-312.pyc
    │           │   │               │   └── wait.cpython-312.pyc
    │           │   │               ├── connection.py
    │           │   │               ├── request.py
    │           │   │               ├── response.py
    │           │   │               ├── retry.py
    │           │   │               ├── selectors.py
    │           │   │               ├── ssl_.py
    │           │   │               ├── timeout.py
    │           │   │               ├── url.py
    │           │   │               └── wait.py
    │           │   ├── version.py
    │           │   ├── voicechat.py
    │           │   └── webhookinfo.py
    │           ├── tornado
    │           │   ├── __init__.py
    │           │   ├── __pycache__
    │           │   │   ├── __init__.cpython-312.pyc
    │           │   │   ├── _locale_data.cpython-312.pyc
    │           │   │   ├── auth.cpython-312.pyc
    │           │   │   ├── autoreload.cpython-312.pyc
    │           │   │   ├── concurrent.cpython-312.pyc
    │           │   │   ├── curl_httpclient.cpython-312.pyc
    │           │   │   ├── escape.cpython-312.pyc
    │           │   │   ├── gen.cpython-312.pyc
    │           │   │   ├── http1connection.cpython-312.pyc
    │           │   │   ├── httpclient.cpython-312.pyc
    │           │   │   ├── httpserver.cpython-312.pyc
    │           │   │   ├── httputil.cpython-312.pyc
    │           │   │   ├── ioloop.cpython-312.pyc
    │           │   │   ├── iostream.cpython-312.pyc
    │           │   │   ├── locale.cpython-312.pyc
    │           │   │   ├── locks.cpython-312.pyc
    │           │   │   ├── log.cpython-312.pyc
    │           │   │   ├── netutil.cpython-312.pyc
    │           │   │   ├── options.cpython-312.pyc
    │           │   │   ├── process.cpython-312.pyc
    │           │   │   ├── queues.cpython-312.pyc
    │           │   │   ├── routing.cpython-312.pyc
    │           │   │   ├── simple_httpclient.cpython-312.pyc
    │           │   │   ├── tcpclient.cpython-312.pyc
    │           │   │   ├── tcpserver.cpython-312.pyc
    │           │   │   ├── template.cpython-312.pyc
    │           │   │   ├── testing.cpython-312.pyc
    │           │   │   ├── util.cpython-312.pyc
    │           │   │   ├── web.cpython-312.pyc
    │           │   │   ├── websocket.cpython-312.pyc
    │           │   │   └── wsgi.cpython-312.pyc
    │           │   ├── _locale_data.py
    │           │   ├── auth.py
    │           │   ├── autoreload.py
    │           │   ├── concurrent.py
    │           │   ├── curl_httpclient.py
    │           │   ├── escape.py
    │           │   ├── gen.py
    │           │   ├── http1connection.py
    │           │   ├── httpclient.py
    │           │   ├── httpserver.py
    │           │   ├── httputil.py
    │           │   ├── ioloop.py
    │           │   ├── iostream.py
    │           │   ├── locale.py
    │           │   ├── locks.py
    │           │   ├── log.py
    │           │   ├── netutil.py
    │           │   ├── options.py
    │           │   ├── platform
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── asyncio.cpython-312.pyc
    │           │   │   │   ├── caresresolver.cpython-312.pyc
    │           │   │   │   └── twisted.cpython-312.pyc
    │           │   │   ├── asyncio.py
    │           │   │   ├── caresresolver.py
    │           │   │   └── twisted.py
    │           │   ├── process.py
    │           │   ├── py.typed
    │           │   ├── queues.py
    │           │   ├── routing.py
    │           │   ├── simple_httpclient.py
    │           │   ├── speedups.cpython-312-x86_64-linux-gnu.so
    │           │   ├── tcpclient.py
    │           │   ├── tcpserver.py
    │           │   ├── template.py
    │           │   ├── test
    │           │   │   ├── __main__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __main__.cpython-312.pyc
    │           │   │   │   ├── asyncio_test.cpython-312.pyc
    │           │   │   │   ├── auth_test.cpython-312.pyc
    │           │   │   │   ├── autoreload_test.cpython-312.pyc
    │           │   │   │   ├── concurrent_test.cpython-312.pyc
    │           │   │   │   ├── curl_httpclient_test.cpython-312.pyc
    │           │   │   │   ├── escape_test.cpython-312.pyc
    │           │   │   │   ├── gen_test.cpython-312.pyc
    │           │   │   │   ├── http1connection_test.cpython-312.pyc
    │           │   │   │   ├── httpclient_test.cpython-312.pyc
    │           │   │   │   ├── httpserver_test.cpython-312.pyc
    │           │   │   │   ├── httputil_test.cpython-312.pyc
    │           │   │   │   ├── import_test.cpython-312.pyc
    │           │   │   │   ├── ioloop_test.cpython-312.pyc
    │           │   │   │   ├── iostream_test.cpython-312.pyc
    │           │   │   │   ├── locale_test.cpython-312.pyc
    │           │   │   │   ├── locks_test.cpython-312.pyc
    │           │   │   │   ├── log_test.cpython-312.pyc
    │           │   │   │   ├── netutil_test.cpython-312.pyc
    │           │   │   │   ├── options_test.cpython-312.pyc
    │           │   │   │   ├── process_test.cpython-312.pyc
    │           │   │   │   ├── queues_test.cpython-312.pyc
    │           │   │   │   ├── resolve_test_helper.cpython-312.pyc
    │           │   │   │   ├── routing_test.cpython-312.pyc
    │           │   │   │   ├── runtests.cpython-312.pyc
    │           │   │   │   ├── simple_httpclient_test.cpython-312.pyc
    │           │   │   │   ├── tcpclient_test.cpython-312.pyc
    │           │   │   │   ├── tcpserver_test.cpython-312.pyc
    │           │   │   │   ├── template_test.cpython-312.pyc
    │           │   │   │   ├── testing_test.cpython-312.pyc
    │           │   │   │   ├── twisted_test.cpython-312.pyc
    │           │   │   │   ├── util.cpython-312.pyc
    │           │   │   │   ├── util_test.cpython-312.pyc
    │           │   │   │   ├── web_test.cpython-312.pyc
    │           │   │   │   ├── websocket_test.cpython-312.pyc
    │           │   │   │   └── wsgi_test.cpython-312.pyc
    │           │   │   ├── asyncio_test.py
    │           │   │   ├── auth_test.py
    │           │   │   ├── autoreload_test.py
    │           │   │   ├── concurrent_test.py
    │           │   │   ├── csv_translations
    │           │   │   │   └── fr_FR.csv
    │           │   │   ├── curl_httpclient_test.py
    │           │   │   ├── escape_test.py
    │           │   │   ├── gen_test.py
    │           │   │   ├── gettext_translations
    │           │   │   │   └── fr_FR
    │           │   │   │       └── LC_MESSAGES
    │           │   │   │           ├── tornado_test.mo
    │           │   │   │           └── tornado_test.po
    │           │   │   ├── http1connection_test.py
    │           │   │   ├── httpclient_test.py
    │           │   │   ├── httpserver_test.py
    │           │   │   ├── httputil_test.py
    │           │   │   ├── import_test.py
    │           │   │   ├── ioloop_test.py
    │           │   │   ├── iostream_test.py
    │           │   │   ├── locale_test.py
    │           │   │   ├── locks_test.py
    │           │   │   ├── log_test.py
    │           │   │   ├── netutil_test.py
    │           │   │   ├── options_test.cfg
    │           │   │   ├── options_test.py
    │           │   │   ├── options_test_types.cfg
    │           │   │   ├── options_test_types_str.cfg
    │           │   │   ├── process_test.py
    │           │   │   ├── queues_test.py
    │           │   │   ├── resolve_test_helper.py
    │           │   │   ├── routing_test.py
    │           │   │   ├── runtests.py
    │           │   │   ├── simple_httpclient_test.py
    │           │   │   ├── static
    │           │   │   │   ├── dir
    │           │   │   │   │   └── index.html
    │           │   │   │   ├── robots.txt
    │           │   │   │   ├── sample.xml
    │           │   │   │   ├── sample.xml.bz2
    │           │   │   │   └── sample.xml.gz
    │           │   │   ├── static_foo.txt
    │           │   │   ├── tcpclient_test.py
    │           │   │   ├── tcpserver_test.py
    │           │   │   ├── template_test.py
    │           │   │   ├── templates
    │           │   │   │   └── utf8.html
    │           │   │   ├── test.crt
    │           │   │   ├── test.key
    │           │   │   ├── testing_test.py
    │           │   │   ├── twisted_test.py
    │           │   │   ├── util.py
    │           │   │   ├── util_test.py
    │           │   │   ├── web_test.py
    │           │   │   ├── websocket_test.py
    │           │   │   └── wsgi_test.py
    │           │   ├── testing.py
    │           │   ├── util.py
    │           │   ├── web.py
    │           │   ├── websocket.py
    │           │   └── wsgi.py
    │           ├── tornado-6.1.dist-info
    │           │   ├── INSTALLER
    │           │   ├── LICENSE
    │           │   ├── METADATA
    │           │   ├── RECORD
    │           │   ├── REQUESTED
    │           │   ├── WHEEL
    │           │   └── top_level.txt
    │           ├── tzlocal
    │           │   ├── __init__.py
    │           │   ├── __pycache__
    │           │   │   ├── __init__.cpython-312.pyc
    │           │   │   ├── unix.cpython-312.pyc
    │           │   │   ├── utils.cpython-312.pyc
    │           │   │   ├── win32.cpython-312.pyc
    │           │   │   └── windows_tz.cpython-312.pyc
    │           │   ├── py.typed
    │           │   ├── unix.py
    │           │   ├── utils.py
    │           │   ├── win32.py
    │           │   └── windows_tz.py
    │           ├── tzlocal-5.2.dist-info
    │           │   ├── INSTALLER
    │           │   ├── LICENSE.txt
    │           │   ├── METADATA
    │           │   ├── RECORD
    │           │   ├── WHEEL
    │           │   └── top_level.txt
    │           ├── urllib3
    │           │   ├── __init__.py
    │           │   ├── __pycache__
    │           │   │   ├── __init__.cpython-312.pyc
    │           │   │   ├── _collections.cpython-312.pyc
    │           │   │   ├── _version.cpython-312.pyc
    │           │   │   ├── connection.cpython-312.pyc
    │           │   │   ├── connectionpool.cpython-312.pyc
    │           │   │   ├── exceptions.cpython-312.pyc
    │           │   │   ├── fields.cpython-312.pyc
    │           │   │   ├── filepost.cpython-312.pyc
    │           │   │   ├── poolmanager.cpython-312.pyc
    │           │   │   ├── request.cpython-312.pyc
    │           │   │   └── response.cpython-312.pyc
    │           │   ├── _collections.py
    │           │   ├── _version.py
    │           │   ├── connection.py
    │           │   ├── connectionpool.py
    │           │   ├── contrib
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   ├── _appengine_environ.cpython-312.pyc
    │           │   │   │   ├── appengine.cpython-312.pyc
    │           │   │   │   ├── ntlmpool.cpython-312.pyc
    │           │   │   │   ├── pyopenssl.cpython-312.pyc
    │           │   │   │   ├── securetransport.cpython-312.pyc
    │           │   │   │   └── socks.cpython-312.pyc
    │           │   │   ├── _appengine_environ.py
    │           │   │   ├── _securetransport
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   ├── bindings.cpython-312.pyc
    │           │   │   │   │   └── low_level.cpython-312.pyc
    │           │   │   │   ├── bindings.py
    │           │   │   │   └── low_level.py
    │           │   │   ├── appengine.py
    │           │   │   ├── ntlmpool.py
    │           │   │   ├── pyopenssl.py
    │           │   │   ├── securetransport.py
    │           │   │   └── socks.py
    │           │   ├── exceptions.py
    │           │   ├── fields.py
    │           │   ├── filepost.py
    │           │   ├── packages
    │           │   │   ├── __init__.py
    │           │   │   ├── __pycache__
    │           │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   └── six.cpython-312.pyc
    │           │   │   ├── backports
    │           │   │   │   ├── __init__.py
    │           │   │   │   ├── __pycache__
    │           │   │   │   │   ├── __init__.cpython-312.pyc
    │           │   │   │   │   ├── makefile.cpython-312.pyc
    │           │   │   │   │   └── weakref_finalize.cpython-312.pyc
    │           │   │   │   ├── makefile.py
    │           │   │   │   └── weakref_finalize.py
    │           │   │   └── six.py
    │           │   ├── poolmanager.py
    │           │   ├── request.py
    │           │   ├── response.py
    │           │   └── util
    │           │       ├── __init__.py
    │           │       ├── __pycache__
    │           │       │   ├── __init__.cpython-312.pyc
    │           │       │   ├── connection.cpython-312.pyc
    │           │       │   ├── proxy.cpython-312.pyc
    │           │       │   ├── queue.cpython-312.pyc
    │           │       │   ├── request.cpython-312.pyc
    │           │       │   ├── response.cpython-312.pyc
    │           │       │   ├── retry.cpython-312.pyc
    │           │       │   ├── ssl_.cpython-312.pyc
    │           │       │   ├── ssl_match_hostname.cpython-312.pyc
    │           │       │   ├── ssltransport.cpython-312.pyc
    │           │       │   ├── timeout.cpython-312.pyc
    │           │       │   ├── url.cpython-312.pyc
    │           │       │   └── wait.cpython-312.pyc
    │           │       ├── connection.py
    │           │       ├── proxy.py
    │           │       ├── queue.py
    │           │       ├── request.py
    │           │       ├── response.py
    │           │       ├── retry.py
    │           │       ├── ssl_.py
    │           │       ├── ssl_match_hostname.py
    │           │       ├── ssltransport.py
    │           │       ├── timeout.py
    │           │       ├── url.py
    │           │       └── wait.py
    │           └── urllib3-1.26.18.dist-info
    │               ├── INSTALLER
    │               ├── LICENSE.txt
    │               ├── METADATA
    │               ├── RECORD
    │               ├── REQUESTED
    │               ├── WHEEL
    │               └── top_level.txt
    ├── lib64 -> lib
    └── pyvenv.cfg

413 directories, 3918 files]
```

### Python Files
```
[/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_text_file.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_extension.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_config_cmd.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_msvccompiler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_check.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_filelist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/support.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_modified.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_archive_util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_build_scripts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_dir_util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_bdist_rpm.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_sysconfig.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_core.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_bdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_build_clib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_clean.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_install_headers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_build.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_mingwccompiler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_ccompiler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_install_data.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_install_lib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_build_ext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_sdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_log.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_bdist_dumb.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_cygwinccompiler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/unix_compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/tests/test_versionpredicate.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/_modified.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/core.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/_log.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/versionpredicate.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/archive_util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/_msvccompiler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/cygwinccompiler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/bdist_rpm.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/build_scripts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/build_clib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/install_lib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/config.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/bdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/install_scripts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/check.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/clean.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/_framework_compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/sdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/install_headers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/build_py.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/install_data.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/build_ext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/build.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/install_egg_info.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/command/bdist_dumb.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_distutils/fancy_getopt.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/namespaces.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/dist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/_elffile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/markers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/specifiers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/requirements.py       
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/_parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/tags.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/_manylinux.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/_musllinux.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/_tokenizer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/vendored/packaging/_structures.py        
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/macosx_libfile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/wheelfile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/bdist_wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/cli/convert.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/cli/unpack.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/cli/tags.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/cli/pack.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/cli/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/wheel/_setuptools_logging.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typing_extensions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/autocommand/automain.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/autocommand/errors.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/autocommand/autoasync.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/autocommand/autoparse.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/autocommand/autocommand.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/autocommand/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_functools.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/compat/py39.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/compat/py311.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_adapters.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_meta.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_itertools.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_text.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/_collections.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/diagnose.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/importlib_metadata/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_transformer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_union_transformer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_config.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_decorators.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_pytest_plugin.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_memo.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_importhook.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_suppression.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_functions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/typeguard/_checkers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/more_itertools/recipes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/more_itertools/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/more_itertools/more.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/functools/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/text/layouts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/text/strip-prefix.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/text/to-dvorak.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/text/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/text/to-qwerty.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/text/show-newlines.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/context.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/jaraco/collections/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/inflect/compat/py38.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/inflect/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/inflect/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/zipp/compat/py310.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/zipp/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/zipp/glob.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/zipp/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/_elffile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/markers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/licenses/_spdx.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/licenses/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/specifiers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/requirements.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/_parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/tags.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/_manylinux.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/_musllinux.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/_tokenizer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/packaging/_structures.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/api.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/unix.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/windows.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/android.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/platformdirs/macos.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/backports/tarfile/compat/py38.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/backports/tarfile/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/backports/tarfile/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/backports/tarfile/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/backports/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/tomli/_types.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/tomli/_re.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/tomli/_parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_vendor/tomli/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/compat/py39.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/compat/py310.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/compat/py312.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/compat/py311.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/discovery.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_path.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/depends.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/build_meta.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/errors.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_core_metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/windows_support.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/monkey.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_apply_pyprojecttoml.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/pyprojecttoml.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/formats.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/fastjsonschema_validations.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/fastjsonschema_exceptions.py/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/error_reporting.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/_validate_pyproject/extra_validations.py        
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/expand.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/setupcfg.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_itertools.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/glob.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/extension.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_reqs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/unicode_utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/logging.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_depends.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_find_py_modules.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_easy_install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_install_scripts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_logging.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/namespaces.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_dist_info.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/compat/py39.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_bdist_egg.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_dist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_editable_install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_virtualenv.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_egg_info.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_core_metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_bdist_wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_build_py.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/integration/helpers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/integration/test_pip_install_sdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/integration/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/environment.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/test_pyprojecttoml_dynamic_deps.py        
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/test_pyprojecttoml.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/test_setupcfg.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/test_apply_pyprojecttoml.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/downloads/preload.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/downloads/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/test_expand.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_distutils_adoption.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_setuptools.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_sandbox.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_glob.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/textwrap.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_windows_wrappers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_shutil_wrapper.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_archive_util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_manifest.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/fixtures.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_bdist_deprecations.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_namespaces.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_build_meta.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/server.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_build_clib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/text.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/contexts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_build.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_packageindex.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_setopt.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/mod_with_constant.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_find_packages.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_config_discovery.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/script-with-bom.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_build_ext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_sdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_extern.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_develop.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_unicode_utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_warnings.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/test_wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_importlib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_normalization.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/msvc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/package_index.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/_entry_points.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/launch.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/archive_util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/warnings.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/modified.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/easy_install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/bdist_rpm.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/build_clib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/install_lib.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/dist_info.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/install_scripts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/bdist_wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/rotate.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/sdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/alias.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/saveopts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/build_py.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/editable_wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/_requirestxt.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/build_ext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/build.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/egg_info.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/develop.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/setopt.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/install_egg_info.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/command/bdist_egg.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/installer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal/unix.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal/win32.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal/windows_tz.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/api.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/_internal_utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/status_codes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/models.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/certs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/hooks.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/sessions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/__version__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/adapters.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/cookies.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/help.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/auth.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/structures.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/requests/packages.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/test_markers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/test_integration_zope_interface.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/test_pkg_resources.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/data/my-test-package-source/setup.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/test_resources.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/test_find_distributions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/tests/test_working_set.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pkg_resources/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chatinvitelink.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/keyboardbutton.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/replykeyboardremove.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/replymarkup.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/proximityalerttriggered.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chatlocation.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/parsemode.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/messageentity.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chatmemberupdated.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chatpermissions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/invoice.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/orderinfo.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/shippingaddress.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/labeledprice.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/shippingoption.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/successfulpayment.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/shippingquery.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/precheckoutquery.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/base.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/passportfile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/encryptedpassportelement.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/data.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/credentials.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/passportelementerrors.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/passportdata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/user.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/choseninlineresult.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/messageautodeletetimerchanged.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/loginurl.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/response.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/response.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/ssl_.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/wait.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/retry.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/timeout.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/selectors.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/connection.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/url.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/request.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib/socks.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib/appengine.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib/pyopenssl.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib/ntlmpool.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/connection.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/fields.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/six.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/ordered_dict.py      
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/ssl_match_hostname/_implementation.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/ssl_match_hostname/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/backports/makefile.py/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/backports/__init__.py/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/filepost.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/_collections.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/connectionpool.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/poolmanager.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/request.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/video.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/file.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/location.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/voice.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/photosize.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/videonote.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/venue.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/animation.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/document.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/audio.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/contact.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/chatphoto.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/inputfile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/inputmedia.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/sticker.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/callbackquery.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/messagequeue.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/inlinequeryhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/callbackqueryhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/pollanswerhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/updater.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/stringcommandhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/choseninlineresulthandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/pollhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/dictpersistence.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/dispatcher.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/typehandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/jobqueue.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/messagehandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/commandhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/chatmemberhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/contexttypes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/precheckoutqueryhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/conversationhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/utils/webhookhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/utils/types.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/utils/promise.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/utils/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/extbot.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/defaults.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/callbackcontext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/picklepersistence.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/handler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/filters.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/regexhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/shippingqueryhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/callbackdatacache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/basepersistence.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/stringregexhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/messageid.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/dice.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/message.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chatmember.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/helpers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/webhookhandler.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/types.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/promise.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/deprecate.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/request.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/botcommandscope.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/botcommand.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/keyboardbuttonpolltype.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/error.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/chataction.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/games/callbackgame.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/games/game.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/games/gamehighscore.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/games/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/bot.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/userprofilephotos.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/constants.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/update.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/replykeyboardmarkup.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/forcereply.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/voicechat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/poll.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/webhookinfo.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedgif.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedvideo.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inputcontactmessagecontent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultphoto.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedsticker.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inputinvoicemessagecontent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinekeyboardmarkup.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultdocument.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedvoice.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultvoice.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inputvenuemessagecontent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresult.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedmpeg4gif.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcontact.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultmpeg4gif.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultlocation.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultvenue.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inputmessagecontent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedaudio.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinekeyboardbutton.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inputtextmessagecontent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultgif.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultarticle.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inputlocationmessagecontent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcachedphoto.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequery.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultaudio.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultcacheddocument.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultgame.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/inlinequeryresultvideo.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/bar.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_export_format.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/segment.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_emoji_replace.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/measure.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/live.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_win32_console.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/panel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/color_triplet.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_fileno.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/padding.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/abc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/color.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_spinners.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/control.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_emoji_codes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/pretty.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/errors.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/style.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/live_render.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_windows_renderer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/pager.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_windows.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/align.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/repr.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/columns.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_inspect.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/constrain.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/file_proxy.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_palettes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/markup.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/themes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/logging.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/styled.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_wrap.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/screen.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/rule.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/progress_bar.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_cell_widths.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_loop.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/jupyter.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/scope.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/syntax.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_stack.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/ansi.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/table.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/filesize.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/containers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/palette.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_pick.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/status.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/text.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/spinner.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_log_render.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/layout.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/box.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_null_file.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/diagnose.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/console.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/cells.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/highlighter.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/region.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_extension.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_ratio.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/terminal_theme.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/prompt.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/tree.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/emoji.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/progress.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/protocol.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/_timer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/traceback.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/default_styles.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/theme.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/rich/json.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/filters/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/python.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/_mapping.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexers/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/styles/_mapping.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/styles/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/style.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/filter.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/plugin.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatter.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/lexer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/modeline.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/token.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/groff.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/img.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/bbcode.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/pangomarkup.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/terminal.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/rtf.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/other.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/latex.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/irc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/_mapping.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/svg.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/html.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/formatters/terminal256.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/cmdline.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/console.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/unistring.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/sphinxext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/regexopt.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pygments/scanner.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/typing_extensions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/certifi/core.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/certifi/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/certifi/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/codec.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/core.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/package_data.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/idnadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/uts46data.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/idna/intranges.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/resources.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/index.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/markers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/manifest.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/locators.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/scripts.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distlib/database.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/adapter.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/cache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/serialize.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/redis_cache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/caches/file_cache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/wrapper.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/filewrapper.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/_cmd.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/heuristics.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/cachecontrol/controller.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/response.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/response.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/ssl_.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/wait.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/retry.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/timeout.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/ssl_match_hostname.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/connection.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/ssltransport.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/url.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/queue.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/proxy.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/util/request.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/socks.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_appengine_environ.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/appengine.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/pyopenssl.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/ntlmpool.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/securetransport.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/bindings.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/low_level.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/_securetransport/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/contrib/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/connection.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/fields.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/six.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/makefile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/weakref_finalize.py        
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/packages/backports/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/filepost.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/_collections.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/connectionpool.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/poolmanager.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/_version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/urllib3/request.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distro/distro.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distro/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/distro/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_impl.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/_in_process.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pyproject_hooks/_in_process/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/compat/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/compat/collections_abc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/reporters.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/resolvers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/providers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/resolvelib/structs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/msgpack/ext.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/msgpack/exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/msgpack/fallback.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/msgpack/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/api.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/_internal_utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/status_codes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/models.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/certs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/hooks.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/sessions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/__version__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/adapters.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/cookies.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/help.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/auth.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/structures.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/requests/packages.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/_elffile.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/markers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/specifiers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/requirements.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/_parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/tags.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/_manylinux.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/_musllinux.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/_tokenizer.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/packaging/_structures.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/pkg_resources/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/api.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/version.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/unix.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/windows.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/android.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/platformdirs/macos.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/truststore/_openssl.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/truststore/_windows.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/truststore/_ssl_constants.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/truststore/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/truststore/_api.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/truststore/_macos.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/tomli/_types.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/tomli/_re.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/tomli/_parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_vendor/tomli/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/build_env.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/base.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/pkg_resources.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_dists.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/importlib/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/importlib/_envs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/_json.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/metadata/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/distributions/installed.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/distributions/base.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/distributions/sdist.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/distributions/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/distributions/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/locations/base.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/locations/_distutils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/locations/_sysconfig.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/locations/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/configuration.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/cache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/xmlrpc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/lazy_wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/download.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/auth.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/utils.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/network/session.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/main.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/self_outdated_check.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/index/sources.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/index/package_finder.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/index/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/index/collector.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/exceptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/spinners.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/status_codes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/autocompletion.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/main.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/req_command.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/base_command.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/progress_bars.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/main_parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/cmdoptions.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/index_command.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/command_context.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/cli/parser.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/wheel_builder.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/candidate.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/index.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/installation_report.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/selection_prefs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/direct_url.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/format_control.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/search_scope.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/scheme.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/link.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/models/target_python.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/freeze.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/check.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/prepare.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/metadata_editable.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/wheel_legacy.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/metadata_legacy.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/build_tracker.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/wheel_editable.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/metadata.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/build/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/install/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/install/editable_legacy.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/operations/install/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/req/req_install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/req/req_file.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/req/constructors.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/req/req_set.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/req/req_uninstall.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/req/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/datetime.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/misc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/compat.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/appdirs.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/unpacking.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/filetypes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/filesystem.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/retry.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/egg_link.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/hashes.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/setuptools_build.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/packaging.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/direct_url_helpers.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/_jaraco_text.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/logging.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/subprocess.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/entrypoints.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/compatibility_tags.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/temp_dir.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/deprecation.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/encoding.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/_log.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/virtualenv.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/urls.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/utils/glibc.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/base.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/base.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/provider.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/factory.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/requirements.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/resolver.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/found_candidates.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/candidates.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/resolvelib/reporter.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/legacy/resolver.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/resolution/legacy/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/pyproject.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/cache.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/hash.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/index.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/freeze.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/configuration.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/search.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/show.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/check.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/download.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/debug.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/install.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/list.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/inspect.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/help.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/wheel.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/completion.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/commands/uninstall.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/vcs/bazaar.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/vcs/mercurial.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/vcs/versioncontrol.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/vcs/git.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/vcs/subversion.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/_internal/vcs/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/pip/__pip-runner__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/log_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/httpserver_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/httpclient_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/escape_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/routing_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/locks_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/resolve_test_helper.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/concurrent_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/import_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/testing_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/asyncio_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/util_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/iostream_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/template_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/tcpserver_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/tcpclient_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/simple_httpclient_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/runtests.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/gen_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/options_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/process_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/ioloop_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/http1connection_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/curl_httpclient_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/autoreload_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/locale_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/web_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/__main__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/netutil_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/auth_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/twisted_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/httputil_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/wsgi_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/queues_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/websocket_test.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/iostream.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/http1connection.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/log.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/netutil.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/process.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/httpserver.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/template.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/platform/caresresolver.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/platform/twisted.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/platform/asyncio.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/platform/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/web.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/util.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/websocket.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/queues.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/tcpserver.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/locale.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/autoreload.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/simple_httpclient.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/tcpclient.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/escape.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/wsgi.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/httpclient.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/auth.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/testing.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/ioloop.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/__init__.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/gen.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/concurrent.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/_locale_data.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/routing.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/options.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/httputil.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/locks.py
/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/curl_httpclient.py
/opt/KiTraderBot/user_management.py
/opt/KiTraderBot/__init__.py
/opt/KiTraderBot/bot.py
/opt/KiTraderBot/scripts/api.py
/opt/KiTraderBot/scripts/database_manager.py
/opt/KiTraderBot/scripts/gmail.py
/opt/KiTraderBot/scripts/bitstamp.py
/opt/KiTraderBot/scripts/binance.py
/opt/KiTraderBot/scripts/user_management.py
/opt/KiTraderBot/scripts/__init__.py
/opt/KiTraderBot/scripts/account.py]
```

### Dependencies
```
[argcomplete==3.4.0
attrs==23.2.0     
autocommand==2.2.2
Automat==22.10.0  
Babel==2.14.0     
bcc==0.30.0       
bcrypt==4.2.0     
blinker==1.8.2    
boto3==1.34.46    
botocore==1.34.46
certifi==2024.6.2
chardet==5.2.0
click==8.1.7
cloud-init==24.3.1
colorama==0.4.6
command-not-found==0.3
configobj==5.0.8
constantly==23.10.4
cryptography==42.0.5
dbus-python==1.3.2
distro==1.9.0
distro-info==1.9
gyp-next==0.16.2
httplib2==0.22.0
hyperlink==21.0.0
idna==3.6
incremental==24.7.2
inflect==7.3.1
jaraco.context==6.0.0
jaraco.functools==4.0.2
Jinja2==3.1.3
jmespath==1.0.1
jsonpatch==1.32
jsonpointer==2.0
jsonschema==4.19.2
jsonschema-specifications==2023.12.1
launchpadlib==2.0.0
lazr.restfulclient==0.14.6
lazr.uri==1.0.6
markdown-it-py==3.0.0
MarkupSafe==2.1.5
mdurl==0.1.2
more-itertools==10.3.0
netaddr==0.10.1
netifaces==0.11.0
oauthlib==3.2.2
packaging==24.1
pexpect==4.9.0
pipx==1.6.0
platformdirs==4.2.2
psutil==5.9.8
ptyprocess==0.7.0
pyasn1==0.5.1
pyasn1-modules==0.3.0
Pygments==2.18.0
PyGObject==3.48.2
PyHamcrest==2.1.0
PyJWT==2.7.0
pyOpenSSL==24.2.1
pyparsing==3.1.2
pyserial==3.5
python-apt==2.9.0+ubuntu1
python-dateutil==2.9.0
python-debian==0.1.49+ubuntu3
python-magic==0.4.27
PyYAML==6.0.2
referencing==0.35.1
requests==2.32.3
rich==13.7.1
rpds-py==0.20.0
s3transfer==0.10.1
service-identity==24.1.0
setuptools==74.1.2
six==1.16.0
sos==4.8.0
ssh-import-id==5.11
systemd-python==235
Twisted==24.7.0
typeguard==4.3.0
typing_extensions==4.12.2
ubuntu-pro-client==8001
ufw==0.36.2
unattended-upgrades==0.1
urllib3==2.0.7
userpath==1.9.1
wadllib==1.3.6
wheel==0.44.0
zipp==3.20.0
zope.interface==6.4]
```
Package                   Version
------------------------- --------------
argcomplete               3.4.0
attrs                     23.2.0
autocommand               2.2.2
Automat                   22.10.0
Babel                     2.14.0
bcc                       0.30.0
bcrypt                    4.2.0
blinker                   1.8.2
boto3                     1.34.46
botocore                  1.34.46
certifi                   2024.6.2
chardet                   5.2.0
click                     8.1.7
cloud-init                24.3.1
colorama                  0.4.6
command-not-found         0.3
configobj                 5.0.8
constantly                23.10.4
cryptography              42.0.5
dbus-python               1.3.2
distro                    1.9.0
distro-info               1.9
gyp-next                  0.16.2
httplib2                  0.22.0
hyperlink                 21.0.0
idna                      3.6
incremental               24.7.2
inflect                   7.3.1
jaraco.context            6.0.0
jaraco.functools          4.0.2
Jinja2                    3.1.3
jmespath                  1.0.1
jsonpatch                 1.32
jsonpointer               2.0
jsonschema                4.19.2
jsonschema-specifications 2023.12.1
launchpadlib              2.0.0
lazr.restfulclient        0.14.6
lazr.uri                  1.0.6
markdown-it-py            3.0.0
MarkupSafe                2.1.5
mdurl                     0.1.2
more-itertools            10.3.0
netaddr                   0.10.1
netifaces                 0.11.0
oauthlib                  3.2.2
packaging                 24.1
pexpect                   4.9.0
pip                       24.2
pipx                      1.6.0
platformdirs              4.2.2
psutil                    5.9.8
ptyprocess                0.7.0
pyasn1                    0.5.1
pyasn1-modules            0.3.0
Pygments                  2.18.0
PyGObject                 3.48.2
PyHamcrest                2.1.0
PyJWT                     2.7.0
pyOpenSSL                 24.2.1
pyparsing                 3.1.2
pyserial                  3.5
python-apt                2.9.0+ubuntu1
python-dateutil           2.9.0
python-debian             0.1.49+ubuntu3
python-magic              0.4.27
PyYAML                    6.0.2
referencing               0.35.1
requests                  2.32.3
rich                      13.7.1
rpds-py                   0.20.0
s3transfer                0.10.1
service-identity          24.1.0
setuptools                74.1.2
six                       1.16.0
sos                       4.8.0
ssh-import-id             5.11
systemd-python            235
Twisted                   24.7.0
typeguard                 4.3.0
typing_extensions         4.12.2
ubuntu-pro-client         8001
ufw                       0.36.2
unattended-upgrades       0.1
urllib3                   2.0.7
userpath                  1.9.1
wadllib                   1.3.6
wheel                     0.44.0
zipp                      3.20.0
zope.interface            6.4
### Virtual Environment
```
[Python version and path info will go here]
```

## 3. Configuration Files
### Config File Inventory
```
 [ no .conf files]
 [no .yaml files]
[/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/distutils.schema.json
/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/config/setuptools.schema.json
/opt/KiTraderBot/users.json
/opt/KiTraderBot/data/users.json]
```

### Service Configuration
```
[ kitraderbot.service - KiTrader Telegram Bot
     Loaded: loaded (/etc/systemd/system/kitraderbot.service; enabled; preset: enabled)
     Active: active (running) since Tue 2024-11-26 21:20:41 UTC; 1 day 3h ago
 Invocation: 0ffd3b256e2e40a88e42fa993a038d2b
   Main PID: 29946 (python)
      Tasks: 9 (limit: 2317)
     Memory: 37.9M (peak: 42.1M)
        CPU: 39.388s
     CGroup: /system.slice/kitraderbot.service
             └─29946 /opt/KiTraderBot/venv/bin/python bot.py

Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:     self._post(
Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:   File "/opt/KiTraderBot/venv/lib/python3.12/si>Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:     return self.request.post(
Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:            ^^^^^^^^^^^^^^^^^^
Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:   File "/opt/KiTraderBot/venv/lib/python3.12/si>Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:     result = self._request_wrapper(
Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:              ^^^^^^^^^^^^^^^^^^^^^^
Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:   File "/opt/KiTraderBot/venv/lib/python3.12/si>Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]:     raise Conflict(message)
Nov 26 21:50:24 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29946]: telegram.error.Conflict: Conflict: terminated b>lines 1-21]



```

### Recent Logs
```
Nov 26 21:10:07 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29666]:   warnings.warn(
Nov 26 21:10:08 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29666]: WARNING:root:Alerts from Gmail are disabled     
Nov 26 21:15:08 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Stopping kitraderbot.service - KiTrader Telegram B>Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29666]: No superusers file found
Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29666]: Starting bot...
Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29666]: Bot FantasySOL is running...
Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: kitraderbot.service: Deactivated successfully.     
Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Stopped kitraderbot.service - KiTrader Telegram Bo>Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Started kitraderbot.service - KiTrader Telegram Bo>Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: /opt/KiTraderBot/venv/lib/python3.12/site-packa>Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]:   warnings.warn(
Nov 26 21:15:10 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: WARNING:root:Alerts from Gmail are disabled     
Nov 26 21:15:16 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: WARNING:urllib3.connectionpool:Retrying (Retry(>Nov 26 21:15:21 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: WARNING:urllib3.connectionpool:Retrying (Retry(>Nov 26 21:20:34 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Stopping kitraderbot.service - KiTrader Telegram B>Nov 26 21:20:41 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: No superusers file found
Nov 26 21:20:41 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: Starting bot...
Nov 26 21:20:41 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 python[29803]: Bot FantasySOL is running...
Nov 26 21:20:41 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: kitraderbot.service: Deactivated successfully.     
Nov 26 21:20:41 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Stopped kitraderbot.service - KiTrader Telegram Bo>Nov 26 21:20:41 ubuntu-s-1vcpu-2gb-70gb-intel-nyc1-01 systemd[1]: Started kitraderbot.service - KiTrader Telegram Bo>lines 1-21]
```

## 4. Environment & Security
### Environment Variables
```
[Environment variables will go here]
```

### Token Files
```
[total 20
drwxr-xr-x 2 root root 4096 Nov 26 21:17 .
drwxr-xr-x 9 root root 4096 Nov 28 00:37 ..
-rw------- 1 root root    0 Nov 24 19:45 bitstamp
-rw------- 1 root root    0 Nov 24 19:45 bitstamp_secret
-rw------- 1 root root  135 Nov 26 18:26 database
-rw-r--r-- 1 root root   22 Nov 26 21:20 superusers
-rw------- 1 root root   47 Nov 24 19:46 telegram

6213058967
5123185118]
```

## 5. Logging & Monitoring
### System Logs
```
[System log entries will go here]
```

### PostgreSQL Logs
```
[ closed_at TIMESTAMP,
            pnl DECIMAL(20,8)
        );
2024-11-26 18:04:03.049 UTC [26850] postgres@fantasysol ERROR:  relation "users" does not exist
2024-11-26 18:04:03.049 UTC [26850] postgres@fantasysol STATEMENT:  CREATE TABLE user_settings (
            user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
            notification_preferences JSONB DEFAULT '{}',
            risk_settings JSONB DEFAULT '{}',
            ui_preferences JSONB DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
2024-11-26 18:04:43.847 UTC [26850] postgres@fantasysol ERROR:  relation "users" already exists
2024-11-26 18:04:43.847 UTC [26850] postgres@fantasysol STATEMENT:  CREATE TABLE users (
        user_id SERIAL PRIMARY KEY,
        telegram_id BIGINT UNIQUE NOT NULL,
        username VARCHAR(255),
        role VARCHAR(50) DEFAULT 'basic',
        registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP,
        account_status VARCHAR(50) DEFAULT 'active'
        );
2024-11-26 18:04:44.046 UTC [26850] postgres@fantasysol ERROR:  relation "trades" already exists
2024-11-26 18:04:44.046 UTC [26850] postgres@fantasysol STATEMENT:  CREATE TABLE trades (
        trade_id SERIAL PRIMARY KEY,
        user_id INTEGER REFERENCES users(user_id),
        symbol VARCHAR(20) NOT NULL,
        entry_price DECIMAL(20,8) NOT NULL,
        exit_price DECIMAL(20,8),
        position_size DECIMAL(20,8) NOT NULL,
        trade_type VARCHAR(10) NOT NULL,
        trade_status VARCHAR(20) DEFAULT 'open',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        closed_at TIMESTAMP,
        pnl DECIMAL(20,8)
        );
2024-11-26 18:04:45.921 UTC [26850] postgres@fantasysol ERROR:  relation "user_settings" already exists
2024-11-26 18:04:45.921 UTC [26850] postgres@fantasysol STATEMENT:  CREATE TABLE user_settings (
        user_id INTEGER PRIMARY KEY REFERENCES users(user_id),
        notification_preferences JSONB DEFAULT '{}',
        risk_settings JSONB DEFAULT '{}',
        ui_preferences JSONB DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
2024-11-26 18:05:35.206 UTC [26705] LOG:  checkpoint complete: wrote 933 buffers (5.7%); 1 WAL file(s) added, 0 removed, 0 recycled; write=93.572 s, sync=0.052 s, total=93.689 s; sync files=323, longest=0.012 s, average=0.001 s; distance=4281 kB, estimate=4516 kB; lsn=0/1DD23D0, redo lsn=0/1D8D6B0
2024-11-26 18:08:21.173 UTC [26892] postgres@fantasysol ERROR:  column "created_at" of relation "trades" already exists
2024-11-26 18:08:21.173 UTC [26892] postgres@fantasysol STATEMENT:  ALTER TABLE trades
        ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ADD COLUMN closed_at TIMESTAMP,
        ADD COLUMN pnl DECIMAL(20,8);
2024-11-26 18:08:57.657 UTC [26892] postgres@fantasysol ERROR:  column "created_at" of relation "trades" already exists
2024-11-26 18:08:57.657 UTC [26892] postgres@fantasysol STATEMENT:  ALTER TABLE trades
        ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ADD COLUMN closed_at TIMESTAMP,
        ADD COLUMN pnl DECIMAL(20,8);
2024-11-26 18:09:01.266 UTC [26705] LOG:  checkpoint starting: time
2024-11-26 18:09:04.207 UTC [26705] LOG:  checkpoint complete: wrote 30 buffers (0.2%); 0 WAL file(s) added, 0 removed, 0 recycled; write=2.923 s, sync=0.004 s, total=2.941 s; sync files=23, longest=0.002 s, average=0.001 s; distance=279 kB, estimate=4092 kB; lsn=0/1DD33F8, redo lsn=0/1DD33C0
2024-11-26 18:10:25.786 UTC [26910] postgres@fantasysol ERROR:  column "created_at" of relation "trades" already exists
2024-11-26 18:10:25.786 UTC [26910] postgres@fantasysol STATEMENT:  ALTER TABLE trades
        ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP;
2024-11-26 18:12:04.726 UTC [26919] postgres@fantasysol ERROR:  syntax error at or near "2" at character 20
2024-11-26 18:12:04.726 UTC [26919] postgres@fantasysol STATEMENT:  ALTER TABLE trades
        2|ADD COLUMN closed_at TIMESTAMP,
        ADD COLUMN pnl DECIMAL(20,8);
2024-11-26 18:12:22.019 UTC [26919] postgres@fantasysol ERROR:  column "closed_at" of relation "trades" already exists
2024-11-26 18:12:22.019 UTC [26919] postgres@fantasysol STATEMENT:  ALTER TABLE trades
        ADD COLUMN closed_at TIMESTAMP,
        ADD COLUMN pnl DECIMAL(20,8);
2024-11-26 18:14:01.222 UTC [26705] LOG:  checkpoint starting: time
2024-11-26 18:14:02.103 UTC [26705] LOG:  checkpoint complete: wrote 9 buffers (0.1%); 0 WAL file(s) added, 0 removed, 0 recycled; write=0.828 s, sync=0.010 s, total=0.881 s; sync files=6, longest=0.009 s, average=0.002 s; distance=6 
kB, estimate=3683 kB; lsn=0/1DD4D70, redo lsn=0/1DD4D38
2024-11-26 18:15:16.587 UTC [26945] postgres@fantasysol ERROR:  column "closed_at" of relation "trades" already exists
2024-11-26 18:15:16.587 UTC [26945] postgres@fantasysol STATEMENT:  ALTER TABLE trades
        ADD COLUMN closed_at TIMESTAMP,
        ADD COLUMN pnl DECIMAL(20,8);
2024-11-26 18:19:01.188 UTC [26705] LOG:  checkpoint starting: time
2024-11-26 18:19:02.610 UTC [26705] LOG:  checkpoint complete: wrote 15 buffers (0.1%); 0 WAL file(s) added, 0 removed, 0 recycled; write=1.409 s, sync=0.003 s, total=1.422 s; sync files=14, longest=0.002 s, average=0.001 s; distance=54 kB, estimate=3320 kB; lsn=0/1DE28F8, redo lsn=0/1DE28C0
2024-11-26 19:30:40.919 UTC [27512] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:30:40.921 UTC [27513] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:30:40.923 UTC [27514] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:30:40.925 UTC [27515] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:30:40.927 UTC [27516] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:36:21.013 UTC [27560] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:36:21.014 UTC [27564] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:36:21.015 UTC [27561] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:36:21.017 UTC [27562] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:36:21.019 UTC [27563] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:42:08.779 UTC [27619] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:42:08.779 UTC [27618] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:42:08.781 UTC [27620] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:42:08.784 UTC [27621] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 19:42:08.788 UTC [27622] fantasysol_user@fantasysol LOG:  could not receive data from client: Connection reset by peer
2024-11-26 20:44:03.278 UTC [26705] LOG:  checkpoint starting: time
2024-11-26 20:45:37.449 UTC [26705] LOG:  checkpoint complete: wrote 939 buffers (5.7%); 0 WAL file(s) added, 0 removed, 1 recycled; write=94.146 s, sync=0.016 s, total=94.171 s; sync files=307, longest=0.003 s, average=0.001 s; distance=4283 kB, estimate=4283 kB; lsn=0/2211548, redo lsn=0/2211510
2024-11-26 20:49:54.597 UTC [28978] postgres@postgres ERROR:  database "kitrader_db" already exists
2024-11-26 20:49:54.597 UTC [28978] postgres@postgres STATEMENT:  CREATE DATABASE kitrader_db;
2024-11-26 20:51:45.047 UTC [29021] root@fantasysol FATAL:  role "root" does not exist
2024-11-26 20:51:52.408 UTC [29025] root@fantasysol FATAL:  role "root" does not exist
2024-11-28 00:09:24.486 UTC [26705] LOG:  checkpoint starting: time
2024-11-28 00:09:25.607 UTC [26705] LOG:  checkpoint complete: wrote 11 buffers (0.1%); 0 WAL file(s) added, 0 removed, 0 recycled; write=1.107 s, sync=0.003 s, total=1.121 s; sync files=6, longest=0.002 s, average=0.001 s; distance=21 kB, estimate=3856 kB; lsn=0/2216C30, redo lsn=0/2216BF8]
```

## 6. Permissions & Access
### File Permissions
```
[-rw-r--r-- 1 root root   685 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  7210 Nov 24 19:58 contexts.cpython-312.pyc
-rw-r--r-- 1 root root  3532 Nov 24 19:58 environment.cpython-312.pyc
-rw-r--r-- 1 root root  7148 Nov 24 19:58 fixtures.cpython-312.pyc
-rw-r--r-- 1 root root   211 Nov 24 19:58 mod_with_constant.cpython-312.pyc
-rw-r--r-- 1 root root  4191 Nov 24 19:58 namespaces.cpython-312.pyc
-rw-r--r-- 1 root root   205 Nov 24 19:58 script-with-bom.cpython-312.pyc
-rw-r--r-- 1 root root  4944 Nov 24 19:58 server.cpython-312.pyc
-rw-r--r-- 1 root root  1861 Nov 24 19:58 test_archive_util.cpython-312.pyc
-rw-r--r-- 1 root root  1560 Nov 24 19:58 test_bdist_deprecations.cpython-312.pyc
-rw-r--r-- 1 root root  4112 Nov 24 19:58 test_bdist_egg.cpython-312.pyc
-rw-r--r-- 1 root root 29459 Nov 24 19:58 test_bdist_wheel.cpython-312.pyc
-rw-r--r-- 1 root root  1590 Nov 24 19:58 test_build.cpython-312.pyc
-rw-r--r-- 1 root root  4135 Nov 24 19:58 test_build_clib.cpython-312.pyc
-rw-r--r-- 1 root root 13326 Nov 24 19:58 test_build_ext.cpython-312.pyc
-rw-r--r-- 1 root root 43509 Nov 24 19:58 test_build_meta.cpython-312.pyc
-rw-r--r-- 1 root root 16997 Nov 24 19:58 test_build_py.cpython-312.pyc
-rw-r--r-- 1 root root 30531 Nov 24 19:58 test_config_discovery.cpython-312.pyc
-rw-r--r-- 1 root root 17770 Nov 24 19:58 test_core_metadata.cpython-312.pyc
-rw-r--r-- 1 root root   918 Nov 24 19:58 test_depends.cpython-312.pyc
-rw-r--r-- 1 root root  8596 Nov 24 19:58 test_develop.cpython-312.pyc
-rw-r--r-- 1 root root 10900 Nov 24 19:58 test_dist.cpython-312.pyc
-rw-r--r-- 1 root root 11183 Nov 24 19:58 test_dist_info.cpython-312.pyc
-rw-r--r-- 1 root root  8216 Nov 24 19:58 test_distutils_adoption.cpython-312.pyc
-rw-r--r-- 1 root root 70591 Nov 24 19:58 test_easy_install.cpython-312.pyc
-rw-r--r-- 1 root root 57533 Nov 24 19:58 test_editable_install.cpython-312.pyc
-rw-r--r-- 1 root root 47343 Nov 24 19:58 test_egg_info.cpython-312.pyc
-rw-r--r-- 1 root root   833 Nov 24 19:58 test_extern.cpython-312.pyc
-rw-r--r-- 1 root root 12170 Nov 24 19:58 test_find_packages.cpython-312.pyc
-rw-r--r-- 1 root root  3791 Nov 24 19:58 test_find_py_modules.cpython-312.pyc
-rw-r--r-- 1 root root  1250 Nov 24 19:58 test_glob.cpython-312.pyc
-rw-r--r-- 1 root root  6102 Nov 24 19:58 test_install_scripts.cpython-312.pyc
-rw-r--r-- 1 root root  3177 Nov 24 19:58 test_logging.cpython-312.pyc
-rw-r--r-- 1 root root 26708 Nov 24 19:58 test_manifest.cpython-312.pyc
-rw-r--r-- 1 root root  5497 Nov 24 19:58 test_namespaces.cpython-312.pyc
-rw-r--r-- 1 root root 18562 Nov 24 19:58 test_packageindex.cpython-312.pyc
-rw-r--r-- 1 root root  9529 Nov 24 19:58 test_sandbox.cpython-312.pyc
-rw-r--r-- 1 root root 45553 Nov 24 19:58 test_sdist.cpython-312.pyc
-rw-r--r-- 1 root root  2853 Nov 24 19:58 test_setopt.cpython-312.pyc
-rw-r--r-- 1 root root 17545 Nov 24 19:58 test_setuptools.cpython-312.pyc
-rw-r--r-- 1 root root  1340 Nov 24 19:58 test_shutil_wrapper.cpython-312.pyc
-rw-r--r-- 1 root root   796 Nov 24 19:58 test_unicode_utils.cpython-312.pyc
-rw-r--r-- 1 root root  4436 Nov 24 19:58 test_virtualenv.cpython-312.pyc
-rw-r--r-- 1 root root  4124 Nov 24 19:58 test_warnings.cpython-312.pyc
-rw-r--r-- 1 root root 19145 Nov 24 19:58 test_wheel.cpython-312.pyc
-rw-r--r-- 1 root root 10470 Nov 24 19:58 test_windows_wrappers.cpython-312.pyc
-rw-r--r-- 1 root root   512 Nov 24 19:58 text.cpython-312.pyc
-rw-r--r-- 1 root root   428 Nov 24 19:58 textwrap.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/compat:
total 8
-rw-r--r-- 1 root root    0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root  135 Nov 24 19:58 py39.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/compat/__pycache__:
total 8
-rw-r--r-- 1 root root 183 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 350 Nov 24 19:58 py39.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config:
total 96
-rw-r--r-- 1 root root     0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
drwxr-xr-x 3 root root  4096 Nov 24 19:58 downloads
-rw-r--r-- 1 root root  1912 Nov 24 19:58 setupcfg_examples.txt
-rw-r--r-- 1 root root 19296 Nov 24 19:58 test_apply_pyprojecttoml.py
-rw-r--r-- 1 root root  8129 Nov 24 19:58 test_expand.py
-rw-r--r-- 1 root root 12406 Nov 24 19:58 test_pyprojecttoml.py
-rw-r--r-- 1 root root  3271 Nov 24 19:58 test_pyprojecttoml_dynamic_deps.py
-rw-r--r-- 1 root root 33197 Nov 24 19:58 test_setupcfg.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/__pycache__:
total 112
-rw-r--r-- 1 root root   183 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 27893 Nov 24 19:58 test_apply_pyprojecttoml.cpython-312.pyc
-rw-r--r-- 1 root root 10747 Nov 24 19:58 test_expand.cpython-312.pyc
-rw-r--r-- 1 root root 15789 Nov 24 19:58 test_pyprojecttoml.cpython-312.pyc
-rw-r--r-- 1 root root  4232 Nov 24 19:58 test_pyprojecttoml_dynamic_deps.cpython-312.pyc
-rw-r--r-- 1 root root 42874 Nov 24 19:58 test_setupcfg.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/downloads:
total 12
-rw-r--r-- 1 root root 1827 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root  450 Nov 24 19:58 preload.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/config/downloads/__pycache__:
total 8
-rw-r--r-- 1 root root 3095 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  781 Nov 24 19:58 preload.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/indexes:
total 4
drwxr-xr-x 3 root root 4096 Nov 24 19:58 test_links_priority

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/indexes/test_links_priority:
total 8
-rw-r--r-- 1 root root   92 Nov 24 19:58 external.html
drwxr-xr-x 3 root root 4096 Nov 24 19:58 simple

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/indexes/test_links_priority/simple:
total 4
drwxr-xr-x 2 root root 4096 Nov 24 19:58 foobar

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/indexes/test_links_priority/simple/foobar:       
total 4
-rw-r--r-- 1 root root 174 Nov 24 19:58 index.html

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/integration:
total 20
-rw-r--r-- 1 root root    0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root 2522 Nov 24 19:58 helpers.py
-rw-r--r-- 1 root root 8204 Nov 24 19:58 test_pip_install_sdist.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools/tests/integration/__pycache__:
total 24
-rw-r--r-- 1 root root  188 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 4621 Nov 24 19:58 helpers.cpython-312.pyc
-rw-r--r-- 1 root root 9125 Nov 24 19:58 test_pip_install_sdist.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/setuptools-75.6.0.dist-info:
total 104
-rw-r--r-- 1 root root     4 Nov 24 19:58 INSTALLER
-rw-r--r-- 1 root root  1023 Nov 24 19:58 LICENSE
-rw-r--r-- 1 root root  6674 Nov 24 19:58 METADATA
-rw-r--r-- 1 root root 74030 Nov 24 19:58 RECORD
-rw-r--r-- 1 root root    91 Nov 24 19:58 WHEEL
-rw-r--r-- 1 root root  2449 Nov 24 19:58 entry_points.txt
-rw-r--r-- 1 root root    41 Nov 24 19:58 top_level.txt

/opt/KiTraderBot/venv/lib/python3.12/site-packages/six-1.16.0.dist-info:
total 24
-rw-r--r-- 1 root root    4 Nov 24 19:58 INSTALLER
-rw-r--r-- 1 root root 1066 Nov 24 19:58 LICENSE
-rw-r--r-- 1 root root 1795 Nov 24 19:58 METADATA
-rw-r--r-- 1 root root  646 Nov 24 19:58 RECORD
-rw-r--r-- 1 root root    0 Nov 24 19:58 REQUESTED
-rw-r--r-- 1 root root  110 Nov 24 19:58 WHEEL
-rw-r--r-- 1 root root    4 Nov 24 19:58 top_level.txt

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram:
total 764
-rw-r--r-- 1 root root  10983 Nov 24 19:59 __init__.py
-rw-r--r-- 1 root root   1779 Nov 24 19:59 __main__.py
drwxr-xr-x 2 root root   4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root   5148 Nov 24 19:59 base.py
-rw-r--r-- 1 root root 245576 Nov 24 19:59 bot.py
-rw-r--r-- 1 root root   1869 Nov 24 19:59 botcommand.py
-rw-r--r-- 1 root root   9964 Nov 24 19:59 botcommandscope.py
-rw-r--r-- 1 root root  23195 Nov 24 19:59 callbackquery.py
-rw-r--r-- 1 root root  56946 Nov 24 19:59 chat.py
-rw-r--r-- 1 root root   3198 Nov 24 19:59 chataction.py
-rw-r--r-- 1 root root   4245 Nov 24 19:59 chatinvitelink.py
-rw-r--r-- 1 root root   2513 Nov 24 19:59 chatlocation.py
-rw-r--r-- 1 root root  28539 Nov 24 19:59 chatmember.py
-rw-r--r-- 1 root root   6597 Nov 24 19:59 chatmemberupdated.py
-rw-r--r-- 1 root root   6007 Nov 24 19:59 chatpermissions.py
-rw-r--r-- 1 root root   3816 Nov 24 19:59 choseninlineresult.py
-rw-r--r-- 1 root root  13016 Nov 24 19:59 constants.py
-rw-r--r-- 1 root root   4002 Nov 24 19:59 dice.py
-rw-r--r-- 1 root root   4255 Nov 24 19:59 error.py
drwxr-xr-x 4 root root   4096 Nov 24 19:59 ext
drwxr-xr-x 3 root root   4096 Nov 24 19:59 files
-rw-r--r-- 1 root root   3044 Nov 24 19:59 forcereply.py
drwxr-xr-x 3 root root   4096 Nov 24 19:59 games
drwxr-xr-x 3 root root   4096 Nov 24 19:59 inline
-rw-r--r-- 1 root root   3614 Nov 24 19:59 keyboardbutton.py
-rw-r--r-- 1 root root   1837 Nov 24 19:59 keyboardbuttonpolltype.py
-rw-r--r-- 1 root root   4094 Nov 24 19:59 loginurl.py
-rw-r--r-- 1 root root 118913 Nov 24 19:59 message.py
-rw-r--r-- 1 root root   1913 Nov 24 19:59 messageautodeletetimerchanged.py
-rw-r--r-- 1 root root   5705 Nov 24 19:59 messageentity.py
-rw-r--r-- 1 root root   1481 Nov 24 19:59 messageid.py
-rw-r--r-- 1 root root   1783 Nov 24 19:59 parsemode.py
drwxr-xr-x 3 root root   4096 Nov 24 19:59 passport
drwxr-xr-x 3 root root   4096 Nov 24 19:59 payment
-rw-r--r-- 1 root root  12268 Nov 24 19:59 poll.py
-rw-r--r-- 1 root root   2654 Nov 24 19:59 proximityalerttriggered.py
-rw-r--r-- 1 root root      0 Nov 24 19:59 py.typed
-rw-r--r-- 1 root root  12527 Nov 24 19:59 replykeyboardmarkup.py
-rw-r--r-- 1 root root   2743 Nov 24 19:59 replykeyboardremove.py
-rw-r--r-- 1 root root   1200 Nov 24 19:59 replymarkup.py
-rw-r--r-- 1 root root  15582 Nov 24 19:59 update.py
-rw-r--r-- 1 root root  40811 Nov 24 19:59 user.py
-rw-r--r-- 1 root root   2808 Nov 24 19:59 userprofilephotos.py
drwxr-xr-x 3 root root   4096 Nov 24 19:59 utils
drwxr-xr-x 4 root root   4096 Nov 24 19:59 vendor
-rw-r--r-- 1 root root    956 Nov 24 19:59 version.py
-rw-r--r-- 1 root root   5209 Nov 24 19:59 voicechat.py
-rw-r--r-- 1 root root   4665 Nov 24 19:59 webhookinfo.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/__pycache__:
total 696
-rw-r--r-- 1 root root   8709 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root   1769 Nov 24 19:59 __main__.cpython-312.pyc
-rw-r--r-- 1 root root   5856 Nov 24 19:59 base.cpython-312.pyc
-rw-r--r-- 1 root root 226747 Nov 24 19:59 bot.cpython-312.pyc
-rw-r--r-- 1 root root   1528 Nov 24 19:59 botcommand.cpython-312.pyc
-rw-r--r-- 1 root root  11807 Nov 24 19:59 botcommandscope.cpython-312.pyc
-rw-r--r-- 1 root root  21227 Nov 24 19:59 callbackquery.cpython-312.pyc
-rw-r--r-- 1 root root  49455 Nov 24 19:59 chat.cpython-312.pyc
-rw-r--r-- 1 root root   2317 Nov 24 19:59 chataction.cpython-312.pyc
-rw-r--r-- 1 root root   4247 Nov 24 19:59 chatinvitelink.cpython-312.pyc
-rw-r--r-- 1 root root   2397 Nov 24 19:59 chatlocation.cpython-312.pyc
-rw-r--r-- 1 root root  28477 Nov 24 19:59 chatmember.cpython-312.pyc
-rw-r--r-- 1 root root   7000 Nov 24 19:59 chatmemberupdated.cpython-312.pyc
-rw-r--r-- 1 root root   5194 Nov 24 19:59 chatpermissions.cpython-312.pyc
-rw-r--r-- 1 root root   3637 Nov 24 19:59 choseninlineresult.cpython-312.pyc
-rw-r--r-- 1 root root  13566 Nov 24 19:59 constants.cpython-312.pyc
-rw-r--r-- 1 root root   3623 Nov 24 19:59 dice.cpython-312.pyc
-rw-r--r-- 1 root root   6258 Nov 24 19:59 error.cpython-312.pyc
-rw-r--r-- 1 root root   2634 Nov 24 19:59 forcereply.cpython-312.pyc
-rw-r--r-- 1 root root   3153 Nov 24 19:59 keyboardbutton.cpython-312.pyc
-rw-r--r-- 1 root root   1496 Nov 24 19:59 keyboardbuttonpolltype.cpython-312.pyc
-rw-r--r-- 1 root root   3629 Nov 24 19:59 loginurl.cpython-312.pyc
-rw-r--r-- 1 root root 111183 Nov 24 19:59 message.cpython-312.pyc
-rw-r--r-- 1 root root   1570 Nov 24 19:59 messageautodeletetimerchanged.cpython-312.pyc
-rw-r--r-- 1 root root   5322 Nov 24 19:59 messageentity.cpython-312.pyc
-rw-r--r-- 1 root root   1169 Nov 24 19:59 messageid.cpython-312.pyc
-rw-r--r-- 1 root root   1276 Nov 24 19:59 parsemode.cpython-312.pyc
-rw-r--r-- 1 root root  13299 Nov 24 19:59 poll.cpython-312.pyc
-rw-r--r-- 1 root root   2673 Nov 24 19:59 proximityalerttriggered.cpython-312.pyc
-rw-r--r-- 1 root root  12494 Nov 24 19:59 replykeyboardmarkup.cpython-312.pyc
-rw-r--r-- 1 root root   2397 Nov 24 19:59 replykeyboardremove.cpython-312.pyc
-rw-r--r-- 1 root root    740 Nov 24 19:59 replymarkup.cpython-312.pyc
-rw-r--r-- 1 root root  15157 Nov 24 19:59 update.cpython-312.pyc
-rw-r--r-- 1 root root  33871 Nov 24 19:59 user.cpython-312.pyc
-rw-r--r-- 1 root root   3610 Nov 24 19:59 userprofilephotos.cpython-312.pyc
-rw-r--r-- 1 root root    311 Nov 24 19:59 version.cpython-312.pyc
-rw-r--r-- 1 root root   6441 Nov 24 19:59 voicechat.cpython-312.pyc
-rw-r--r-- 1 root root   3982 Nov 24 19:59 webhookinfo.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext:
total 532
-rw-r--r-- 1 root root  3547 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 23836 Nov 24 19:59 basepersistence.py
-rw-r--r-- 1 root root 14479 Nov 24 19:59 callbackcontext.py
-rw-r--r-- 1 root root 17176 Nov 24 19:59 callbackdatacache.py
-rw-r--r-- 1 root root 10842 Nov 24 19:59 callbackqueryhandler.py
-rw-r--r-- 1 root root  7034 Nov 24 19:59 chatmemberhandler.py
-rw-r--r-- 1 root root  7130 Nov 24 19:59 choseninlineresulthandler.py
-rw-r--r-- 1 root root 20693 Nov 24 19:59 commandhandler.py
-rw-r--r-- 1 root root  6026 Nov 24 19:59 contexttypes.py
-rw-r--r-- 1 root root 31360 Nov 24 19:59 conversationhandler.py
-rw-r--r-- 1 root root 10386 Nov 24 19:59 defaults.py
-rw-r--r-- 1 root root 15978 Nov 24 19:59 dictpersistence.py
-rw-r--r-- 1 root root 33944 Nov 24 19:59 dispatcher.py
-rw-r--r-- 1 root root 13406 Nov 24 19:59 extbot.py
-rw-r--r-- 1 root root 86691 Nov 24 19:59 filters.py
-rw-r--r-- 1 root root 11226 Nov 24 19:59 handler.py
-rw-r--r-- 1 root root  9794 Nov 24 19:59 inlinequeryhandler.py
-rw-r--r-- 1 root root 27032 Nov 24 19:59 jobqueue.py
-rw-r--r-- 1 root root  9710 Nov 24 19:59 messagehandler.py
-rw-r--r-- 1 root root 14773 Nov 24 19:59 messagequeue.py
-rw-r--r-- 1 root root 18616 Nov 24 19:59 picklepersistence.py
-rw-r--r-- 1 root root  4832 Nov 24 19:59 pollanswerhandler.py
-rw-r--r-- 1 root root  4808 Nov 24 19:59 pollhandler.py
-rw-r--r-- 1 root root  4845 Nov 24 19:59 precheckoutqueryhandler.py
-rw-r--r-- 1 root root  7823 Nov 24 19:59 regexhandler.py
-rw-r--r-- 1 root root  4831 Nov 24 19:59 shippingqueryhandler.py
-rw-r--r-- 1 root root  6445 Nov 24 19:59 stringcommandhandler.py
-rw-r--r-- 1 root root  7164 Nov 24 19:59 stringregexhandler.py
-rw-r--r-- 1 root root  4743 Nov 24 19:59 typehandler.py
-rw-r--r-- 1 root root 35830 Nov 24 19:59 updater.py
drwxr-xr-x 3 root root  4096 Nov 24 19:59 utils

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/__pycache__:
total 556
-rw-r--r-- 1 root root  2471 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 26264 Nov 24 19:59 basepersistence.cpython-312.pyc
-rw-r--r-- 1 root root 16278 Nov 24 19:59 callbackcontext.cpython-312.pyc
-rw-r--r-- 1 root root 18252 Nov 24 19:59 callbackdatacache.cpython-312.pyc
-rw-r--r-- 1 root root 10972 Nov 24 19:59 callbackqueryhandler.cpython-312.pyc
-rw-r--r-- 1 root root  6653 Nov 24 19:59 chatmemberhandler.cpython-312.pyc
-rw-r--r-- 1 root root  7244 Nov 24 19:59 choseninlineresulthandler.cpython-312.pyc
-rw-r--r-- 1 root root 21927 Nov 24 19:59 commandhandler.cpython-312.pyc
-rw-r--r-- 1 root root  7398 Nov 24 19:59 contexttypes.cpython-312.pyc
-rw-r--r-- 1 root root 33813 Nov 24 19:59 conversationhandler.cpython-312.pyc
-rw-r--r-- 1 root root 10937 Nov 24 19:59 defaults.cpython-312.pyc
-rw-r--r-- 1 root root 18051 Nov 24 19:59 dictpersistence.cpython-312.pyc
-rw-r--r-- 1 root root 36875 Nov 24 19:59 dispatcher.cpython-312.pyc
-rw-r--r-- 1 root root 11479 Nov 24 19:59 extbot.cpython-312.pyc
-rw-r--r-- 1 root root 98997 Nov 24 19:59 filters.cpython-312.pyc
-rw-r--r-- 1 root root 11134 Nov 24 19:59 handler.cpython-312.pyc
-rw-r--r-- 1 root root  9918 Nov 24 19:59 inlinequeryhandler.cpython-312.pyc
-rw-r--r-- 1 root root 32238 Nov 24 19:59 jobqueue.cpython-312.pyc
-rw-r--r-- 1 root root  9668 Nov 24 19:59 messagehandler.cpython-312.pyc
-rw-r--r-- 1 root root 15373 Nov 24 19:59 messagequeue.cpython-312.pyc
-rw-r--r-- 1 root root 21425 Nov 24 19:59 picklepersistence.cpython-312.pyc
-rw-r--r-- 1 root root  4629 Nov 24 19:59 pollanswerhandler.cpython-312.pyc
-rw-r--r-- 1 root root  4591 Nov 24 19:59 pollhandler.cpython-312.pyc
-rw-r--r-- 1 root root  4654 Nov 24 19:59 precheckoutqueryhandler.cpython-312.pyc
-rw-r--r-- 1 root root  7617 Nov 24 19:59 regexhandler.cpython-312.pyc
-rw-r--r-- 1 root root  4635 Nov 24 19:59 shippingqueryhandler.cpython-312.pyc
-rw-r--r-- 1 root root  6636 Nov 24 19:59 stringcommandhandler.cpython-312.pyc
-rw-r--r-- 1 root root  7316 Nov 24 19:59 stringregexhandler.cpython-312.pyc
-rw-r--r-- 1 root root  4599 Nov 24 19:59 typehandler.cpython-312.pyc
-rw-r--r-- 1 root root 35231 Nov 24 19:59 updater.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/utils:
total 28
-rw-r--r-- 1 root root  800 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 5804 Nov 24 19:59 promise.py
-rw-r--r-- 1 root root 1905 Nov 24 19:59 types.py
-rw-r--r-- 1 root root 6101 Nov 24 19:59 webhookhandler.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/ext/utils/__pycache__:
total 28
-rw-r--r-- 1 root root  178 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 6778 Nov 24 19:59 promise.cpython-312.pyc
-rw-r--r-- 1 root root  899 Nov 24 19:59 types.cpython-312.pyc
-rw-r--r-- 1 root root 8933 Nov 24 19:59 webhookhandler.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files:
total 128
-rw-r--r-- 1 root root     0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root  5198 Nov 24 19:59 animation.py
-rw-r--r-- 1 root root  5397 Nov 24 19:59 audio.py
-rw-r--r-- 1 root root  5179 Nov 24 19:59 chatphoto.py
-rw-r--r-- 1 root root  2540 Nov 24 19:59 contact.py
-rw-r--r-- 1 root root  4486 Nov 24 19:59 document.py
-rw-r--r-- 1 root root  8343 Nov 24 19:59 file.py
-rw-r--r-- 1 root root  4251 Nov 24 19:59 inputfile.py
-rw-r--r-- 1 root root 22605 Nov 24 19:59 inputmedia.py
-rw-r--r-- 1 root root  3831 Nov 24 19:59 location.py
-rw-r--r-- 1 root root  3626 Nov 24 19:59 photosize.py
-rw-r--r-- 1 root root 10869 Nov 24 19:59 sticker.py
-rw-r--r-- 1 root root  3970 Nov 24 19:59 venue.py
-rw-r--r-- 1 root root  5076 Nov 24 19:59 video.py
-rw-r--r-- 1 root root  4497 Nov 24 19:59 videonote.py
-rw-r--r-- 1 root root  3858 Nov 24 19:59 voice.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/files/__pycache__:
total 128
-rw-r--r-- 1 root root   174 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  5167 Nov 24 19:59 animation.cpython-312.pyc
-rw-r--r-- 1 root root  5325 Nov 24 19:59 audio.cpython-312.pyc
-rw-r--r-- 1 root root  4946 Nov 24 19:59 chatphoto.cpython-312.pyc
-rw-r--r-- 1 root root  2145 Nov 24 19:59 contact.cpython-312.pyc
-rw-r--r-- 1 root root  4440 Nov 24 19:59 document.cpython-312.pyc
-rw-r--r-- 1 root root  9235 Nov 24 19:59 file.cpython-312.pyc
-rw-r--r-- 1 root root  4839 Nov 24 19:59 inputfile.cpython-312.pyc
-rw-r--r-- 1 root root 22652 Nov 24 19:59 inputmedia.cpython-312.pyc
-rw-r--r-- 1 root root  3314 Nov 24 19:59 location.cpython-312.pyc
-rw-r--r-- 1 root root  3516 Nov 24 19:59 photosize.cpython-312.pyc
-rw-r--r-- 1 root root 11745 Nov 24 19:59 sticker.cpython-312.pyc
-rw-r--r-- 1 root root  3639 Nov 24 19:59 venue.cpython-312.pyc
-rw-r--r-- 1 root root  5049 Nov 24 19:59 video.cpython-312.pyc
-rw-r--r-- 1 root root  4509 Nov 24 19:59 videonote.cpython-312.pyc
-rw-r--r-- 1 root root  3636 Nov 24 19:59 voice.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/games:
total 20
-rw-r--r-- 1 root root    0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 1074 Nov 24 19:59 callbackgame.py
-rw-r--r-- 1 root root 7698 Nov 24 19:59 game.py
-rw-r--r-- 1 root root 2320 Nov 24 19:59 gamehighscore.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/games/__pycache__:
total 24
-rw-r--r-- 1 root root  174 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  618 Nov 24 19:59 callbackgame.cpython-312.pyc
-rw-r--r-- 1 root root 8762 Nov 24 19:59 game.cpython-312.pyc
-rw-r--r-- 1 root root 2252 Nov 24 19:59 gamehighscore.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline:
total 212
-rw-r--r-- 1 root root     0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root  7533 Nov 24 19:59 inlinekeyboardbutton.py
-rw-r--r-- 1 root root  4862 Nov 24 19:59 inlinekeyboardmarkup.py
-rw-r--r-- 1 root root  6662 Nov 24 19:59 inlinequery.py
-rw-r--r-- 1 root root  2449 Nov 24 19:59 inlinequeryresult.py
-rw-r--r-- 1 root root  3996 Nov 24 19:59 inlinequeryresultarticle.py
-rw-r--r-- 1 root root  5037 Nov 24 19:59 inlinequeryresultaudio.py
-rw-r--r-- 1 root root  4545 Nov 24 19:59 inlinequeryresultcachedaudio.py
-rw-r--r-- 1 root root  5085 Nov 24 19:59 inlinequeryresultcacheddocument.py
-rw-r--r-- 1 root root  4856 Nov 24 19:59 inlinequeryresultcachedgif.py
-rw-r--r-- 1 root root  4918 Nov 24 19:59 inlinequeryresultcachedmpeg4gif.py
-rw-r--r-- 1 root root  5076 Nov 24 19:59 inlinequeryresultcachedphoto.py
-rw-r--r-- 1 root root  2915 Nov 24 19:59 inlinequeryresultcachedsticker.py
-rw-r--r-- 1 root root  5054 Nov 24 19:59 inlinequeryresultcachedvideo.py
-rw-r--r-- 1 root root  4738 Nov 24 19:59 inlinequeryresultcachedvoice.py
-rw-r--r-- 1 root root  4272 Nov 24 19:59 inlinequeryresultcontact.py
-rw-r--r-- 1 root root  6083 Nov 24 19:59 inlinequeryresultdocument.py
-rw-r--r-- 1 root root  2201 Nov 24 19:59 inlinequeryresultgame.py
-rw-r--r-- 1 root root  6189 Nov 24 19:59 inlinequeryresultgif.py
-rw-r--r-- 1 root root  5749 Nov 24 19:59 inlinequeryresultlocation.py
-rw-r--r-- 1 root root  6226 Nov 24 19:59 inlinequeryresultmpeg4gif.py
-rw-r--r-- 1 root root  5864 Nov 24 19:59 inlinequeryresultphoto.py
-rw-r--r-- 1 root root  5638 Nov 24 19:59 inlinequeryresultvenue.py
-rw-r--r-- 1 root root  6674 Nov 24 19:59 inlinequeryresultvideo.py
-rw-r--r-- 1 root root  4961 Nov 24 19:59 inlinequeryresultvoice.py
-rw-r--r-- 1 root root  2454 Nov 24 19:59 inputcontactmessagecontent.py
-rw-r--r-- 1 root root 11009 Nov 24 19:59 inputinvoicemessagecontent.py
-rw-r--r-- 1 root root  3863 Nov 24 19:59 inputlocationmessagecontent.py
-rw-r--r-- 1 root root  1332 Nov 24 19:59 inputmessagecontent.py
-rw-r--r-- 1 root root  3882 Nov 24 19:59 inputtextmessagecontent.py
-rw-r--r-- 1 root root  3981 Nov 24 19:59 inputvenuemessagecontent.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/inline/__pycache__:
total 208
-rw-r--r-- 1 root root   175 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  7216 Nov 24 19:59 inlinekeyboardbutton.cpython-312.pyc
-rw-r--r-- 1 root root  5786 Nov 24 19:59 inlinekeyboardmarkup.cpython-312.pyc
-rw-r--r-- 1 root root  6332 Nov 24 19:59 inlinequery.cpython-312.pyc
-rw-r--r-- 1 root root  2264 Nov 24 19:59 inlinequeryresult.cpython-312.pyc
-rw-r--r-- 1 root root  3499 Nov 24 19:59 inlinequeryresultarticle.cpython-312.pyc
-rw-r--r-- 1 root root  4575 Nov 24 19:59 inlinequeryresultaudio.cpython-312.pyc
-rw-r--r-- 1 root root  4140 Nov 24 19:59 inlinequeryresultcachedaudio.cpython-312.pyc
-rw-r--r-- 1 root root  4622 Nov 24 19:59 inlinequeryresultcacheddocument.cpython-312.pyc
-rw-r--r-- 1 root root  4445 Nov 24 19:59 inlinequeryresultcachedgif.cpython-312.pyc
-rw-r--r-- 1 root root  4511 Nov 24 19:59 inlinequeryresultcachedmpeg4gif.cpython-312.pyc
-rw-r--r-- 1 root root  4614 Nov 24 19:59 inlinequeryresultcachedphoto.cpython-312.pyc
-rw-r--r-- 1 root root  2530 Nov 24 19:59 inlinequeryresultcachedsticker.cpython-312.pyc
-rw-r--r-- 1 root root  4618 Nov 24 19:59 inlinequeryresultcachedvideo.cpython-312.pyc
-rw-r--r-- 1 root root  4327 Nov 24 19:59 inlinequeryresultcachedvoice.cpython-312.pyc
-rw-r--r-- 1 root root  3743 Nov 24 19:59 inlinequeryresultcontact.cpython-312.pyc
-rw-r--r-- 1 root root  5558 Nov 24 19:59 inlinequeryresultdocument.cpython-312.pyc
-rw-r--r-- 1 root root  1845 Nov 24 19:59 inlinequeryresultgame.cpython-312.pyc
-rw-r--r-- 1 root root  5631 Nov 24 19:59 inlinequeryresultgif.cpython-312.pyc
-rw-r--r-- 1 root root  5156 Nov 24 19:59 inlinequeryresultlocation.cpython-312.pyc
-rw-r--r-- 1 root root  5681 Nov 24 19:59 inlinequeryresultmpeg4gif.cpython-312.pyc
-rw-r--r-- 1 root root  5355 Nov 24 19:59 inlinequeryresultphoto.cpython-312.pyc
-rw-r--r-- 1 root root  4986 Nov 24 19:59 inlinequeryresultvenue.cpython-312.pyc
-rw-r--r-- 1 root root  6119 Nov 24 19:59 inlinequeryresultvideo.cpython-312.pyc
-rw-r--r-- 1 root root  4520 Nov 24 19:59 inlinequeryresultvoice.cpython-312.pyc
-rw-r--r-- 1 root root  2071 Nov 24 19:59 inputcontactmessagecontent.cpython-312.pyc
-rw-r--r-- 1 root root 10653 Nov 24 19:59 inputinvoicemessagecontent.cpython-312.pyc
-rw-r--r-- 1 root root  3363 Nov 24 19:59 inputlocationmessagecontent.cpython-312.pyc
-rw-r--r-- 1 root root   891 Nov 24 19:59 inputmessagecontent.cpython-312.pyc
-rw-r--r-- 1 root root  3785 Nov 24 19:59 inputtextmessagecontent.cpython-312.pyc
-rw-r--r-- 1 root root  3420 Nov 24 19:59 inputvenuemessagecontent.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport:
total 76
-rw-r--r-- 1 root root     0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 19374 Nov 24 19:59 credentials.py
-rw-r--r-- 1 root root  4692 Nov 24 19:59 data.py
-rw-r--r-- 1 root root 12172 Nov 24 19:59 encryptedpassportelement.py
-rw-r--r-- 1 root root  4938 Nov 24 19:59 passportdata.py
-rw-r--r-- 1 root root 16267 Nov 24 19:59 passportelementerrors.py
-rw-r--r-- 1 root root  5601 Nov 24 19:59 passportfile.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/passport/__pycache__:
total 88
-rw-r--r-- 1 root root   177 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 21551 Nov 24 19:59 credentials.cpython-312.pyc
-rw-r--r-- 1 root root  4239 Nov 24 19:59 data.cpython-312.pyc
-rw-r--r-- 1 root root 12387 Nov 24 19:59 encryptedpassportelement.cpython-312.pyc
-rw-r--r-- 1 root root  5474 Nov 24 19:59 passportdata.cpython-312.pyc
-rw-r--r-- 1 root root 18517 Nov 24 19:59 passportelementerrors.cpython-312.pyc
-rw-r--r-- 1 root root  5628 Nov 24 19:59 passportfile.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment:
total 48
-rw-r--r-- 1 root root    0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 3166 Nov 24 19:59 invoice.py
-rw-r--r-- 1 root root 2182 Nov 24 19:59 labeledprice.py
-rw-r--r-- 1 root root 2881 Nov 24 19:59 orderinfo.py
-rw-r--r-- 1 root root 5229 Nov 24 19:59 precheckoutquery.py
-rw-r--r-- 1 root root 2858 Nov 24 19:59 shippingaddress.py
-rw-r--r-- 1 root root 2330 Nov 24 19:59 shippingoption.py
-rw-r--r-- 1 root root 4118 Nov 24 19:59 shippingquery.py
-rw-r--r-- 1 root root 4400 Nov 24 19:59 successfulpayment.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/payment/__pycache__:
total 40
-rw-r--r-- 1 root root  176 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 2695 Nov 24 19:59 invoice.cpython-312.pyc
-rw-r--r-- 1 root root 1906 Nov 24 19:59 labeledprice.cpython-312.pyc
-rw-r--r-- 1 root root 2766 Nov 24 19:59 orderinfo.cpython-312.pyc
-rw-r--r-- 1 root root 5085 Nov 24 19:59 precheckoutquery.cpython-312.pyc
-rw-r--r-- 1 root root 2405 Nov 24 19:59 shippingaddress.cpython-312.pyc
-rw-r--r-- 1 root root 2233 Nov 24 19:59 shippingoption.cpython-312.pyc
-rw-r--r-- 1 root root 4055 Nov 24 19:59 shippingquery.cpython-312.pyc
-rw-r--r-- 1 root root 4006 Nov 24 19:59 successfulpayment.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils:
total 60
-rw-r--r-- 1 root root     0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root  2029 Nov 24 19:59 deprecate.py
-rw-r--r-- 1 root root 20674 Nov 24 19:59 helpers.py
-rw-r--r-- 1 root root  1350 Nov 24 19:59 promise.py
-rw-r--r-- 1 root root 15475 Nov 24 19:59 request.py
-rw-r--r-- 1 root root  2114 Nov 24 19:59 types.py
-rw-r--r-- 1 root root  1383 Nov 24 19:59 webhookhandler.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/utils/__pycache__:
total 60
-rw-r--r-- 1 root root   174 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  1397 Nov 24 19:59 deprecate.cpython-312.pyc
-rw-r--r-- 1 root root 23698 Nov 24 19:59 helpers.cpython-312.pyc
-rw-r--r-- 1 root root   676 Nov 24 19:59 promise.cpython-312.pyc
-rw-r--r-- 1 root root 15839 Nov 24 19:59 request.cpython-312.pyc
-rw-r--r-- 1 root root   999 Nov 24 19:59 types.cpython-312.pyc
-rw-r--r-- 1 root root   850 Nov 24 19:59 webhookhandler.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor:
total 8
-rw-r--r-- 1 root root    0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
drwxr-xr-x 4 root root 4096 Nov 24 19:59 ptb_urllib3

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/__pycache__:
total 4
-rw-r--r-- 1 root root 175 Nov 24 19:59 __init__.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3:
total 8
-rw-r--r-- 1 root root    0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
drwxr-xr-x 6 root root 4096 Nov 24 19:59 urllib3

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/__pycache__:
total 4
-rw-r--r-- 1 root root 187 Nov 24 19:59 __init__.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3:
total 152
-rw-r--r-- 1 root root  2851 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 10638 Nov 24 19:59 _collections.py
-rw-r--r-- 1 root root 12709 Nov 24 19:59 connection.py
-rw-r--r-- 1 root root 35475 Nov 24 19:59 connectionpool.py
drwxr-xr-x 3 root root  4096 Nov 24 19:59 contrib
-rw-r--r-- 1 root root  6603 Nov 24 19:59 exceptions.py
-rw-r--r-- 1 root root  5943 Nov 24 19:59 fields.py
-rw-r--r-- 1 root root  2321 Nov 24 19:59 filepost.py
drwxr-xr-x 5 root root  4096 Nov 24 19:59 packages
-rw-r--r-- 1 root root 13053 Nov 24 19:59 poolmanager.py
-rw-r--r-- 1 root root  5946 Nov 24 19:59 request.py
-rw-r--r-- 1 root root 22662 Nov 24 19:59 response.py
drwxr-xr-x 3 root root  4096 Nov 24 19:59 util

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/__pycache__:
total 148
-rw-r--r-- 1 root root  3342 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 15788 Nov 24 19:59 _collections.cpython-312.pyc
-rw-r--r-- 1 root root 13154 Nov 24 19:59 connection.cpython-312.pyc
-rw-r--r-- 1 root root 33161 Nov 24 19:59 connectionpool.cpython-312.pyc
-rw-r--r-- 1 root root 11491 Nov 24 19:59 exceptions.cpython-312.pyc
-rw-r--r-- 1 root root  7551 Nov 24 19:59 fields.cpython-312.pyc
-rw-r--r-- 1 root root  3810 Nov 24 19:59 filepost.cpython-312.pyc
-rw-r--r-- 1 root root 14830 Nov 24 19:59 poolmanager.cpython-312.pyc
-rw-r--r-- 1 root root  6348 Nov 24 19:59 request.cpython-312.pyc
-rw-r--r-- 1 root root 24602 Nov 24 19:59 response.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib:
total 48
-rw-r--r-- 1 root root     0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 10865 Nov 24 19:59 appengine.py
-rw-r--r-- 1 root root  4478 Nov 24 19:59 ntlmpool.py
-rw-r--r-- 1 root root 15139 Nov 24 19:59 pyopenssl.py
-rw-r--r-- 1 root root  6391 Nov 24 19:59 socks.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/contrib/__pycache__:
total 60
-rw-r--r-- 1 root root   203 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 12360 Nov 24 19:59 appengine.cpython-312.pyc
-rw-r--r-- 1 root root  5360 Nov 24 19:59 ntlmpool.cpython-312.pyc
-rw-r--r-- 1 root root 21637 Nov 24 19:59 pyopenssl.cpython-312.pyc
-rw-r--r-- 1 root root  6858 Nov 24 19:59 socks.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages:
total 60
-rw-r--r-- 1 root root   109 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
drwxr-xr-x 3 root root  4096 Nov 24 19:59 backports
-rw-r--r-- 1 root root  8935 Nov 24 19:59 ordered_dict.py
-rw-r--r-- 1 root root 30098 Nov 24 19:59 six.py
drwxr-xr-x 3 root root  4096 Nov 24 19:59 ssl_match_hostname

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/__pycache__:
total 52
-rw-r--r-- 1 root root   324 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 10914 Nov 24 19:59 ordered_dict.cpython-312.pyc
-rw-r--r-- 1 root root 36557 Nov 24 19:59 six.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/backports:
total 8
-rw-r--r-- 1 root root    0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 1461 Nov 24 19:59 makefile.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/backports/__pycache__:
total 8
-rw-r--r-- 1 root root  214 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 1862 Nov 24 19:59 makefile.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/ssl_match_hostname:  
total 16
-rw-r--r-- 1 root root  688 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 5702 Nov 24 19:59 _implementation.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/packages/ssl_match_hostname/__pycache__:
total 12
-rw-r--r-- 1 root root  723 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 5115 Nov 24 19:59 _implementation.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util:
total 96
-rw-r--r-- 1 root root   994 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root  4237 Nov 24 19:59 connection.py
-rw-r--r-- 1 root root  3704 Nov 24 19:59 request.py
-rw-r--r-- 1 root root  2343 Nov 24 19:59 response.py
-rw-r--r-- 1 root root 14123 Nov 24 19:59 retry.py
-rw-r--r-- 1 root root 18929 Nov 24 19:59 selectors.py
-rw-r--r-- 1 root root 12046 Nov 24 19:59 ssl_.py
-rw-r--r-- 1 root root  9757 Nov 24 19:59 timeout.py
-rw-r--r-- 1 root root  6289 Nov 24 19:59 url.py
-rw-r--r-- 1 root root  1451 Nov 24 19:59 wait.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/telegram/vendor/ptb_urllib3/urllib3/util/__pycache__:
total 96
-rw-r--r-- 1 root root  1002 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  4298 Nov 24 19:59 connection.cpython-312.pyc
-rw-r--r-- 1 root root  4069 Nov 24 19:59 request.cpython-312.pyc
-rw-r--r-- 1 root root  2519 Nov 24 19:59 response.cpython-312.pyc
-rw-r--r-- 1 root root 15539 Nov 24 19:59 retry.cpython-312.pyc
-rw-r--r-- 1 root root 23865 Nov 24 19:59 selectors.cpython-312.pyc
-rw-r--r-- 1 root root 11441 Nov 24 19:59 ssl_.cpython-312.pyc
-rw-r--r-- 1 root root 10761 Nov 24 19:59 timeout.cpython-312.pyc
-rw-r--r-- 1 root root  6800 Nov 24 19:59 url.cpython-312.pyc
-rw-r--r-- 1 root root  2020 Nov 24 19:59 wait.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado:
total 944
-rw-r--r-- 1 root root   1018 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root   4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root   4627 Nov 24 19:59 _locale_data.py
-rw-r--r-- 1 root root  46051 Nov 24 19:59 auth.py
-rw-r--r-- 1 root root  13652 Nov 24 19:59 autoreload.py
-rw-r--r-- 1 root root   8108 Nov 24 19:59 concurrent.py
-rw-r--r-- 1 root root  24575 Nov 24 19:59 curl_httpclient.py
-rw-r--r-- 1 root root  13267 Nov 24 19:59 escape.py
-rw-r--r-- 1 root root  30957 Nov 24 19:59 gen.py
-rw-r--r-- 1 root root  36098 Nov 24 19:59 http1connection.py
-rw-r--r-- 1 root root  31919 Nov 24 19:59 httpclient.py
-rw-r--r-- 1 root root  15555 Nov 24 19:59 httpserver.py
-rw-r--r-- 1 root root  35933 Nov 24 19:59 httputil.py
-rw-r--r-- 1 root root  35342 Nov 24 19:59 ioloop.py
-rw-r--r-- 1 root root  65451 Nov 24 19:59 iostream.py
-rw-r--r-- 1 root root  20972 Nov 24 19:59 locale.py
-rw-r--r-- 1 root root  17414 Nov 24 19:59 locks.py
-rw-r--r-- 1 root root  12414 Nov 24 19:59 log.py
-rw-r--r-- 1 root root  22912 Nov 24 19:59 netutil.py
-rw-r--r-- 1 root root  25601 Nov 24 19:59 options.py
drwxr-xr-x 3 root root   4096 Nov 24 19:59 platform
-rw-r--r-- 1 root root  12789 Nov 24 19:59 process.py
-rw-r--r-- 1 root root      0 Nov 24 19:59 py.typed
-rw-r--r-- 1 root root  12289 Nov 24 19:59 queues.py
-rw-r--r-- 1 root root  25082 Nov 24 19:59 routing.py
-rw-r--r-- 1 root root  27578 Nov 24 19:59 simple_httpclient.py
-rwxr-xr-x 1 root root  25360 Nov 24 19:59 speedups.cpython-312-x86_64-linux-gnu.so
-rw-r--r-- 1 root root  12076 Nov 24 19:59 tcpclient.py
-rw-r--r-- 1 root root  13242 Nov 24 19:59 tcpserver.py
-rw-r--r-- 1 root root  37798 Nov 24 19:59 template.py
drwxr-xr-x 7 root root   4096 Nov 24 19:59 test
-rw-r--r-- 1 root root  30623 Nov 24 19:59 testing.py
-rw-r--r-- 1 root root  16702 Nov 24 19:59 util.py
-rw-r--r-- 1 root root 138140 Nov 24 19:59 web.py
-rw-r--r-- 1 root root  61476 Nov 24 19:59 websocket.py
-rw-r--r-- 1 root root   7807 Nov 24 19:59 wsgi.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/__pycache__:
total 1028
-rw-r--r-- 1 root root    287 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root   4023 Nov 24 19:59 _locale_data.cpython-312.pyc
-rw-r--r-- 1 root root  53229 Nov 24 19:59 auth.cpython-312.pyc
-rw-r--r-- 1 root root  11999 Nov 24 19:59 autoreload.cpython-312.pyc
-rw-r--r-- 1 root root  10072 Nov 24 19:59 concurrent.cpython-312.pyc
-rw-r--r-- 1 root root  27632 Nov 24 19:59 curl_httpclient.cpython-312.pyc
-rw-r--r-- 1 root root  15394 Nov 24 19:59 escape.cpython-312.pyc
-rw-r--r-- 1 root root  34161 Nov 24 19:59 gen.cpython-312.pyc
-rw-r--r-- 1 root root  39533 Nov 24 19:59 http1connection.cpython-312.pyc
-rw-r--r-- 1 root root  35143 Nov 24 19:59 httpclient.cpython-312.pyc
-rw-r--r-- 1 root root  18307 Nov 24 19:59 httpserver.cpython-312.pyc
-rw-r--r-- 1 root root  44665 Nov 24 19:59 httputil.cpython-312.pyc
-rw-r--r-- 1 root root  38413 Nov 24 19:59 ioloop.cpython-312.pyc
-rw-r--r-- 1 root root  68592 Nov 24 19:59 iostream.cpython-312.pyc
-rw-r--r-- 1 root root  23615 Nov 24 19:59 locale.cpython-312.pyc
-rw-r--r-- 1 root root  23508 Nov 24 19:59 locks.cpython-312.pyc
-rw-r--r-- 1 root root  12529 Nov 24 19:59 log.cpython-312.pyc
-rw-r--r-- 1 root root  24680 Nov 24 19:59 netutil.cpython-312.pyc
-rw-r--r-- 1 root root  32525 Nov 24 19:59 options.cpython-312.pyc
-rw-r--r-- 1 root root  14884 Nov 24 19:59 process.cpython-312.pyc
-rw-r--r-- 1 root root  17885 Nov 24 19:59 queues.cpython-312.pyc
-rw-r--r-- 1 root root  31756 Nov 24 19:59 routing.cpython-312.pyc
-rw-r--r-- 1 root root  34312 Nov 24 19:59 simple_httpclient.cpython-312.pyc
-rw-r--r-- 1 root root  14370 Nov 24 19:59 tcpclient.cpython-312.pyc
-rw-r--r-- 1 root root  13848 Nov 24 19:59 tcpserver.cpython-312.pyc
-rw-r--r-- 1 root root  49406 Nov 24 19:59 template.cpython-312.pyc
-rw-r--r-- 1 root root  35215 Nov 24 19:59 testing.cpython-312.pyc
-rw-r--r-- 1 root root  18994 Nov 24 19:59 util.cpython-312.pyc
-rw-r--r-- 1 root root 160279 Nov 24 19:59 web.cpython-312.pyc
-rw-r--r-- 1 root root  74642 Nov 24 19:59 websocket.cpython-312.pyc
-rw-r--r-- 1 root root   9441 Nov 24 19:59 wsgi.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/platform:
total 40
-rw-r--r-- 1 root root     0 Nov 24 19:59 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root 23216 Nov 24 19:59 asyncio.py
-rw-r--r-- 1 root root  3318 Nov 24 19:59 caresresolver.py
-rw-r--r-- 1 root root  5477 Nov 24 19:59 twisted.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/platform/__pycache__:
total 48
-rw-r--r-- 1 root root   176 Nov 24 19:59 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 27058 Nov 24 19:59 asyncio.cpython-312.pyc
-rw-r--r-- 1 root root  4866 Nov 24 19:59 caresresolver.cpython-312.pyc
-rw-r--r-- 1 root root  6692 Nov 24 19:59 twisted.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test:
total 724
-rw-r--r-- 1 root root    335 Nov 24 19:59 __main__.py
drwxr-xr-x 2 root root   4096 Nov 24 19:59 __pycache__
-rw-r--r-- 1 root root   7155 Nov 24 19:59 asyncio_test.py
-rw-r--r-- 1 root root  23437 Nov 24 19:59 auth_test.py
-rw-r--r-- 1 root root   3948 Nov 24 19:59 autoreload_test.py
-rw-r--r-- 1 root root   6051 Nov 24 19:59 concurrent_test.py
drwxr-xr-x 2 root root   4096 Nov 24 19:59 csv_translations
-rw-r--r-- 1 root root   4303 Nov 24 19:59 curl_httpclient_test.py
-rw-r--r-- 1 root root  12372 Nov 24 19:59 escape_test.py
-rw-r--r-- 1 root root  33838 Nov 24 19:59 gen_test.py
drwxr-xr-x 3 root root   4096 Nov 24 19:59 gettext_translations
-rw-r--r-- 1 root root   1950 Nov 24 19:59 http1connection_test.py
-rw-r--r-- 1 root root  34231 Nov 24 19:59 httpclient_test.py
-rw-r--r-- 1 root root  46492 Nov 24 19:59 httpserver_test.py
-rw-r--r-- 1 root root  19053 Nov 24 19:59 httputil_test.py
-rw-r--r-- 1 root root   1980 Nov 24 19:59 import_test.py
-rw-r--r-- 1 root root  25653 Nov 24 19:59 ioloop_test.py
-rw-r--r-- 1 root root  46328 Nov 24 19:59 iostream_test.py
-rw-r--r-- 1 root root   5756 Nov 24 19:59 locale_test.py
-rw-r--r-- 1 root root  17010 Nov 24 19:59 locks_test.py
-rw-r--r-- 1 root root   9504 Nov 24 19:59 log_test.py
-rw-r--r-- 1 root root   7907 Nov 24 19:59 netutil_test.py
-rw-r--r-- 1 root root     69 Nov 24 19:59 options_test.cfg
-rw-r--r-- 1 root root  11821 Nov 24 19:59 options_test.py
-rw-r--r-- 1 root root    266 Nov 24 19:59 options_test_types.cfg
-rw-r--r-- 1 root root    150 Nov 24 19:59 options_test_types_str.cfg
-rw-r--r-- 1 root root  11455 Nov 24 19:59 process_test.py
-rw-r--r-- 1 root root  13981 Nov 24 19:59 queues_test.py
-rw-r--r-- 1 root root    411 Nov 24 19:59 resolve_test_helper.py
-rw-r--r-- 1 root root   8827 Nov 24 19:59 routing_test.py
-rw-r--r-- 1 root root   8348 Nov 24 19:59 runtests.py
-rw-r--r-- 1 root root  30943 Nov 24 19:59 simple_httpclient_test.py
drwxr-xr-x 3 root root   4096 Nov 24 19:59 static
-rw-r--r-- 1 root root     95 Nov 24 19:59 static_foo.txt
-rw-r--r-- 1 root root  16814 Nov 24 19:59 tcpclient_test.py
-rw-r--r-- 1 root root   6482 Nov 24 19:59 tcpserver_test.py
-rw-r--r-- 1 root root  18668 Nov 24 19:59 template_test.py
drwxr-xr-x 2 root root   4096 Nov 24 19:59 templates
-rw-r--r-- 1 root root   1224 Nov 24 19:59 test.crt
-rw-r--r-- 1 root root   1704 Nov 24 19:59 test.key
-rw-r--r-- 1 root root  10711 Nov 24 19:59 testing_test.py
-rw-r--r-- 1 root root   8510 Nov 24 19:59 twisted_test.py
-rw-r--r-- 1 root root   3654 Nov 24 19:59 util.py
-rw-r--r-- 1 root root   9781 Nov 24 19:59 util_test.py
-rw-r--r-- 1 root root 115864 Nov 24 19:59 web_test.py
-rw-r--r-- 1 root root  27976 Nov 24 19:59 websocket_test.py
-rw-r--r-- 1 root root    657 Nov 24 19:59 wsgi_test.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/__pycache__:
total 1084
-rw-r--r-- 1 root root    362 Nov 24 19:59 __main__.cpython-312.pyc
-rw-r--r-- 1 root root  10753 Nov 24 19:59 asyncio_test.cpython-312.pyc
-rw-r--r-- 1 root root  32707 Nov 24 19:59 auth_test.cpython-312.pyc
-rw-r--r-- 1 root root   5460 Nov 24 19:59 autoreload_test.cpython-312.pyc
-rw-r--r-- 1 root root  12533 Nov 24 19:59 concurrent_test.cpython-312.pyc
-rw-r--r-- 1 root root   7058 Nov 24 19:59 curl_httpclient_test.cpython-312.pyc
-rw-r--r-- 1 root root  12573 Nov 24 19:59 escape_test.cpython-312.pyc
-rw-r--r-- 1 root root  65419 Nov 24 19:59 gen_test.cpython-312.pyc
-rw-r--r-- 1 root root   4272 Nov 24 19:59 http1connection_test.cpython-312.pyc
-rw-r--r-- 1 root root  50193 Nov 24 19:59 httpclient_test.cpython-312.pyc
-rw-r--r-- 1 root root  85807 Nov 24 19:59 httpserver_test.cpython-312.pyc
-rw-r--r-- 1 root root  25769 Nov 24 19:59 httputil_test.cpython-312.pyc
-rw-r--r-- 1 root root   2577 Nov 24 19:59 import_test.cpython-312.pyc
-rw-r--r-- 1 root root  45803 Nov 24 19:59 ioloop_test.cpython-312.pyc
-rw-r--r-- 1 root root  77412 Nov 24 19:59 iostream_test.cpython-312.pyc
-rw-r--r-- 1 root root  10726 Nov 24 19:59 locale_test.cpython-312.pyc
-rw-r--r-- 1 root root  34450 Nov 24 19:59 locks_test.cpython-312.pyc
-rw-r--r-- 1 root root  15126 Nov 24 19:59 log_test.cpython-312.pyc
-rw-r--r-- 1 root root  13579 Nov 24 19:59 netutil_test.cpython-312.pyc
-rw-r--r-- 1 root root  19653 Nov 24 19:59 options_test.cpython-312.pyc
-rw-r--r-- 1 root root  14845 Nov 24 19:59 process_test.cpython-312.pyc
-rw-r--r-- 1 root root  27957 Nov 24 19:59 queues_test.cpython-312.pyc
-rw-r--r-- 1 root root    599 Nov 24 19:59 resolve_test_helper.cpython-312.pyc
-rw-r--r-- 1 root root  15226 Nov 24 19:59 routing_test.cpython-312.pyc
-rw-r--r-- 1 root root  10702 Nov 24 19:59 runtests.cpython-312.pyc
-rw-r--r-- 1 root root  59999 Nov 24 19:59 simple_httpclient_test.cpython-312.pyc
-rw-r--r-- 1 root root  30019 Nov 24 19:59 tcpclient_test.cpython-312.pyc
-rw-r--r-- 1 root root  10162 Nov 24 19:59 tcpserver_test.cpython-312.pyc
-rw-r--r-- 1 root root  28451 Nov 24 19:59 template_test.cpython-312.pyc
-rw-r--r-- 1 root root  22667 Nov 24 19:59 testing_test.cpython-312.pyc
-rw-r--r-- 1 root root  12972 Nov 24 19:59 twisted_test.cpython-312.pyc
-rw-r--r-- 1 root root   4624 Nov 24 19:59 util.cpython-312.pyc
-rw-r--r-- 1 root root  18039 Nov 24 19:59 util_test.cpython-312.pyc
-rw-r--r-- 1 root root 193261 Nov 24 19:59 web_test.cpython-312.pyc
-rw-r--r-- 1 root root  51269 Nov 24 19:59 websocket_test.cpython-312.pyc
-rw-r--r-- 1 root root   1331 Nov 24 19:59 wsgi_test.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/csv_translations:
total 4
-rw-r--r-- 1 root root 18 Nov 24 19:59 fr_FR.csv

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/gettext_translations:
total 4
drwxr-xr-x 3 root root 4096 Nov 24 19:59 fr_FR

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/gettext_translations/fr_FR:
total 4
drwxr-xr-x 2 root root 4096 Nov 24 19:59 LC_MESSAGES

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/gettext_translations/fr_FR/LC_MESSAGES:
total 8
-rw-r--r-- 1 root root  665 Nov 24 19:59 tornado_test.mo
-rw-r--r-- 1 root root 1049 Nov 24 19:59 tornado_test.po

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/static:
total 20
drwxr-xr-x 2 root root 4096 Nov 24 19:59 dir
-rw-r--r-- 1 root root   26 Nov 24 19:59 robots.txt
-rw-r--r-- 1 root root  666 Nov 24 19:59 sample.xml
-rw-r--r-- 1 root root  285 Nov 24 19:59 sample.xml.bz2
-rw-r--r-- 1 root root  264 Nov 24 19:59 sample.xml.gz

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/static/dir:
total 4
-rw-r--r-- 1 root root 18 Nov 24 19:59 index.html

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado/test/templates:
total 4
-rw-r--r-- 1 root root 7 Nov 24 19:59 utf8.html

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tornado-6.1.dist-info:
total 40
-rw-r--r-- 1 root root     4 Nov 24 19:59 INSTALLER
-rw-r--r-- 1 root root 11358 Nov 24 19:59 LICENSE
-rw-r--r-- 1 root root  2437 Nov 24 19:59 METADATA
-rw-r--r-- 1 root root 11774 Nov 24 19:59 RECORD
-rw-r--r-- 1 root root     0 Nov 24 19:59 REQUESTED
-rw-r--r-- 1 root root   104 Nov 24 19:59 WHEEL
-rw-r--r-- 1 root root     8 Nov 24 19:59 top_level.txt

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal:
total 64
-rw-r--r-- 1 root root   396 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root     0 Nov 24 19:58 py.typed
-rw-r--r-- 1 root root  8168 Nov 24 19:58 unix.py
-rw-r--r-- 1 root root  3329 Nov 24 19:58 utils.py
-rw-r--r-- 1 root root  4772 Nov 24 19:58 win32.py
-rw-r--r-- 1 root root 35165 Nov 24 19:58 windows_tz.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal/__pycache__:
total 64
-rw-r--r-- 1 root root   505 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  9124 Nov 24 19:58 unix.cpython-312.pyc
-rw-r--r-- 1 root root  4454 Nov 24 19:58 utils.cpython-312.pyc
-rw-r--r-- 1 root root  4852 Nov 24 19:58 win32.cpython-312.pyc
-rw-r--r-- 1 root root 30015 Nov 24 19:58 windows_tz.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/tzlocal-5.2.dist-info:
total 28
-rw-r--r-- 1 root root    4 Nov 24 19:58 INSTALLER
-rw-r--r-- 1 root root 1060 Nov 24 19:58 LICENSE.txt
-rw-r--r-- 1 root root 7791 Nov 24 19:58 METADATA
-rw-r--r-- 1 root root 1150 Nov 24 19:58 RECORD
-rw-r--r-- 1 root root   92 Nov 24 19:58 WHEEL
-rw-r--r-- 1 root root    8 Nov 24 19:58 top_level.txt

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3:
total 184
-rw-r--r-- 1 root root  3333 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root 11372 Nov 24 19:58 _collections.py
-rw-r--r-- 1 root root    64 Nov 24 19:58 _version.py
-rw-r--r-- 1 root root 20300 Nov 24 19:58 connection.py
-rw-r--r-- 1 root root 40285 Nov 24 19:58 connectionpool.py
drwxr-xr-x 4 root root  4096 Nov 24 19:58 contrib
-rw-r--r-- 1 root root  8217 Nov 24 19:58 exceptions.py
-rw-r--r-- 1 root root  8579 Nov 24 19:58 fields.py
-rw-r--r-- 1 root root  2440 Nov 24 19:58 filepost.py
drwxr-xr-x 4 root root  4096 Nov 24 19:58 packages
-rw-r--r-- 1 root root 19990 Nov 24 19:58 poolmanager.py
-rw-r--r-- 1 root root  6691 Nov 24 19:58 request.py
-rw-r--r-- 1 root root 30761 Nov 24 19:58 response.py
drwxr-xr-x 3 root root  4096 Nov 24 19:58 util

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/__pycache__:
total 176
-rw-r--r-- 1 root root  3382 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 16341 Nov 24 19:58 _collections.cpython-312.pyc
-rw-r--r-- 1 root root   195 Nov 24 19:58 _version.cpython-312.pyc
-rw-r--r-- 1 root root 20380 Nov 24 19:58 connection.cpython-312.pyc
-rw-r--r-- 1 root root 36414 Nov 24 19:58 connectionpool.cpython-312.pyc
-rw-r--r-- 1 root root 13470 Nov 24 19:58 exceptions.cpython-312.pyc
-rw-r--r-- 1 root root 10379 Nov 24 19:58 fields.cpython-312.pyc
-rw-r--r-- 1 root root  3989 Nov 24 19:58 filepost.cpython-312.pyc
-rw-r--r-- 1 root root 20406 Nov 24 19:58 poolmanager.cpython-312.pyc
-rw-r--r-- 1 root root  7271 Nov 24 19:58 request.cpython-312.pyc
-rw-r--r-- 1 root root 34100 Nov 24 19:58 response.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/contrib:
total 96
-rw-r--r-- 1 root root     0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root   957 Nov 24 19:58 _appengine_environ.py
drwxr-xr-x 3 root root  4096 Nov 24 19:58 _securetransport
-rw-r--r-- 1 root root 11012 Nov 24 19:58 appengine.py
-rw-r--r-- 1 root root  4528 Nov 24 19:58 ntlmpool.py
-rw-r--r-- 1 root root 17055 Nov 24 19:58 pyopenssl.py
-rw-r--r-- 1 root root 34431 Nov 24 19:58 securetransport.py
-rw-r--r-- 1 root root  7097 Nov 24 19:58 socks.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/contrib/__pycache__:
total 96
-rw-r--r-- 1 root root   175 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  1825 Nov 24 19:58 _appengine_environ.cpython-312.pyc
-rw-r--r-- 1 root root 11517 Nov 24 19:58 appengine.cpython-312.pyc
-rw-r--r-- 1 root root  5691 Nov 24 19:58 ntlmpool.cpython-312.pyc
-rw-r--r-- 1 root root 24392 Nov 24 19:58 pyopenssl.cpython-312.pyc
-rw-r--r-- 1 root root 35463 Nov 24 19:58 securetransport.cpython-312.pyc
-rw-r--r-- 1 root root  7488 Nov 24 19:58 socks.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/contrib/_securetransport:
total 40
-rw-r--r-- 1 root root     0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root 17632 Nov 24 19:58 bindings.py
-rw-r--r-- 1 root root 13922 Nov 24 19:58 low_level.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/contrib/_securetransport/__pycache__:
total 40
-rw-r--r-- 1 root root   192 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 17404 Nov 24 19:58 bindings.cpython-312.pyc
-rw-r--r-- 1 root root 14740 Nov 24 19:58 low_level.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/packages:
total 44
-rw-r--r-- 1 root root     0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
drwxr-xr-x 3 root root  4096 Nov 24 19:58 backports
-rw-r--r-- 1 root root 34665 Nov 24 19:58 six.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/packages/__pycache__:
total 48
-rw-r--r-- 1 root root   176 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 41232 Nov 24 19:58 six.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/packages/backports:
total 16
-rw-r--r-- 1 root root    0 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root 4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root 1417 Nov 24 19:58 makefile.py
-rw-r--r-- 1 root root 5343 Nov 24 19:58 weakref_finalize.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/packages/backports/__pycache__:
total 16
-rw-r--r-- 1 root root  186 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root 1802 Nov 24 19:58 makefile.cpython-312.pyc
-rw-r--r-- 1 root root 7313 Nov 24 19:58 weakref_finalize.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/util:
total 132
-rw-r--r-- 1 root root  1155 Nov 24 19:58 __init__.py
drwxr-xr-x 2 root root  4096 Nov 24 19:58 __pycache__
-rw-r--r-- 1 root root  4901 Nov 24 19:58 connection.py
-rw-r--r-- 1 root root  1605 Nov 24 19:58 proxy.py
-rw-r--r-- 1 root root   498 Nov 24 19:58 queue.py
-rw-r--r-- 1 root root  4225 Nov 24 19:58 request.py
-rw-r--r-- 1 root root  3510 Nov 24 19:58 response.py
-rw-r--r-- 1 root root 22013 Nov 24 19:58 retry.py
-rw-r--r-- 1 root root 17165 Nov 24 19:58 ssl_.py
-rw-r--r-- 1 root root  5758 Nov 24 19:58 ssl_match_hostname.py
-rw-r--r-- 1 root root  6895 Nov 24 19:58 ssltransport.py
-rw-r--r-- 1 root root 10168 Nov 24 19:58 timeout.py
-rw-r--r-- 1 root root 14279 Nov 24 19:58 url.py
-rw-r--r-- 1 root root  5403 Nov 24 19:58 wait.py

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3/util/__pycache__:
total 128
-rw-r--r-- 1 root root  1123 Nov 24 19:58 __init__.cpython-312.pyc
-rw-r--r-- 1 root root  4724 Nov 24 19:58 connection.cpython-312.pyc
-rw-r--r-- 1 root root  1529 Nov 24 19:58 proxy.cpython-312.pyc
-rw-r--r-- 1 root root  1329 Nov 24 19:58 queue.cpython-312.pyc
-rw-r--r-- 1 root root  4399 Nov 24 19:58 request.cpython-312.pyc
-rw-r--r-- 1 root root  2969 Nov 24 19:58 response.cpython-312.pyc
-rw-r--r-- 1 root root 21678 Nov 24 19:58 retry.cpython-312.pyc
-rw-r--r-- 1 root root 15049 Nov 24 19:58 ssl_.cpython-312.pyc
-rw-r--r-- 1 root root  5028 Nov 24 19:58 ssl_match_hostname.cpython-312.pyc
-rw-r--r-- 1 root root 10730 Nov 24 19:58 ssltransport.cpython-312.pyc
-rw-r--r-- 1 root root 11116 Nov 24 19:58 timeout.cpython-312.pyc
-rw-r--r-- 1 root root 15738 Nov 24 19:58 url.cpython-312.pyc
-rw-r--r-- 1 root root  4380 Nov 24 19:58 wait.cpython-312.pyc

/opt/KiTraderBot/venv/lib/python3.12/site-packages/urllib3-1.26.18.dist-info:
total 72
-rw-r--r-- 1 root root     4 Nov 24 19:58 INSTALLER
-rw-r--r-- 1 root root  1115 Nov 24 19:58 LICENSE.txt
-rw-r--r-- 1 root root 48910 Nov 24 19:58 METADATA
-rw-r--r-- 1 root root  6054 Nov 24 19:58 RECORD
-rw-r--r-- 1 root root     0 Nov 24 19:58 REQUESTED
-rw-r--r-- 1 root root   110 Nov 24 19:58 WHEEL
-rw-r--r-- 1 root root     8 Nov 24 19:58 top_level.txt


                               List of roles
    Role name    |                         Attributes
-----------------+------------------------------------------------------------
 fantasysol_user | Create DB
 kitrader        | Superuser, Create role, Create DB
 kitraderbot     |
 postgres        | Superuser, Create role, Create DB, Replication, Bypass RLS]
```

### Database Users
```
[Database user list will go here]
```

## 7. Backup Configuration
### Database Backups
```
[Backup configuration and status will go here]
```

## 8. Network Configuration
### Active Connections
```
[Network status information will go here]
```

## 9. Summary Report
[ GNU nano 8.1                                  system_analysis_report.txt
=== KiTraderBot System Analysis Report ===
Date: Thu Nov 28 00:51:36 UTC 2024

=== PostgreSQL Version ===
psql (PostgreSQL) 16.4 (Ubuntu 16.4-1build1)

=== Database Tables ===
                                              List of relations
 Schema |        Name         |   Type   |  Owner   | Persistence | Access method |    Size    | Description
--------+---------------------+----------+----------+-------------+---------------+------------+-------------        
 public | trades              | table    | postgres | permanent   | heap          | 0 bytes    |
 public | trades_trade_id_seq | sequence | postgres | permanent   |               | 8192 bytes |
 public | user_settings       | table    | postgres | permanent   | heap          | 8192 bytes |
 public | users               | table    | postgres | permanent   | heap          | 0 bytes    |
 public | users_user_id_seq   | sequence | postgres | permanent   |               | 8192 bytes |
(5 rows)
]

## 10. Identified Issues
[Any issues or concerns found during analysis will go here]

## 11. Recommendations
[Recommendations for implementation based on findings will go here]

