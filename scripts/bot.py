#!/usr/bin/env python3
import gpt_2_simple as gpt2
import fire
import os
import tweepy
import tqdm
from pathlib import Path
from dotenv import load_dotenv


# root directory
load_dotenv(dotenv_path=str(Path("..") / ".env"))


def generate_tweets(run):
    """
    Generate a couple tweets from our already 
    trained and tuned model 
    """
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, run_name='run1')
    tweets = list(map(lambda x: x.strip(), gpt2.generate(sess, run_name=run, return_as_list=True)[0].split("\n")))
    return tweets


def post_tweets(run='run1'):
    in_tweet_list = generate_tweets(run)

    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(os.getenv("twitter_api"), os.getenv("twitter_secret"))
    auth.set_access_token(os.getenv("twitter_access_token"), os.getenv("twitter_access_token_secret"))

    # Create API object
    api = tweepy.API(auth)

    # Create a tweet
    for tweet in set(in_tweet_list):
        try:
            api.update_status(tweet)  
        except tweepy.error.TweepError:
            pass


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    fire.Fire(post_tweets)