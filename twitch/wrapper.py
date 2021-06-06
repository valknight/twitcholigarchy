from requests.api import head
from sanic.response import json, redirect
import aiohttp
import json
import requests
import sys
from datetime import datetime
from data import store
from polls.poll import Poll, PollTypes
from config import twitch_client_secret, twitch_client_id, twitch_scopes, public_url, public_url_user, twitch_eventsub_types, twitch_subscription_secret
import asyncio

class Twitch:
    def __init__(self) -> None:
        self.poll = None
        self.eventsub_registered = False
        self.lastRefresh = -1
        self.lastUser = -1
        self.timeBetweenRefreshes = 30
        if store.get('auth') is not None:
            if json.loads(store.get('auth')).get('scope', []) != twitch_scopes.split(" "):
                print("Scope not same, wiping auth")
                store.delete('auth') # need to change out if the scope is invalid

    def get_user(self) -> dict:
        if datetime.utcnow().timestamp() - self.lastUser > self.timeBetweenRefreshes:
            print('using cached user data')
            if store.get('user') is not None:
                return json.loads(store.get('user'))
        print("refreshing user data")
        headers = {'Client-ID': twitch_client_id,
                   'Authorization': 'Bearer {}'.format(self.refresh_user_access_token()['access_token']), 'Content-Type': 'application/json'}
        r = requests.get('https://api.twitch.tv/helix/users', headers=headers)
        store.set('user', json.dumps(r.json()))
        self.lastUser = datetime.utcnow().timestamp()
        return self.get_user()
    
    def get_token(self) -> json:
        r = requests.post("https://id.twitch.tv/oauth2/token?client_id={}&client_secret={}&grant_type=client_credentials&scope={}".format(
            twitch_client_id, twitch_client_secret, twitch_scopes))
        return r.json()

    def get_user_redirect_url(self) -> str:
        return "https://id.twitch.tv/oauth2/authorize?client_id={}&redirect_uri={}&response_type=code&scope={}".format(twitch_client_id, public_url_user, twitch_scopes)

    def refresh_user_access_token(self) -> dict:
        auth = store.get('auth')
        if auth is None:
            return None
        if datetime.utcnow().timestamp() - self.lastRefresh > self.timeBetweenRefreshes:
            print("using cached auth")
            return json.loads(store.get('auth'))
        auth = json.loads(store.get('auth'))
        r = requests.post("https://id.twitch.tv/oauth2/token?grant_type=refresh_token&refresh_token={refresh_token}&client_id={id}&client_secret={secret}".format(
            id=twitch_client_id, secret=twitch_client_secret, refresh_token=auth.get('refresh_token')))
        if r.json().get('access_token') is not None:
            store.set('auth', json.dumps(r.json()))
        self.lastRefresh = datetime.utcnow().timestamp()
        return r.json()

    def get_user_access_token(self, code) -> dict:
        r = requests.post('https://id.twitch.tv/oauth2/token?client_id={id}&client_secret={secret}&code={code}&grant_type=authorization_code&redirect_uri={redirect}'.format(
            id=twitch_client_id, secret=twitch_client_secret, code=code, redirect=public_url_user))
        if r.json().get('access_token') is not None:
            store.set('auth', json.dumps(r.json()))
        return r.json()

    async def register_eventsub(self) -> str:
        # first up, get the user's ID using the token which should be generated by now
        user = self.get_user()
        user_id = user.get('data', [{}])[0].get('id')
        if user_id is None:
            # if this is the case, the token may be expired or invalid. might need another login.
            raise ValueError('could not get user ID')
        token = self.get_token()['access_token']
        headers = {'Client-ID': twitch_client_id,
                   'Authorization': 'Bearer {}'.format(token), 'Content-Type': 'application/json'}
        # Get the existing subscriptions
        url = "https://api.twitch.tv/helix/eventsub/subscriptions"
        r = requests.get(url, headers=headers)
        for subscription in r.json()['data']:
            async with aiohttp.ClientSession() as session:
                await session.delete("https://api.twitch.tv/helix/eventsub/subscriptions?id={}".format(subscription['id']), headers=headers)

        for t in twitch_eventsub_types:
            async with aiohttp.ClientSession() as session:
                # Go and setup the event subscriptions!
                await session.post("https://api.twitch.tv/helix/eventsub/subscriptions", headers=headers, json={
                    "type": "{}".format(t),
                    "version": "1",
                    "condition": {
                            "broadcaster_user_id": "{}".format(user_id)
                    },
                    "transport": {
                        "method": "webhook",
                        "callback": public_url,
                        "secret": twitch_subscription_secret
                    }
                })
        self.eventsub_registered = True
        return "sent subscription requests for {} event types".format(len(twitch_eventsub_types))

    def handle(self, data: dict):
        # TODO: Write data handling
        if data.get('subscription').get('type') == "channel.poll.begin":
            if len(dict(data.get('event').get('choices'))) > 2:
                return  # polls larger than 2 we can't handle
            c = data.get('event').get('choices')
            # We got a new normal twitch poll!
            self.poll = Poll(data.get('event')[
                             'title'], c[0]['title'], c[1]['title'], False, PollTypes.POLL)
        elif data.get('subscription').get('type') == "channel.poll.progress":
            if self.poll is not None:
                if self.poll.name == data.get('event').get('title'):
                    self.poll.setVotesPoll(data.get('event').get('choices'))
            pass
        elif data.get('subscription').get('type') == "channel.poll.end":
            if self.poll is not None:
                self.poll.close()
        elif data.get('subscription').get('type') == "channel.channel_points_custom_reward_redemption.add":
            pass
        elif data.get('subscription').get('type') == "channel.prediction.begin":
            e = data.get('event')
            outcomes = e.get('outcomes',[{},{}])
            self.poll = Poll(e.get('title'), outcomes[0].get('title'), outcomes[1].get('title'), True, PollTypes.PREDICTION)
        elif data.get('subscription').get('type') == "channel.prediction.progress":
            e = data.get('event')
            outcomes = e.get('outcomes')
            self.poll.setVotesPrediction(outcomes)
        elif data.get('subscription').get('type') == "channel.prediction.lock":
            e = data.get('event')
            self.poll.setVotesPrediction(e.get('outcomes'))
            self.poll.close()
            self.poll.expiration = (sys.maxsize / 4)
        elif data.get('subscription').get('type') == "channel.prediction.end":
            e = data.get('event')
            self.poll.setVotesPrediction(e.get('outcomes'))
            self.poll.close()
            self.poll.expiration = 30
        else:
            print(data.get('subscription').get('type'))

    def get_poll(self):
        if self.poll is None:
            return None
        if not(self.poll.isOpen) and datetime.utcnow().timestamp() - self.poll.closedAt > self.poll.expiration:
            self.poll = None
        return self.poll