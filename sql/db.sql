-- public.tricount definition

-- Drop table

-- DROP TABLE public.tricount;

CREATE TABLE public.tricount
(
    id          int8    NOT NULL GENERATED ALWAYS AS IDENTITY,
    tr_uuid     uuid    NOT NULL,
    tr_id       varchar NOT NULL,
    title       varchar NOT NULL,
    description varchar NOT NULL,
    tr_currency varchar NOT NULL,
    CONSTRAINT tricount_pk PRIMARY KEY (id),
    CONSTRAINT tr_id_un UNIQUE (tr_uuid),
    CONSTRAINT tricount_un UNIQUE (tr_id)
);


-- public.expenses definition

-- Drop table

-- DROP TABLE public.expenses;

CREATE TABLE public.expenses
(
    id                  int8        NOT NULL GENERATED ALWAYS AS IDENTITY,
    exp_uuid            uuid        NOT NULL,
    tr_uuid             uuid        NOT NULL,
    amount_tr_currency  numeric     NOT NULL,
    amount_exp_currency numeric     NOT NULL,
    exchange_rate       numeric     NOT NULL,
    exp_currency        varchar     NOT NULL,
    "name"              varchar     NOT NULL,
    payed_by            varchar     NOT NULL,
    addeddate           timestamptz NOT NULL,
    CONSTRAINT expenses_pk PRIMARY KEY (id),
    CONSTRAINT expenses_un UNIQUE (exp_uuid),
    CONSTRAINT expenses_fk FOREIGN KEY (tr_uuid) REFERENCES public.tricount (tr_uuid)
);


-- public.impacts definition

-- Drop table

-- DROP TABLE public.impacts;

CREATE TABLE public.impacts
(
    id                 int8    NOT NULL GENERATED ALWAYS AS IDENTITY,
    exp_uuid           uuid    NOT NULL,
    "User"             varchar NOT NULL,
    amount_tr_currency numeric NOT NULL,
    CONSTRAINT impacts_pk PRIMARY KEY (id),
    CONSTRAINT impacts_fk FOREIGN KEY (exp_uuid) REFERENCES public.expenses (exp_uuid)
);