from tqdm import tqdm
from mining import all_stats, thirty_stats
from mining import recent_authors, top_authors_avg, top_authors_sum
from mining import save_output as graph_output
from time import sleep
import sys



def mine(type, limit=500, subreddit=None):
    mining_dict = {
        'live': recent_authors,
        'sum': top_authors_sum,
        'avg': top_authors_avg
    }
    limit = int(limit)
    auth_list = mining_dict[type](subreddit, limit)
    for user in tqdm(auth_list):
        all_stats(user)
        thirty_stats(user)
        sleep(1)


if __name__ == '__main__':
    arg = sys.argv
    try:
        mine(*arg[1:])
    except KeyError:
        graph_output(*arg[1:])
