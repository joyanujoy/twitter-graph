# -*- coding: utf-8 -*-

"""
graph.py - written during my early python days, so code not 100% pythonic
--------

graph.py is a tool for extracting a twitter user's friends ie 'following' list
into a json file for building social network visualisation in d3.js.

Usage:

    python graph.py <setting file.json> <twitter screen name>

    e.g python graph.py settings.json TelegraphLondon

    settings.json contains api settings. e.g
    {
        "app_name": "Registered Twitter APP name",
        "consumer_key": "lrRh435yyQs1RDygpyKyS78",
        "consumer_secret": "zEIIOoxjlhSFLh4ypUyy",
        "auth_url": "https://api.twitter.com/oauth2/token",
        "friends_url": "https://api.twitter.com/1.1/friends/ids.json",
        "limit_url": "https://api.twitter.com/1.1/application/rate_limit_statu
        s.json",
        "user_lookup_url" : "https://api.twitter.com/1.1/users/lookup.json"
    }

Output:
    graph.json file in the format required for d3.js:
    {
        "nodes" : [
                    {"name": Name, "scr_name": Screen Name, "degree": Degree},
                    {"name": Name, "scr_name": Screen Name, "degree": Degree},
                ],
        "links" : [
                    {"source": index of source, "target": index of target},
                    {"source": index of source, "target": index of target}
                ]

    }

    where Degree: indegree of the node ie. number of followers
          index : index of element in the list "nodes"



"""

__title__ = 'graph'
__version__ = '1.0'
__author__ = 'Anu Joy'
__license__ = 'Apache 2.0'
__copyright__ = 'Copyright 2013 Anu Joy'

import sys
import json
import logging
from time import strftime, localtime, sleep, time
from twitter import Twitter


logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')


def call_api(func, n):
    """
    A wrapper to call api function. If response is null retry n times.
    """
    if n == 0:
        return func
    else:
        n -= 1
        return func or call_api(func, n)


def self_limit(twitter, entity, n):
    """
    Find the time when current twitter API limit window is expiring, sleep for
    a second more to overcome the limit.
    twitter :   twitter object
    entity  :   twitter resource entity; 'friends/ids' or 'users/lookup'
    n       :   self limit threshold, e.g 3 (3 calls remaining)


    Twitter limit API returns an epoch time value when the current limit
    window will be reset; sleep for reset time + 1 second.
    """
    snooze = None

    try:

        limits = twitter.get_limits()

        if entity == 'friends/ids':
            if limits['resources']['friends']['/friends/ids']['remaining'] < n:
                snooze = abs(limits['resources']['friends']['/friends/ids']
                             ['reset'] - time()) + 1
        elif entity == 'users/lookup':
            if limits['resources']['users']['/users/lookup']['remaining'] < n:
                snooze = abs(limits['resources']['users']['/users/lookup']
                             ['reset'] - time()) + 1
    except Exception:
        raise

    if(snooze):
        logging.info(("Nearing limit, sleeping till %s") %
                     (strftime("%Y-%m-%d %H:%M:%S", localtime(time()+snooze))))
        sleep(snooze)


def main(filename, screen_name):
    """
    filename : json settings file see the sample file in repository
    screen_name : screen name of a twitter user
    """

    with open(filename, 'r') as f:
        settings = json.load(f)

    twitter = Twitter(**settings)
    twitter.get_access_token()

    # Graph structure { node_a: [connected_node_1, connected_node_2,..]}
    graph = {}

    self_limit(twitter, 'users/lookup', 3)
    try:
        uid = call_api(twitter.user_lookup(screen_name=screen_name),
                       3)[0]['id_str']
    except Exception:
        logging.debug("Error getting twitter userid: " + screen_name)
        raise

    self_limit(twitter, 'friends/ids', 3)
    try:
        graph[uid] = call_api(twitter.get_friends(uid), 3)
    except Exception:
        logging.debug("Error getting friends list")
        raise

    # Get friends' friends and add to nodes; graph[friend] = [their friends]
    for friend in graph[uid]:
        self_limit(twitter, 'friends/ids', 3)
        try:
            graph[friend] = call_api(twitter.get_friends(friend), 3)
        except Exception:
            logging.debug("Error getting friends' friends!")
            raise
        # No point in hitting twitter too fast
        sleep(10)

    # Find indegree of connected nodes and build a frequency table. The freq
    # table can be used to idenfity nodes to include in the graph. ie include
    # only those users with at least 2 followers within the network.
    freq = {}
    freq[uid] = 0  # because main user may not appear in the below list
    for node in [x for y in graph.values() if y is not None for x in y]:
        if node in freq:
            freq[node] += 1
        else:
            freq[node] = 1

    # Add main user and friends to a list. Indices of elements in this list
    # will be used later to build graph node source->target table for d3.js
    node_list = graph.keys()

    # Add friends of friends to node list if they're friends with more than 1
    for node in [x for x in freq if freq[x] > 5]:
        if node not in node_list:
            node_list.append(node)

    logging.info(('Found %s vertices for the graph') % (len(node_list)))

    # Get user's name and screen name; store it in a dict for lookup later
    # bunch 100 ids into a comma separated query string
    n = 0
    query_str = ''
    user_details = {}

    for user in node_list:
        n += 1
        query_str += user + ","
        if (n % 100 == 0) or n == len(node_list):

            try:
                r = call_api(twitter.user_lookup(id=query_str), 3)
            except Exception:
                logging.debug("Error getting details for: " + user)
                raise

            for rec in r:
                # user_details[user_id] = [name, screen_name].
                user_details[rec['id_str']] = [rec.get('name'),
                                               rec.get('screen_name')]
            query_str = ''

    # Build json for d3.js
    # {
    #    "nodes" : [
    #                {"name": Name, "scr_name": Screen Name, "degree": Degree},
    #                {"name": Name, "scr_name": Screen Name, "degree": Degree},
    #            ],
    #    "links" : [
    #                {"source": index of source, "target": index of target},
    #                {"source": index of source, "target": indext of target}
    #            ]
    # }

    d3_json = {
        "nodes": [],
        "links": []
    }

    for user_id in node_list:
        if user_id in user_details:
            d3_json["nodes"].append({
                "name": user_details[user_id][0],
                "scr_name": user_details[user_id][1],
                "degree": freq[user_id]
            })
        # inner bracket [graph.get(user_id)] is to get empty list[] if NoneType
            for connected_node in [x for y in [graph.get(user_id)] if y is not
                                   None for x in y]:
                if connected_node in node_list:
                    d3_json["links"].append({
                        "source": node_list.index(user_id),
                        "target": node_list.index(connected_node)
                    })

    with open('graph.json', mode='w') as f:
        json.dump(d3_json, f)

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print 'Usage python main.py <settings.json filename> <twitter'  \
              'screenname>'
    else:
        main(sys.argv[1], sys.argv[2])
