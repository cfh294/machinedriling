#!/usr/bin/env python3
import json
import argparse
import datetime
import logging
from utils import with_connection, with_sql

logging.basicConfig(level=logging.DEBUG)


def with_cmd_line_args(f):
    """
    Decorator that handles command line argument parsing
    :param f: The function to be decorated
    :return:  The decorated function
    """
    def with_cmd_line_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Loads a json files of tweets to the configured database.")
        ap.add_argument("-f", "--file-path", type=str, required=True, help="Path to json file.")
        ap.add_argument("-n", "--chunk-size", type=int, default=100000,
                        help="PostgreSQL connection will commit after every n-records.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_cmd_line_args_


@with_connection(auto_commit=True)
def insert_values(connection, sql, values):
    cursor = connection.cursor()
    cursor.execute(sql, values)
    cursor.close()
    del cursor


@with_sql("insert_tweet.dml.sql")
@with_cmd_line_args
def main(cmd_line, sql):
    """
    Main method, contains the main logic of the program
    :param cmd_line:   Command line arguments (from decorator)
    :param sql:        Sql to execute (from decorator)
    :return:
    """
    logging.info(f"Loading file ({cmd_line.file_path})...")
    with open(cmd_line.file_path, "r") as json_file:
        data = json.load(json_file)["tweets"]
    logging.info("Done.")

    logging.info("Loading tweets...")
    logging.info("Done.")
    overall_sql = ""
    current_values = []
    num_tweets = len(data)
    logging.info(f"Inserting {num_tweets} tweets into the database.")
    for i, tweet in enumerate(data, start=1):
        current_values.extend([
            tweet["tweet_id"],
            tweet["tweet_user"],
            tweet["tweet_text"],
            datetime.datetime.strptime(tweet["tweet_date"], "%b %d, %Y %I:%M:%S %p")
        ])
        overall_sql += sql + "\n"

        if i % cmd_line.chunk_size == 0 or i == num_tweets - 1:
            logging.info(f"\tAdding {cmd_line.chunk_size} records...")
            insert_values(overall_sql, current_values)
            overall_sql = ""
            current_values = []
    logging.info("Finished.")


# run the program
if __name__ == "__main__":
    main()
