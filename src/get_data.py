"""Tool to get the data from the Twitter API."""
import json
import re
from typing import List

import requests

from .config import BASE_PATH, TWITTER_TOKEN


ENDPOINT = 'https://api.twitter.com/2/tweets/search/recent'


def load_users() -> List[str]:
    """Load the users to get tweets from."""
    with open(str(BASE_PATH / 'accounts.txt')) as f:
        return list(f.read().strip().split('\n'))


def form_queries(users: List[str]) -> List[str]:
    """Put the lists of users into seperate Twitter queries."""
    next_group = []
    queries = []
    for user in users:
        if len(' OR '.join([*next_group, '@' + user])) < 512:
            next_group.append('@' + user)
        else:
            queries.append(' OR '.join(next_group))
            next_group = ['@' + user]
    queries.append(' OR '.join(next_group))
    return queries


def make_queries(queries: List[str], target_tweets: int) -> List[str]:
    """Get tweets from some queries."""
    headers = {'Authorization': f'Bearer {TWITTER_TOKEN}'}
    tweets = []
    tweets_per_query = target_tweets // len(queries)
    for query in queries:
        tweets_for_query = 0
        next_token = None
        while (
                    tweets_for_query < tweets_per_query and next_token
                ) or (not tweets_for_query):
            params = {'query': query, 'max_results': 100}
            if next_token:
                params['next_token'] = next_token
            response = requests.get(
                ENDPOINT, headers=headers, params=params
            ).json()
            for tweet in response['data']:
                if not tweet['text'].startswith('RT '):
                    tweets.append(tweet['text'])
                    tweets_for_query += 1
            next_token = response['meta'].get('next_token')
    return tweets


def filter_tweets(tweets: List[str]) -> List[str]:
    """Filter tweets to remove user mentions and links."""
    filtered_tweets = []
    for tweet in tweets:
        filtered_tweet = re.sub(r'@\w{4,15}', '', tweet)
        filtered_tweet = re.sub(r'https?://[^ ]*', '', filtered_tweet)
        filtered_tweets.append(filtered_tweet.strip())
    return filtered_tweets


def download_tweets(target_tweets: int = 100):
    """Coordinates downloading a selection of tweets to a file."""
    users = load_users()
    queries = form_queries(users)
    unfiltered_tweets = make_queries(queries, target_tweets)
    tweets = filter_tweets(unfiltered_tweets)
    with open(str(BASE_PATH / 'tweets.json'), 'w') as f:
        json.dump({'tweets': tweets}, f)
