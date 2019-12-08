CREATE TABLE wtm.model
(
    tweet_user text COLLATE pg_catalog."default" NOT NULL,
    model bytea,
    vocab bytea,
    words bytea,
    vocab_inv bytea,
    CONSTRAINT model_pkey PRIMARY KEY (tweet_user)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE wtm.model
    OWNER to postgres;
GRANT ALL ON TABLE wtm.model TO postgres;