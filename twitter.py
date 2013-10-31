# -*- coding: utf-8 -*-

__title__ = 'twitter'
__version__ = '1.0'
__author__ = 'Anu Joy'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Anu Joy'


import requests
import logging
from base64 import b64encode


class Twitter:
    """
    Twitter Class providing basic authentication and api query methods
    """

    __attrs__ = [
        'app_name', 'consumer_key', 'consumer_secret',
        'auth_url', 'friends_url', 'limit_url', 'CONTENT_TYPE',
        'access_token']

    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(message)s')

    def __init__(self, app_name="", consumer_key="", consumer_secret="",
                 auth_url="", friends_url="", limit_url="",
                 user_lookup_url=""):
        self.app_name = app_name
        self.consumer_key = consumer_key
        self.consumer_secret = consumer_secret
        self.auth_url = auth_url
        self.friends_url = friends_url
        self.limit_url = limit_url
        self.user_lookup_url = user_lookup_url
        self.CONTENT_TYPE = 'application/x-www-form-urlencoded;charset=UTF-8'

    def __repr__(self):
        return "Twitter(app_name=%s, consumer_key=%s, consumer_secret=%s, "\
               "auth_url=%s, friends_url=%s, limit_url=%s, access_token=%s)"\
            % (self.app_name, self.consumer_key, self.consumer_secret,
               self.auth_url, self.friends_url, self.limit_url,
               self.access_token)

    def get_access_token(self):
        """ Returns the bearer token for api requests """

        headers = {
            'User-Agent': self.app_name,
            'Authorization': 'Basic ' + b64encode(self.consumer_key + ':' +
                                                  self.consumer_secret),
            'Content-Type': self.CONTENT_TYPE
            }

        payload = 'grant_type=client_credentials'

        try:
            r = requests.post(self.auth_url, payload, headers=headers)
            if r.json()['token_type'] == 'bearer':
                self.access_token = r.json()['access_token']
            else:
                raise Exception("Invalid response from access token api")
        except Exception:
            logging.debug("Error posting access token request")

    def get_friends(self, id):
        """
        Return list of 5000 friends. That should be enough for graph
        visualisation. If more than 5000 records need to be
        retrieved this function needs to be modified to use twitter's
        cursor navigation method
        """
        headers = {
            'User-Agent': self.app_name,
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': self.CONTENT_TYPE
            }
        payload = {
            'user_id': id,
            'stringify_ids': 'true'
            }

        try:
            r = requests.get(self.friends_url, params=payload, headers=headers)
            if r.status_code == requests.codes.ok:
                return r.json().get('ids')
            else:
                return None
        except Exception:
            logging.debug("Error getting friends/ids")
            return None

    def get_limits(self):
        headers = {
            'User-Agent': self.app_name,
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': self.CONTENT_TYPE
            }

        payload = {
            'resources': 'users,friends'
            }
        try:
            r = requests.get(self.limit_url, params=payload, headers=headers)
            if r.status_code == requests.codes.ok:
                return r.json()
            else:
                return None
        except Exception:
            logging.debug("Error getting resource limits")
            return None

    def user_lookup(self, screen_name="", id=""):
        headers = {
            'User-Agent': self.app_name,
            'Authorization': 'Bearer ' + self.access_token,
            'Content-Type': self.CONTENT_TYPE
            }

        payload = {
            'screen_name': screen_name,
            'user_id': id
            }

        try:
            r = requests.get(self.user_lookup_url, params=payload,
                             headers=headers)
            if r.status_code == requests.codes.ok:
                return r.json()
            else:
                return None
        except Exception:
            logging.debug("Error getting user details")
            return None
