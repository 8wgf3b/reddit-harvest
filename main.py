from tqdm import tqdm
from mining import recent_authors, user_text, all_stats, thirty_stats
from time import sleep
import sys


def live_mine(limit=500, subreddit=None):
    limit = int(limit)
    auth_list = recent_authors(subreddit, limit)
    for user in tqdm(auth_list):
        all_stats(user)
        thirty_stats(user)
        user_text(user)
        sleep(1)


if __name__ == '__main__':
    arg = sys.argv
    if arg[1] == 'live':
        live_mine(*arg[2:])
