"""Load config from JSON."""
import json
import pathlib


BASE_PATH = pathlib.Path(__file__).parent.parent


with open(str(BASE_PATH / 'config.json')) as f:
    _config = json.load(f)


TWITTER_TOKEN = _config['twitter_token']
