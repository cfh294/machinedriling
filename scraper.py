#!/usr/bin/env python3
"""
scraper.py

Scrapes a bunch of tweets from a tweet aggregation site (https://cooltweets.herokuapp.com/)

Usage:
   ./scraper.py [-nl, --no-logging]
"""
import requests
import logging
import argparse
import json
import os
from bs4 import BeautifulSoup

_url = "https://cooltweets.herokuapp.com/"
_skip = "improver.html"

logging.getLogger("urllib3").setLevel(logging.WARNING)


def validate_filepath(file_path):
    if os.path.exists(os.path.dirname(file_path)):
        return file_path
    else:
        raise IOError("Invalid file path.")


def with_cmd_line_args(f):
    """
    Decorator that gathers information from the command line
    :param f: the function to be decorated
    :return:  the decorated function
    """
    def with_cmd_line_args_(*args, **kwargs):
        ap = argparse.ArgumentParser()
        ap.add_argument("-o", "--output-file", type=validate_filepath, required=True, help="The output file location.")
        ap.add_argument("-nl", "--no-logging", action="store_true", default=False, help="Turn off logging.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_cmd_line_args_


@with_cmd_line_args
def main(cmd_line):
    """
    Main method, contains the main program
    :param cmd_line: Parsed command line argument(s) from the user
    :return:
    """

    # turn logging off, if desired by the user
    if cmd_line.no_logging:
        logging.basicConfig(level=logging.CRITICAL)
    else:
        logging.basicConfig(level=logging.DEBUG)
    logging.info("Grabbing accounts...")

    # make request to get the main page of the site, this page has a list of accounts that is easy to scrape
    account_request = requests.get(_url)
    if account_request.status_code == 200:
        logging.info("Done.")
        home_soup = BeautifulSoup(account_request.text, "html.parser")
        tweet_list = []

        # iterate through the account name links
        for account in home_soup.find_all("a"):

            account_href = account.get("href")
            tweet_page = requests.get(_url + account_href)

            # grab all tweets for a given account
            user = account_href.replace("/old", "")
            logging.info(f"Scraping tweets for @{user}...")

            if tweet_page.status_code == 200:
                tweet_soup = BeautifulSoup(tweet_page.text, "html.parser")

                # iterate through this account's tweets, add a dml statement to our list of
                # sql statements
                for tweet in tweet_soup.find_all("li", {"class": "t"}):
                    tweet_id = tweet.get("id")
                    tweet_text = tweet.find("div", {"class": "text"}).text.strip()
                    tweet_dt = tweet.find("div", {"class": "time"}).text.strip()
                    tweet_list.append(
                        dict(tweet_id=tweet_id, tweet_user=user, tweet_text=tweet_text, tweet_date=tweet_dt)
                    )
                logging.info("Done.")
            else:
                logging.warning(f"Could not retrieve tweets for @{user}, skipping.")

        # insert the tweet data into the database table
        if tweet_list:
            logging.info(f"Writing tweets into to {cmd_line.output_file}...")
            with open(cmd_line.output_file, "w") as output_file:
                output_file.write(json.dumps(dict(tweets=tweet_list)))
                logging.info("Done.")
    else:
        logging.error("Could not retrieve accounts.")


# run program
if __name__ == "__main__":
    main()
