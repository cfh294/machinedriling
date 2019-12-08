"""
Utility objects for this project
"""
import functools
import psycopg2
import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, String, BLOB, MetaData, TIMESTAMP
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from pathlib import PurePath, Path


# root directory
_root = PurePath(__file__).parent
_dot_file = str(_root.parent / ".env")
load_dotenv(dotenv_path=_dot_file)

# grab configuration settings
connection_string = f"{os.getenv('rdbms')}://"\
                    f"{os.getenv('user')}:{os.getenv('password')}"\
                    f"@{os.getenv('host')}/{os.getenv('database')}"
engine = create_engine(connection_string, pool_pre_ping=True)
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


class AttrDict(dict):
    def __init__(self, *args, **kwargs):
        super(AttrDict, self).__init__(*args, **kwargs)
        self.__dict__ = self


def clean_account_name(in_name):
    """
    Cleans account name input
    :param in_name: The input account name
    :return:        The cleaned account name
    """
    result = in_name
    if in_name.startswith("@"):
        result = result[1:]
    return result


def with_engine(f):
    def with_engine_(*args, **kwargs):
        return f(create_engine(connection_string), *args, **kwargs)
    return with_engine_


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

                
def with_sql(file_path):
    def with_sql_(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            with open(str(_root / "sql" / file_path), "r") as sql_file:
                sql_string = "".join(sql_file.readlines())
            return f(sql_string, *args, **kwargs)
        return wrap
    return with_sql_


def with_connection(auto_commit=False):
    """
    Decorator that safely manages a connection object within the context of the decorated function.
    If an exception is raised, the connection object properly rolls back all changes and closes.
    :param auto_commit: Whether or not the connection should commit changes automatically if there are no exceptions.
    :return:            The decorated function
    """
    def with_connection_(f):
        @functools.wraps(f)
        def wrap(*args, **kwargs):
            connection = psycopg2.connect(connection_string)
            exception = None
            try:
                f(connection, *args, **kwargs)
            except Exception as e:
                connection.rollback()
                exception = e
            else:
                if auto_commit:
                    connection.commit()
            finally:
                connection.close()
                del connection
                if exception:
                    raise exception
        return wrap
    return with_connection_
