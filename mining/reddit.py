import requests
from random import random


def recent_authors(subreddit=None, total=100, c_ratio=random()):
    total = 500 if total > 500 else total
    sub_address = 'https://api.pushshift.io/reddit/submission/search'
    comm_address = 'https://api.pushshift.io/reddit/comment/search'
    params = {
        'fields': 'author'
    }
    if subreddit is not None:
        param['subreddit'] = subreddit
    auth_list = []
    params['size'] = int(round(total * (1 - c_ratio)))
    r = requests.get(sub_address, params=params).json()['data']
    auth_list.extend([x['author'] for x in r])
    params['size'] = int(round(total * c_ratio))
    r = requests.get(comm_address, params=params).json()['data']
    auth_list.extend([x['author'] for x in r])
    return list(set(auth_list))


if __name__ == '__main__':
    print(recent_authors())
