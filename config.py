import os
from log import get_logger
from dotenv import load_dotenv
import json

load_dotenv()
logger = get_logger(__name__)


class ConfigNotFoundException(Exception):
    pass


def verify_config():
    required_options = ['REDIS_HOST',
                        'REDIS_PORT',
                        'REDIS_DB',
                        'REDIS_PASSWORD',
                        'PUBLIC_URL',
                        'PUBLIC_URL_USER',
                        'TWITCH_CLIENT_ID',
                        'TWITCH_CLIENT_SECRET',
                        'TWITCH_SUBSCRIPTION_SECRET']

    for option in required_options:
        if os.environ.get(option) == None:
            raise ConfigNotFoundException(
                'could not find {} in env variables'.format(option))
        else:
            logger.debug("found {} in config successfully".format(option))

def load_json_from_env(key: str):
    d = os.environ.get(key)
    if d == None:
        raise ConfigNotFoundException('could not find {} in env variables'.format(key))
    l = json.loads(d)
    return l

verify_config()

redis_host = os.environ.get('REDIS_HOST')
redis_port = os.environ.get('REDIS_PORT')
redis_db = os.environ.get('REDIS_DB')
redis_password = os.environ.get('REDIS_PASSWORD')
public_url = os.environ.get('PUBLIC_URL')
public_url_user = os.environ.get('PUBLIC_URL_USER')
twitch_client_id = os.environ.get('TWITCH_CLIENT_ID')
twitch_client_secret = os.environ.get('TWITCH_CLIENT_SECRET')
try:
    twitch_scopes = os.environ.get('TWITCH_SCOPES')
except ConfigNotFoundException:
    logger.warn('using preset values for twitch_scopes')
    twitch_scopes = "channel:read:predictions channel:read:polls channel:read:redemptions channel:manage:polls channel:manage:predictions"
try:
    twitch_eventsub_types = load_json_from_env('TWITCH_EVENTSUB_TYPES')
except ConfigNotFoundException:
    logger.warn('using preset values for twitch_eventsub_types')
    twitch_eventsub_types=["channel.channel_points_custom_reward_redemption.add", "channel.channel_points_custom_reward_redemption.update", "channel.poll.begin", "channel.poll.progress", "channel.poll.end", "channel.prediction.begin", "channel.prediction.progress", "channel.prediction.lock", "channel.prediction.end"]
twitch_subscription_secret = os.environ.get('TWITCH_SUBSCRIPTION_SECRET')