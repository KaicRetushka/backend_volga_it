
CREATE SEQUENCE appointments_appointment_id_seq;
CREATE SEQUENCE history_history_id_seq;
CREATE SEQUENCE hospitals_id_seq;
CREATE SEQUENCE timetables_timetable_id_seq;
CREATE SEQUENCE users_id_seq;

CREATE TABLE appointments
(
    appointment_id integer NOT NULL DEFAULT nextval('appointments_appointment_id_seq'::regclass),
    timetable_id integer NOT NULL,
    from_time timestamp without time zone,
    to_time timestamp without time zone,
    is_recorded boolean DEFAULT false,
    recorded_user character varying(100) COLLATE pg_catalog."default",
    CONSTRAINT appointments_pkey PRIMARY KEY (appointment_id)
);

CREATE TABLE history
(
    history_id integer NOT NULL DEFAULT nextval('history_history_id_seq'::regclass),
    date timestamp without time zone,
    pacient_id integer,
    hospital_id integer,
    doctor_id integer,
    room character varying(100) COLLATE pg_catalog."default",
    data text COLLATE pg_catalog."default",
    CONSTRAINT history_pkey PRIMARY KEY (history_id)
);

CREATE TABLE hospitals
(
    id integer NOT NULL DEFAULT nextval('hospitals_id_seq'::regclass),
    name character varying(100) COLLATE pg_catalog."default",
    addres character varying(400) COLLATE pg_catalog."default",  
    contact_phone character varying(12) COLLATE pg_catalog."default",
    rooms text[] COLLATE pg_catalog."default",
    is_deleted boolean DEFAULT false,
    CONSTRAINT hospitals_pkey PRIMARY KEY (id)
);

CREATE TABLE timetables
(
    timetable_id integer NOT NULL DEFAULT nextval('timetables_timetable_id_seq'::regclass), 
    hospital_id integer NOT NULL,
    doctor_id integer NOT NULL,
    from_time timestamp without time zone,
    to_time timestamp without time zone,
    room character varying(100) COLLATE pg_catalog."default",
    is_recorded boolean DEFAULT false,
    CONSTRAINT timetables_pkey PRIMARY KEY (timetable_id)
);


CREATE TABLE users
(
    id integer NOT NULL DEFAULT nextval('users_id_seq'::regclass),
    username character varying(100) COLLATE pg_catalog."default",
    password character varying(100) COLLATE pg_catalog."default",
    role text[] COLLATE pg_catalog."default",
    last_name character varying(100) COLLATE pg_catalog."default",
    first_name character varying(100) COLLATE pg_catalog."default",
    in_account boolean,
    is_deleted boolean DEFAULT false,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);

INSERT INTO users(username, password, role, last_name, first_name) VALUES('admin', 'admin', ARRAY['Admin'], 'Админ', 'Админ');
INSERT INTO users(username, password, role, last_name, first_name) VALUES('manager', 'manager', ARRAY['Manager'], 'Менеджер', 'Менеджер');  
INSERT INTO users(username, password, role, last_name, first_name) VALUES('doctor', 'doctor', ARRAY['Doctor'], 'Доктор', 'Доктор');
INSERT INTO users(username, password, role, last_name, first_name) VALUES('user', 'user', ARRAY['User'], 'Пользователь', 'Пользователь');
