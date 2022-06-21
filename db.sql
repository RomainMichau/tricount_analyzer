-- public.tricount definition

-- Drop table

-- DROP TABLE public.tricount;

CREATE TABLE public.tricount (
	id int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
	tr_uuid uuid NOT NULL,
	title varchar NOT NULL,
	CONSTRAINT tricount_pk PRIMARY KEY (id),
	CONSTRAINT tricount_un UNIQUE (tr_uuid)
);


-- public.expenses definition

-- Drop table

-- DROP TABLE public.expenses;

CREATE TABLE public.expenses (
	id int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
	tr_id int8 NOT NULL,
	addeddate varchar NOT NULL,
	tr_exp_id int8 NOT NULL,
	amount varchar NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT expenses_pk PRIMARY KEY (id),
	CONSTRAINT expenses_un UNIQUE (tr_exp_id),
	CONSTRAINT expenses_fk FOREIGN KEY (tr_id) REFERENCES public.tricount(id)
);


-- public.impacts definition

-- Drop table

-- DROP TABLE public.impacts;

CREATE TABLE public.impacts (
	id int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
	exp_id int8 NOT NULL,
	"User" varchar NOT NULL,
	amount numeric NOT NULL,
	CONSTRAINT impacts_pk PRIMARY KEY (id),
	CONSTRAINT impacts_fk FOREIGN KEY (exp_id) REFERENCES public.expenses(id)
);