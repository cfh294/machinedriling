"""
Utility objects for this project
"""
import functools
import psycopg2
import os
import threading
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, BLOB, MetaData, TIMESTAMP, exc, event
from sqlalchemy.pool import Pool
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import PurePath, Path
from datetime import datetime


# root directory
_root = PurePath(__file__).parent
_dot_file = str(_root.parent.parent / ".env")
load_dotenv(dotenv_path=_dot_file)

# grab configuration settings
connection_string = f"{os.getenv('rdbms')}://"\
                    f"{os.getenv('user')}:{os.getenv('password')}"\
                    f"@{os.getenv('host')}/{os.getenv('database')}"
engine = create_engine(connection_string, pool_pre_ping=True, pool_recycle=1800, connect_args=dict(connect_timeout="86400"))
session_maker = sessionmaker()
_base = declarative_base(MetaData())


class Tweet(_base):
    __tablename__ = "tweet"
    __table_args__ = dict(schema="wtm")

    tweet_id = Column(String, primary_key=True)
    tweet_user = Column(String)
    tweet_text = Column(String)
    tweet_date = Column(TIMESTAMP)
    

class CreatedTweet(_base):
    __tablename__ = "created_tweet"    
    __table_args__ = dict(schema="wtm")

    tweet_user = Column(String, primary_key=True)
    tweet_text = Column(String)
    create_date = Column(TIMESTAMP, primary_key=True)


class ModelData(_base):
    __tablename__ = "model"
    __table_args__ = dict(schema="wtm")

    tweet_user = Column(String, primary_key=True)
    model = Column(BLOB)
    vocab = Column(BLOB)
    vocab_inv = Column(BLOB)
    words = Column(BLOB)


def with_session(auto_commit=False):
    def with_session_(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            session = sessionmaker(bind=engine)()
            error = None
            try:
                f(session, *args, **kwargs)
            except Exception as e:
                session.rollback()
                error = e
            else:
                if auto_commit:
                    session.commit()
            finally:
                session.close()
                if error:
                    raise error
        return wrap
    return with_session_
