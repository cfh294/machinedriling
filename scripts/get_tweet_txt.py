#!/usr/bin/env python3
import argparse
import re
from utils import with_session, Tweet
from sqlalchemy import not_

_fake_link = "https://tinyurl.com/jwj699s"
_regex = re.compile(r"http[s]{0,1}://[www\.]*(t\.co|tinyurl|bit\.ly|tinypic).*")

def with_cmd_line_args(f):  
    def with_cmd_line_args_(*args, **kwargs):
        ap = argparse.ArgumentParser(description="Pull all tweets for a user and output a massive text blob.")
        ap.add_argument("-u", "--user", required=True, type=str, help="Twitter account username.")
        ap.add_argument("-f", "--file", required=True, type=str, help="Output file path for .txt file.")
        return f(ap.parse_args(), *args, **kwargs)
    return with_cmd_line_args_


def clean_tweet(in_tweet):
    out = ""
    if _regex.match(in_tweet.tweet_text):
        out = _regex.sub(_fake_link, in_tweet.tweet_text)
    else:
        out = in_tweet.tweet_text
    return out


@with_session()
@with_cmd_line_args
def main(cmd_line, session):
    tweets = session.query(Tweet).filter(
        Tweet.tweet_user == cmd_line.user
    ).all()
    cleaned = list(map(lambda t: clean_tweet(t), tweets))
    with open(cmd_line.file, "w") as output:
        output.write("\n".join(cleaned))

if __name__ == "__main__":
    main()
