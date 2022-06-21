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
    exp_uuid uuid NOT NULL,
	tr_uuid uuid NOT NULL,
	addeddate timetz NOT NULL,
	amount varchar NOT NULL,
	"name" varchar NOT NULL,
	CONSTRAINT expenses_pk PRIMARY KEY (id),
	CONSTRAINT expenses_un UNIQUE (exp_uuid),
	CONSTRAINT expenses_fk FOREIGN KEY (tr_uuid) REFERENCES public.tricount(tr_uuid)
);


-- public.impacts definition

-- Drop table

-- DROP TABLE public.impacts;

CREATE TABLE public.impacts (
	id int8 NOT NULL GENERATED ALWAYS AS IDENTITY,
    exp_uuid uuid NOT NULL,
	"User" varchar NOT NULL,
	amount numeric NOT NULL,
	CONSTRAINT impacts_pk PRIMARY KEY (id),
	CONSTRAINT impacts_fk FOREIGN KEY (exp_uuid) REFERENCES public.expenses(exp_uuid)
);