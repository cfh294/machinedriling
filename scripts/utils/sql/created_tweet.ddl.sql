CREATE TABLE wtm.created_tweet
(
    tweet_user text COLLATE pg_catalog."default" NOT NULL,
    tweet_text text COLLATE pg_catalog."default" NOT NULL,
    create_date timestamp without time zone NOT NULL,
    CONSTRAINT created_tweet_pkey PRIMARY KEY (tweet_user, create_date)
)
WITH (
    OIDS = FALSE
)
TABLESPACE pg_default;
ALTER TABLE wtm.created_tweet
    OWNER to postgres;
GRANT ALL ON TABLE wtm.created_tweet TO postgres;