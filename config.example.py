redis_host = "redis_host.example.com"
redis_port = 18099
redis_db = 0
redis_password = "PUT_REDIS_PASSWORD_HERE"
public_url = "https://PUBLIC_NGROK.ngrok.io/callback"
public_url_user = "https://PUBLIC_NGROK.ngrok.io/callback_user"
twitch_client_id = "TWITCH_C_ID"
twitch_client_secret = "TWITCH_C_S"
twitch_scopes = "channel:read:predictions channel:read:polls channel:read:redemptions channel:manage:polls channel:manage:predictions"
twitch_eventsub_types = ['channel.channel_points_custom_reward_redemption.add',
            'channel.channel_points_custom_reward_redemption.update',
            'channel.poll.begin',
            'channel.poll.progress',
            'channel.poll.end',
            'channel.prediction.begin',
            'channel.prediction.progress',
            'channel.prediction.lock',
            'channel.prediction.end']
twitch_subscription_secret = "CHANGEMECHANGEMECHANGEMECHANGEMECHANGEME" #TODO: Make this randomly generate