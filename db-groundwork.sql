--
-- PostgreSQL database dump
--

-- Dumped from database version 13.0
-- Dumped by pg_dump version 13.0

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
-- Name: auth_group; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.auth_group (
    id integer NOT NULL,
    name character varying(150) NOT NULL
);


ALTER TABLE public.auth_group OWNER TO core;

--
-- Name: auth_group_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.auth_group_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_id_seq OWNER TO core;

--
-- Name: auth_group_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.auth_group_id_seq OWNED BY public.auth_group.id;


--
-- Name: auth_group_permissions; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.auth_group_permissions (
    id bigint NOT NULL,
    group_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_group_permissions OWNER TO core;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.auth_group_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_group_permissions_id_seq OWNER TO core;

--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.auth_group_permissions_id_seq OWNED BY public.auth_group_permissions.id;


--
-- Name: auth_permission; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.auth_permission (
    id integer NOT NULL,
    name character varying(255) NOT NULL,
    content_type_id integer NOT NULL,
    codename character varying(100) NOT NULL
);


ALTER TABLE public.auth_permission OWNER TO core;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.auth_permission_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_permission_id_seq OWNER TO core;

--
-- Name: auth_permission_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.auth_permission_id_seq OWNED BY public.auth_permission.id;


--
-- Name: auth_user; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.auth_user (
    id integer NOT NULL,
    password character varying(128) NOT NULL,
    last_login timestamp with time zone,
    is_superuser boolean NOT NULL,
    username character varying(150) NOT NULL,
    first_name character varying(150) NOT NULL,
    last_name character varying(150) NOT NULL,
    email character varying(254) NOT NULL,
    is_staff boolean NOT NULL,
    is_active boolean NOT NULL,
    date_joined timestamp with time zone NOT NULL
);


ALTER TABLE public.auth_user OWNER TO core;

--
-- Name: auth_user_groups; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.auth_user_groups (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    group_id integer NOT NULL
);


ALTER TABLE public.auth_user_groups OWNER TO core;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.auth_user_groups_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_groups_id_seq OWNER TO core;

--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.auth_user_groups_id_seq OWNED BY public.auth_user_groups.id;


--
-- Name: auth_user_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.auth_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_id_seq OWNER TO core;

--
-- Name: auth_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.auth_user_id_seq OWNED BY public.auth_user.id;


--
-- Name: auth_user_user_permissions; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.auth_user_user_permissions (
    id bigint NOT NULL,
    user_id integer NOT NULL,
    permission_id integer NOT NULL
);


ALTER TABLE public.auth_user_user_permissions OWNER TO core;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.auth_user_user_permissions_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.auth_user_user_permissions_id_seq OWNER TO core;

--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.auth_user_user_permissions_id_seq OWNED BY public.auth_user_user_permissions.id;


--
-- Name: django_admin_log; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.django_admin_log (
    id integer NOT NULL,
    action_time timestamp with time zone NOT NULL,
    object_id text,
    object_repr character varying(200) NOT NULL,
    action_flag smallint NOT NULL,
    change_message text NOT NULL,
    content_type_id integer,
    user_id integer NOT NULL,
    CONSTRAINT django_admin_log_action_flag_check CHECK ((action_flag >= 0))
);


ALTER TABLE public.django_admin_log OWNER TO core;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.django_admin_log_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_admin_log_id_seq OWNER TO core;

--
-- Name: django_admin_log_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.django_admin_log_id_seq OWNED BY public.django_admin_log.id;


--
-- Name: django_content_type; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.django_content_type (
    id integer NOT NULL,
    app_label character varying(100) NOT NULL,
    model character varying(100) NOT NULL
);


ALTER TABLE public.django_content_type OWNER TO core;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.django_content_type_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_content_type_id_seq OWNER TO core;

--
-- Name: django_content_type_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.django_content_type_id_seq OWNED BY public.django_content_type.id;


--
-- Name: django_migrations; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.django_migrations (
    id bigint NOT NULL,
    app character varying(255) NOT NULL,
    name character varying(255) NOT NULL,
    applied timestamp with time zone NOT NULL
);


ALTER TABLE public.django_migrations OWNER TO core;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.django_migrations_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.django_migrations_id_seq OWNER TO core;

--
-- Name: django_migrations_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.django_migrations_id_seq OWNED BY public.django_migrations.id;


--
-- Name: django_session; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.django_session (
    session_key character varying(40) NOT NULL,
    session_data text NOT NULL,
    expire_date timestamp with time zone NOT NULL
);


ALTER TABLE public.django_session OWNER TO core;

--
-- Name: pipelines_dataset; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.pipelines_dataset (
    id bigint NOT NULL,
    base_pipeline_name character varying(80) NOT NULL,
    short_pipe character varying(50) NOT NULL,
    description character varying(2000) NOT NULL,
    short character varying(50) NOT NULL,
    base_pipe_name_wo character varying(50) NOT NULL,
    pub_date timestamp with time zone NOT NULL
);


ALTER TABLE public.pipelines_dataset OWNER TO core;

--
-- Name: pipelines_dataset_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.pipelines_dataset_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pipelines_dataset_id_seq OWNER TO core;

--
-- Name: pipelines_dataset_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.pipelines_dataset_id_seq OWNED BY public.pipelines_dataset.id;


--
-- Name: pipelines_datasetpipelines; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.pipelines_datasetpipelines (
    id bigint NOT NULL,
    pipeline_name character varying(80) NOT NULL,
    short_description character varying(200) NOT NULL,
    description character varying(2000) NOT NULL,
    target_destination character varying(50) NOT NULL,
    dataset_id bigint NOT NULL
);


ALTER TABLE public.pipelines_datasetpipelines OWNER TO core;

--
-- Name: pipelines_datasetpipelines_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.pipelines_datasetpipelines_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pipelines_datasetpipelines_id_seq OWNER TO core;

--
-- Name: pipelines_datasetpipelines_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.pipelines_datasetpipelines_id_seq OWNED BY public.pipelines_datasetpipelines.id;


--
-- Name: pipelines_pipeline; Type: TABLE; Schema: public; Owner: core
--

CREATE TABLE public.pipelines_pipeline (
    id bigint NOT NULL,
    pipeline_name character varying(50) NOT NULL,
    base_pipeline character varying(50) NOT NULL,
    description text NOT NULL,
    short character varying(50) NOT NULL,
    pub_date timestamp with time zone NOT NULL,
    sorting_id character varying(20) NOT NULL
);


ALTER TABLE public.pipelines_pipeline OWNER TO core;

--
-- Name: pipelines_pipeline_id_seq; Type: SEQUENCE; Schema: public; Owner: core
--

CREATE SEQUENCE public.pipelines_pipeline_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.pipelines_pipeline_id_seq OWNER TO core;

--
-- Name: pipelines_pipeline_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: core
--

ALTER SEQUENCE public.pipelines_pipeline_id_seq OWNED BY public.pipelines_pipeline.id;


--
-- Name: auth_group id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group ALTER COLUMN id SET DEFAULT nextval('public.auth_group_id_seq'::regclass);


--
-- Name: auth_group_permissions id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_group_permissions_id_seq'::regclass);


--
-- Name: auth_permission id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_permission ALTER COLUMN id SET DEFAULT nextval('public.auth_permission_id_seq'::regclass);


--
-- Name: auth_user id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user ALTER COLUMN id SET DEFAULT nextval('public.auth_user_id_seq'::regclass);


--
-- Name: auth_user_groups id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_groups ALTER COLUMN id SET DEFAULT nextval('public.auth_user_groups_id_seq'::regclass);


--
-- Name: auth_user_user_permissions id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_user_permissions ALTER COLUMN id SET DEFAULT nextval('public.auth_user_user_permissions_id_seq'::regclass);


--
-- Name: django_admin_log id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_admin_log ALTER COLUMN id SET DEFAULT nextval('public.django_admin_log_id_seq'::regclass);


--
-- Name: django_content_type id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_content_type ALTER COLUMN id SET DEFAULT nextval('public.django_content_type_id_seq'::regclass);


--
-- Name: django_migrations id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_migrations ALTER COLUMN id SET DEFAULT nextval('public.django_migrations_id_seq'::regclass);


--
-- Name: pipelines_dataset id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_dataset ALTER COLUMN id SET DEFAULT nextval('public.pipelines_dataset_id_seq'::regclass);


--
-- Name: pipelines_datasetpipelines id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_datasetpipelines ALTER COLUMN id SET DEFAULT nextval('public.pipelines_datasetpipelines_id_seq'::regclass);


--
-- Name: pipelines_pipeline id; Type: DEFAULT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_pipeline ALTER COLUMN id SET DEFAULT nextval('public.pipelines_pipeline_id_seq'::regclass);


--
-- Data for Name: auth_group; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.auth_group (id, name) FROM stdin;
\.


--
-- Data for Name: auth_group_permissions; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.auth_group_permissions (id, group_id, permission_id) FROM stdin;
\.


--
-- Data for Name: auth_permission; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.auth_permission (id, name, content_type_id, codename) FROM stdin;
1	Can add log entry	1	add_logentry
2	Can change log entry	1	change_logentry
3	Can delete log entry	1	delete_logentry
4	Can view log entry	1	view_logentry
5	Can add permission	2	add_permission
6	Can change permission	2	change_permission
7	Can delete permission	2	delete_permission
8	Can view permission	2	view_permission
9	Can add group	3	add_group
10	Can change group	3	change_group
11	Can delete group	3	delete_group
12	Can view group	3	view_group
13	Can add user	4	add_user
14	Can change user	4	change_user
15	Can delete user	4	delete_user
16	Can view user	4	view_user
17	Can add content type	5	add_contenttype
18	Can change content type	5	change_contenttype
19	Can delete content type	5	delete_contenttype
20	Can view content type	5	view_contenttype
21	Can add session	6	add_session
22	Can change session	6	change_session
23	Can delete session	6	delete_session
24	Can view session	6	view_session
25	Can add dataset	7	add_dataset
26	Can change dataset	7	change_dataset
27	Can delete dataset	7	delete_dataset
28	Can view dataset	7	view_dataset
29	Can add pipeline	8	add_pipeline
30	Can change pipeline	8	change_pipeline
31	Can delete pipeline	8	delete_pipeline
32	Can view pipeline	8	view_pipeline
33	Can add dataset pipelines	9	add_datasetpipelines
34	Can change dataset pipelines	9	change_datasetpipelines
35	Can delete dataset pipelines	9	delete_datasetpipelines
36	Can view dataset pipelines	9	view_datasetpipelines
\.


--
-- Data for Name: auth_user; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.auth_user (id, password, last_login, is_superuser, username, first_name, last_name, email, is_staff, is_active, date_joined) FROM stdin;
1	pbkdf2_sha256$260000$k1I4rtFJmHnBbAIhp4jHel$V+OJ+0GbTgtC0nkv78C3Vec3BczGikiT5yLWGmFWYGM=	2021-11-09 17:10:41.360745+00	t	admin				t	t	2021-11-03 21:37:59.830178+00
\.


--
-- Data for Name: auth_user_groups; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.auth_user_groups (id, user_id, group_id) FROM stdin;
\.


--
-- Data for Name: auth_user_user_permissions; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.auth_user_user_permissions (id, user_id, permission_id) FROM stdin;
\.


--
-- Data for Name: django_admin_log; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.django_admin_log (id, action_time, object_id, object_repr, action_flag, change_message, content_type_id, user_id) FROM stdin;
1	2021-11-03 21:38:22.429918+00	1	atacseq	1	[{"added": {}}]	7	1
2	2021-11-03 21:38:39.621641+00	2	chipseq	1	[{"added": {}}]	7	1
3	2021-11-03 21:41:50.388083+00	3	rnaseq	1	[{"added": {}}]	7	1
4	2021-11-03 21:42:01.791163+00	4	sarek	1	[{"added": {}}]	7	1
5	2021-11-03 21:42:27.257052+00	1	RNA-Seq	1	[{"added": {}}]	8	1
6	2021-11-03 21:43:05.099873+00	2	Sarek	1	[{"added": {}}]	8	1
7	2021-11-03 21:43:23.181605+00	3	ChIP-Seq	1	[{"added": {}}]	8	1
8	2021-11-03 21:43:38.654851+00	4	ATAC-Seq	1	[{"added": {}}]	8	1
9	2021-11-03 21:44:26.512542+00	6	Post-ChIP-Seq	1	[{"added": {}}]	8	1
10	2021-11-03 21:44:49.573332+00	7	Post-ATAC-Seq	1	[{"added": {}}]	8	1
11	2021-11-03 21:45:03.441729+00	8	Post-RNA-Seq	1	[{"added": {}}]	8	1
12	2021-11-03 21:45:54.534453+00	1	Post-ATAC-Seq	1	[{"added": {}}]	9	1
13	2021-11-03 21:46:22.627976+00	2	Post-ChIP-Seq	1	[{"added": {}}]	9	1
14	2021-11-03 21:47:04.596863+00	3	Post-RNA-Seq	1	[{"added": {}}]	9	1
15	2021-11-09 17:11:25.518692+00	9	Test pipeline	1	[{"added": {}}]	8	1
16	2021-11-09 17:12:13.410347+00	9	Test pipeline	3		8	1
17	2021-11-16 14:10:24.770704+00	8	Post-RNA-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
18	2021-11-16 14:10:34.26606+00	7	Post-ATAC-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
19	2021-11-16 14:10:38.562509+00	6	Post-ChIP-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
20	2021-11-16 14:10:55.980012+00	1	RNA-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
21	2021-11-16 14:11:10.390777+00	6	Post-ChIP-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
22	2021-11-16 14:11:30.242777+00	4	ATAC-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
23	2021-11-16 14:11:38.211189+00	3	ChIP-Seq	2	[{"changed": {"fields": ["Description"]}}]	8	1
24	2021-11-16 14:11:48.791582+00	2	Sarek	2	[{"changed": {"fields": ["Description"]}}]	8	1
\.


--
-- Data for Name: django_content_type; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.django_content_type (id, app_label, model) FROM stdin;
1	admin	logentry
2	auth	permission
3	auth	group
4	auth	user
5	contenttypes	contenttype
6	sessions	session
7	pipelines	dataset
8	pipelines	pipeline
9	pipelines	datasetpipelines
\.


--
-- Data for Name: django_migrations; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.django_migrations (id, app, name, applied) FROM stdin;
1	contenttypes	0001_initial	2021-11-03 21:37:33.450297+00
2	auth	0001_initial	2021-11-03 21:37:33.490292+00
3	admin	0001_initial	2021-11-03 21:37:33.503904+00
4	admin	0002_logentry_remove_auto_add	2021-11-03 21:37:33.508909+00
5	admin	0003_logentry_add_action_flag_choices	2021-11-03 21:37:33.514365+00
6	contenttypes	0002_remove_content_type_name	2021-11-03 21:37:33.525688+00
7	auth	0002_alter_permission_name_max_length	2021-11-03 21:37:33.531678+00
8	auth	0003_alter_user_email_max_length	2021-11-03 21:37:33.537313+00
9	auth	0004_alter_user_username_opts	2021-11-03 21:37:33.542294+00
10	auth	0005_alter_user_last_login_null	2021-11-03 21:37:33.548694+00
11	auth	0006_require_contenttypes_0002	2021-11-03 21:37:33.550647+00
12	auth	0007_alter_validators_add_error_messages	2021-11-03 21:37:33.55646+00
13	auth	0008_alter_user_username_max_length	2021-11-03 21:37:33.563862+00
14	auth	0009_alter_user_last_name_max_length	2021-11-03 21:37:33.570265+00
15	auth	0010_alter_group_name_max_length	2021-11-03 21:37:33.576228+00
16	auth	0011_update_proxy_permissions	2021-11-03 21:37:33.581145+00
17	auth	0012_alter_user_first_name_max_length	2021-11-03 21:37:33.589469+00
18	pipelines	0001_initial	2021-11-03 21:37:33.603955+00
19	sessions	0001_initial	2021-11-03 21:37:33.610565+00
\.


--
-- Data for Name: django_session; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.django_session (session_key, session_data, expire_date) FROM stdin;
58ca7crybk663hrf6g8y5cb3ccjs2i8l	.eJxVjDkOwjAUBe_iGlnxEsdQ0ucM1t-MA8iR4qRC3B0ipYD2zcx7qQTbWtLWZEkTq4sy6vS7IdBD6g74DvU2a5rrukyod0UftOlxZnleD_fvoEAr33rwOVoXsnBEyuiHzBIpspzBOYMUPVoMnbAxHqHvwBrB3kGwBAJW1PsDEq05PQ:1miNxM:CMFyh5Kv8iiLWFJmIojLq0teFggANXTpIReTrmjfnrw	2021-11-17 21:38:04.548183+00
ot0mgcz9bomrr7cl47otj55n1dqm8my3	.eJxVjDkOwjAUBe_iGlnxEsdQ0ucM1t-MA8iR4qRC3B0ipYD2zcx7qQTbWtLWZEkTq4sy6vS7IdBD6g74DvU2a5rrukyod0UftOlxZnleD_fvoEAr33rwOVoXsnBEyuiHzBIpspzBOYMUPVoMnbAxHqHvwBrB3kGwBAJW1PsDEq05PQ:1mkUdt:gph3HkFdTELU8l1ms0r27z8eSlWi09kkX66hZl8k5b4	2021-11-23 17:10:41.363072+00
\.


--
-- Data for Name: pipelines_dataset; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.pipelines_dataset (id, base_pipeline_name, short_pipe, description, short, base_pipe_name_wo, pub_date) FROM stdin;
1	atacseq	atacseq	Data from nf-core's ATAC-Seq peak-calling pipeline	ATAC-Seq data	ATAC-Seq	2021-11-03 21:38:22.429226+00
2	chipseq	chipseq	Data from nf-core's ChIP-Seq peak-calling pipeline	ChIP-Seq data	ChIP-Seq	2021-11-03 21:38:39.618988+00
3	rnaseq	rnaseq	Data from nf-core's RNA sequencing analysis pipeline	RNA-Seq data	RNA-Seq	2021-11-03 21:41:50.387295+00
4	sarek	sarek	Data from nf-core's Sarek analysis pipeline	Sarek data	Sarek	2021-11-03 21:42:01.790616+00
\.


--
-- Data for Name: pipelines_datasetpipelines; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.pipelines_datasetpipelines (id, pipeline_name, short_description, description, target_destination, dataset_id) FROM stdin;
1	Post-ATAC-Seq	Visualization pipeline for ATAC-Seq output	Visualization pipeline for ATAC-Seq output	postacs	1
2	Post-ChIP-Seq	Visualization pipeline for ChIP-Seq output	Visualization pipeline for ChIP-Seq output	postacs	2
3	Post-RNA-Seq	Analysis pipeline for RNA-Seq output.	Analysis pipeline for RNA-Seq output.	postrna	3
\.


--
-- Data for Name: pipelines_pipeline; Type: TABLE DATA; Schema: public; Owner: core
--

COPY public.pipelines_pipeline (id, pipeline_name, base_pipeline, description, short, pub_date, sorting_id) FROM stdin;
7	Post-RNA-Seq	RNA-Seq	Analysis pipeline for further analisation of the results of nfcore's RNA-Seq pipeline. It performs functional enrichment analysis running g:Profiler and extracts all maximal connected sub-networks of a biological network using KeyPathwayMiner.	postrna	2021-11-03 21:45:03.440989+00	2
6	Post-ATAC-Seq	ATAC-Seq	Pipeline for further analysis of the results of nf-core's ATAC-Seq pipeline. It visualizes the results of the pipeline in form of normalized bigWig files.	postacs	2021-11-03 21:44:49.570258+00	4
1	RNA-Seq	nf-core base	nf-core's RNA-Seq analysis pipeline. It can be used to analyse RNA sequencing data obtained from organisms with a reference genome and annotation. It utilizes STAR with Salmon or RSEM, or HISAT2 for alignment of the RNA-seq data and for quantification of gene expression. Quality control is done through RSeQC, Qualimap, dupRadar, Preseq and DESeq2.	nfcore/rnaseq	2021-11-03 21:42:27.256191+00	1
5	Post-ChIP-Seq	ChIP-Seq	Pipeline for further analysis of the results of nf-core's ChIP-Seq pipeline. It visualizes the results of the pipeline in form of normalized bigWig files.	postacs	2021-11-03 21:44:26.512046+00	6
4	ATAC-Seq	nf-core base	nf-core's ATAC-seq pipeline, used for ATAC-seq data. It uses tools like deepTools for genome-wide enrichment, MACS2 for peak-calling and DESeq2 for differential analysis.	nfcore/atacseq	2021-11-03 21:43:38.652263+00	3
3	ChIP-Seq	nf-core base	nf-core's ChIP-Seq pipeline for Chromatin ImmunopreciPitation sequencing (ChIP-Seq) data. It uses tools like deepTools for genome-wide enrichment, MACS2 for peak-calling and DESeq2 for differential analysis.	nfcore/chipseq	2021-11-03 21:43:23.1788+00	5
2	Sarek	nf-core base	nf-core's Sarek pipeline, used to detect variants on whole genome or targeted sequencing data. It is designed for Human or mouse, but can work with data of any species with a reference genome. It uses tools like BWA mem to map Reads to Reference, GATK BaseRecalibrator for Quality Score Recalibration and Qualimap and bamqc for quality control	nfcore/sarek	2021-11-03 21:43:05.096455+00	7
\.


--
-- Name: auth_group_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.auth_group_id_seq', 1, false);


--
-- Name: auth_group_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.auth_group_permissions_id_seq', 1, false);


--
-- Name: auth_permission_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.auth_permission_id_seq', 36, true);


--
-- Name: auth_user_groups_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.auth_user_groups_id_seq', 1, false);


--
-- Name: auth_user_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.auth_user_id_seq', 1, true);


--
-- Name: auth_user_user_permissions_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.auth_user_user_permissions_id_seq', 1, false);


--
-- Name: django_admin_log_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.django_admin_log_id_seq', 26, true);


--
-- Name: django_content_type_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.django_content_type_id_seq', 9, true);


--
-- Name: django_migrations_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.django_migrations_id_seq', 19, true);


--
-- Name: pipelines_dataset_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.pipelines_dataset_id_seq', 4, true);


--
-- Name: pipelines_datasetpipelines_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.pipelines_datasetpipelines_id_seq', 3, true);


--
-- Name: pipelines_pipeline_id_seq; Type: SEQUENCE SET; Schema: public; Owner: core
--

SELECT pg_catalog.setval('public.pipelines_pipeline_id_seq', 9, true);


--
-- Name: auth_group auth_group_name_key; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_name_key UNIQUE (name);


--
-- Name: auth_group_permissions auth_group_permissions_group_id_permission_id_0cd325b0_uniq; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_permission_id_0cd325b0_uniq UNIQUE (group_id, permission_id);


--
-- Name: auth_group_permissions auth_group_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_group auth_group_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group
    ADD CONSTRAINT auth_group_pkey PRIMARY KEY (id);


--
-- Name: auth_permission auth_permission_content_type_id_codename_01ab375a_uniq; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_codename_01ab375a_uniq UNIQUE (content_type_id, codename);


--
-- Name: auth_permission auth_permission_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_pkey PRIMARY KEY (id);


--
-- Name: auth_user_groups auth_user_groups_user_id_group_id_94350c0c_uniq; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_group_id_94350c0c_uniq UNIQUE (user_id, group_id);


--
-- Name: auth_user auth_user_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_pkey PRIMARY KEY (id);


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_permission_id_14a6b632_uniq; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_permission_id_14a6b632_uniq UNIQUE (user_id, permission_id);


--
-- Name: auth_user auth_user_username_key; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user
    ADD CONSTRAINT auth_user_username_key UNIQUE (username);


--
-- Name: django_admin_log django_admin_log_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_pkey PRIMARY KEY (id);


--
-- Name: django_content_type django_content_type_app_label_model_76bd3d3b_uniq; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_app_label_model_76bd3d3b_uniq UNIQUE (app_label, model);


--
-- Name: django_content_type django_content_type_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_content_type
    ADD CONSTRAINT django_content_type_pkey PRIMARY KEY (id);


--
-- Name: django_migrations django_migrations_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_migrations
    ADD CONSTRAINT django_migrations_pkey PRIMARY KEY (id);


--
-- Name: django_session django_session_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_session
    ADD CONSTRAINT django_session_pkey PRIMARY KEY (session_key);


--
-- Name: pipelines_dataset pipelines_dataset_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_dataset
    ADD CONSTRAINT pipelines_dataset_pkey PRIMARY KEY (id);


--
-- Name: pipelines_datasetpipelines pipelines_datasetpipelines_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_datasetpipelines
    ADD CONSTRAINT pipelines_datasetpipelines_pkey PRIMARY KEY (id);


--
-- Name: pipelines_pipeline pipelines_pipeline_pkey; Type: CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_pipeline
    ADD CONSTRAINT pipelines_pipeline_pkey PRIMARY KEY (id);


--
-- Name: auth_group_name_a6ea08ec_like; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_group_name_a6ea08ec_like ON public.auth_group USING btree (name varchar_pattern_ops);


--
-- Name: auth_group_permissions_group_id_b120cbf9; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_group_permissions_group_id_b120cbf9 ON public.auth_group_permissions USING btree (group_id);


--
-- Name: auth_group_permissions_permission_id_84c5c92e; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_group_permissions_permission_id_84c5c92e ON public.auth_group_permissions USING btree (permission_id);


--
-- Name: auth_permission_content_type_id_2f476e4b; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_permission_content_type_id_2f476e4b ON public.auth_permission USING btree (content_type_id);


--
-- Name: auth_user_groups_group_id_97559544; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_user_groups_group_id_97559544 ON public.auth_user_groups USING btree (group_id);


--
-- Name: auth_user_groups_user_id_6a12ed8b; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_user_groups_user_id_6a12ed8b ON public.auth_user_groups USING btree (user_id);


--
-- Name: auth_user_user_permissions_permission_id_1fbb5f2c; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_user_user_permissions_permission_id_1fbb5f2c ON public.auth_user_user_permissions USING btree (permission_id);


--
-- Name: auth_user_user_permissions_user_id_a95ead1b; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_user_user_permissions_user_id_a95ead1b ON public.auth_user_user_permissions USING btree (user_id);


--
-- Name: auth_user_username_6821ab7c_like; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX auth_user_username_6821ab7c_like ON public.auth_user USING btree (username varchar_pattern_ops);


--
-- Name: django_admin_log_content_type_id_c4bce8eb; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX django_admin_log_content_type_id_c4bce8eb ON public.django_admin_log USING btree (content_type_id);


--
-- Name: django_admin_log_user_id_c564eba6; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX django_admin_log_user_id_c564eba6 ON public.django_admin_log USING btree (user_id);


--
-- Name: django_session_expire_date_a5c62663; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX django_session_expire_date_a5c62663 ON public.django_session USING btree (expire_date);


--
-- Name: django_session_session_key_c0390e0f_like; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX django_session_session_key_c0390e0f_like ON public.django_session USING btree (session_key varchar_pattern_ops);


--
-- Name: pipelines_datasetpipelines_dataset_id_29626196; Type: INDEX; Schema: public; Owner: core
--

CREATE INDEX pipelines_datasetpipelines_dataset_id_29626196 ON public.pipelines_datasetpipelines USING btree (dataset_id);


--
-- Name: auth_group_permissions auth_group_permissio_permission_id_84c5c92e_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissio_permission_id_84c5c92e_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_group_permissions auth_group_permissions_group_id_b120cbf9_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_group_permissions
    ADD CONSTRAINT auth_group_permissions_group_id_b120cbf9_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_permission auth_permission_content_type_id_2f476e4b_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_permission
    ADD CONSTRAINT auth_permission_content_type_id_2f476e4b_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_group_id_97559544_fk_auth_group_id; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_group_id_97559544_fk_auth_group_id FOREIGN KEY (group_id) REFERENCES public.auth_group(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_groups auth_user_groups_user_id_6a12ed8b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_groups
    ADD CONSTRAINT auth_user_groups_user_id_6a12ed8b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm FOREIGN KEY (permission_id) REFERENCES public.auth_permission(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: auth_user_user_permissions auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.auth_user_user_permissions
    ADD CONSTRAINT auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_content_type_id_c4bce8eb_fk_django_co; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_content_type_id_c4bce8eb_fk_django_co FOREIGN KEY (content_type_id) REFERENCES public.django_content_type(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: django_admin_log django_admin_log_user_id_c564eba6_fk_auth_user_id; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.django_admin_log
    ADD CONSTRAINT django_admin_log_user_id_c564eba6_fk_auth_user_id FOREIGN KEY (user_id) REFERENCES public.auth_user(id) DEFERRABLE INITIALLY DEFERRED;


--
-- Name: pipelines_datasetpipelines pipelines_datasetpip_dataset_id_29626196_fk_pipelines; Type: FK CONSTRAINT; Schema: public; Owner: core
--

ALTER TABLE ONLY public.pipelines_datasetpipelines
    ADD CONSTRAINT pipelines_datasetpip_dataset_id_29626196_fk_pipelines FOREIGN KEY (dataset_id) REFERENCES public.pipelines_dataset(id) DEFERRABLE INITIALLY DEFERRED;


--
-- PostgreSQL database dump complete
--

