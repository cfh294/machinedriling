#!/usr/bin/env python3
import os
import gpt_2_simple as gpt2
import fire
import tweepy
import tqdm
import random
from pathlib import Path
from dotenv import load_dotenv


# root directory
load_dotenv(dotenv_path=str(Path("..") / ".env"))


def generate_tweets(run):
    """
    Generate a couple tweets from our already
    trained and tuned model
    """
    # Get our pathfor the checkpoint setup
    checkpoint_dir = Path("checkpoint").absolute()

    # Start tensorflow session & load our model
    sess = gpt2.start_tf_sess()
    gpt2.load_gpt2(sess, checkpoint_dir=checkpoint_dir, run_name=run)

    # Generate and return tweets
    tweets = list(
        map(
            lambda x: x.strip(),
            gpt2.generate(sess, run_name=run, return_as_list=True)[0].split("\n"),
        )
    )
    return tweets


def post_tweet(tweet):
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


def main(run="run1", output="twitter"):
    in_tweet_list = generate_tweets(run)
    print(f"Using run: {run}")

    # Create a tweet
    tweet = random.choice(in_tweet_list)
    print(tweet)
    """
    for tweet in set(in_tweet_list):
        if output == "twitter":
            post_tweet(tweet)
        else:
            print(tweet)
    """


if __name__ == "__main__":
    # pylint: disable=no-value-for-parameter
    fire.Fire(main)
