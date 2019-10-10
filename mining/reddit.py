import requests
from random import random
from functools import partial


def recent_authors(subreddit=None, total=100, c_ratio=random()):
    total = 500 if total > 500 else total
    sub_address = 'https://api.pushshift.io/reddit/submission/search'
    comm_address = 'https://api.pushshift.io/reddit/comment/search'
    params = {
        'fields': 'author'
    }
    if subreddit is not None:
        params['subreddit'] = subreddit
    auth_list = []
    params['size'] = int(round(total * (1 - c_ratio)))
    r = requests.get(sub_address, params=params).json()['data']
    auth_list.extend([x['author'] for x in r])
    params['size'] = int(round(total * c_ratio))
    r = requests.get(comm_address, params=params).json()['data']
    auth_list.extend([x['author'] for x in r])
    return list(set(auth_list) - {"AutoModerator", "[deleted]"})


def top_authors(subreddit=None, total=100, type='avg', period=30):
    comm_address = 'https://api.pushshift.io/reddit/comment/search'
    params = {
        'size': 0,
        'agg_size': total,
        'metadata': True,
        'aggs': 'author:score:' + type
    }
    if period is not None:
        params['after'] = '{}d'.format(period)
    if subreddit is not None:
        params['subreddit'] = subreddit
    r = requests.get(comm_address, params=params).json()['aggs']['author:score']
    auth_list = [x['key'] for x in r]
    return list(set(auth_list) - {"AutoModerator", "[deleted]"})


top_authors_avg = partial(top_authors, type='avg', period=30)
top_authors_sum = partial(top_authors, type='sum', period=30)


if __name__ == '__main__':
    print(top_authors_sum('the_donald'))
