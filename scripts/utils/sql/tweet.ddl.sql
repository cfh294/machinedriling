CREATE TABLE wtm.tweet
(
    tweet_id text COLLATE pg_catalog."default" NOT NULL,
    tweet_user text COLLATE pg_catalog."default",
    tweet_text text COLLATE pg_catalog."default",
    tweet_date timestamp without time zone,
    CONSTRAINT tweet_pkey PRIMARY KEY (tweet_id)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE wtm.tweet
    OWNER to postgres;