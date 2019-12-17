#!/usr/bin/env python3
import os
import gpt_2_simple as gpt2
import fire
import tweepy
import tqdm
import random
import time
from pathlib import Path
from dotenv import load_dotenv


# root directory
load_dotenv(".env")


def generate_tweets(run, sess):
    """
    Generate a couple tweets from our already
    trained and tuned model
    """

    # Generate and return tweets
    tweets = list(
        map(
            lambda x: x.strip(),
            gpt2.generate(sess, run_name=run, return_as_list=True)[0].split("\n"),
        )
    )
    return tweets


def load_model(run):
    # Get our pathfor the checkpoint setup
    checkpoint_dir = Path("checkpoint").absolute()

    # Start tensorflow session & load our model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_dir, run_name=run)
    return sess


def post_tweet(tweet):
    print("Posting Tweet")
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler(os.getenv("twitter_api"), os.getenv("twitter_secret"))
    auth.set_access_token(
        os.getenv("twitter_access_token"), os.getenv("twitter_access_token_secret")
    )

    # Create API object
    api = tweepy.API(auth)
    try:
        api.update_status(tweet)
    except tweepy.error.TweepError:
        pass


def main(run="run1"):
    sess = load_model(run)

    while True:
        print("Generating Tweet")
        # Create a tweet
        in_tweet_list = generate_tweets(run, sess)
        tweet = random.choice(in_tweet_list)
        post_tweet(tweet)
        # Sleep for 15min
        print("Sleeping for 15min")
        time.sleep(900)


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    print("Running Bot")
    fire.Fire(main)
