"""
At some point, I will need to learn how to mock external services. For now
directly use twitter api for tests.
"""
from __future__ import print_function
import ujson as json
from twitter import Twitter


class TestTwitter(object):
    def __init__(self):
        with open('settings.json.test', 'rt') as f:
            self.SETTINGS = json.load(f)

    def test_access_token(self):
        tw = Twitter(**self.SETTINGS)
        print("Twitter object: ", tw)
        tw.get_access_token()
        assert tw.access_token

    def test_user_lookup(self):
        tw = Twitter(**self.SETTINGS)
        print("Twitter object: ", tw)
        tw.get_access_token()
        user = tw.user_lookup(screen_name='neokluber')
        print("Twitter username: ", user)
        assert user[0]['id_str']

    def test_get_friends(self):
        tw = Twitter(**self.SETTINGS)
        print("Twitter object: ", tw)
        tw.get_access_token()
        user = tw.user_lookup(screen_name='neokluber')
        uid = user[0]['id_str']

        friend_list = tw.get_friends(uid)
        print("Friends list: ", friend_list)
        assert isinstance(friend_list, list)
        assert friend_list

    def test_get_limits(self):
        tw = Twitter(**self.SETTINGS)
        print("Twitter object: ", tw)
        tw.get_access_token()

        limits = tw.get_limits()
        print("Limits: ", limits)

        assert (limits.get('resources').get('friends').get('/friends/ids')
                .get('remaining'))

        assert (limits.get('resources').get('users').get('/users/lookup')
                .get('remaining'))
