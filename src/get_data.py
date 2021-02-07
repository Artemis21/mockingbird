"""Tool to get the data from the Twitter API."""
import requests

from .config import BASE_PATH, TWITTER_TOKEN


def load_users() -> list[str]:
    """Load the users to get tweets from."""
    with open(str(BASE_PATH / 'accounts.txt')) as f:
        return list(f.read().strip().split('\n'))


def form_queries(users: list[str]) -> list[str]:
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
