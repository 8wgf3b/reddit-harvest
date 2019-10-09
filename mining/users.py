import praw
import json, os, re, shutil, sys
import requests
from tqdm import tqdm

def save_user(username, period=None, saveloc='users/', tosave=['stats']):
    pass


def get_user_text(username, period=None, data_type='stats'):
    sub_address = 'https://api.pushshift.io/reddit/submission/search'
    comm_address = 'https://api.pushshift.io/reddit/comment/search'
    params = {
        'author': username,
        'size': 500,
    }
    if period is not None:
        params['after'] = '{}d'.format(period)
    if data_type == 'stats':
        params['size'] = 0
        params['aggs'] = 'subreddit'
        s = requests.get(sub_address, params=params).json()['aggs']['subreddit']
        c = requests.get(comm_address, params=params).json()['aggs']['subreddit']
        s = defaultdict(int, [(x['key'], x['doc_count']) for x in s])
        c = defaultdict(int, [(x['key'], x['doc_count']) for x in c])
        for k in c:
            s[k] += c[k]
        return s

    elif data_type == 'submission':
        params['fields'] = ('title', 'selftext', 'created_utc')
        titles = set()
        iteration = 1
        while True:
            if iteration > 1:
                params.update({'before': r[-1]['created_utc']})
            r = requests.get(sub_address, params=params).json()['data']
            if len(r) == 0:
                break
            for post in r:
                title = post['title']
                body = post['selftext'] if post['selftext'] is not None else ''
                if title not in titles:
                    titles.add(title)
                    yield(title)
                    yield(body)
            iteration = iteration + 1

    elif data_type == 'comment':
        params['fields'] = ('body', 'created_utc')
        iteration = 1
        while True:
            if iteration > 1:
                params.update({'before': r[-1]['created_utc']})
            r = requests.get(comm_address, params=params).json()['data']
            if len(r) == 0:
                break
            for comment in r:
                yield(comment['body'])
            iteration = iteration + 1


def download_file(url, outputFile):
    with requests.get(url, stream=True) as r:
        with open(outputFile, 'wb') as f:
            shutil.copyfileobj(r.raw, f)

#u/jackacooper's code
def get_user_media(username, period=None, save_loc='users/'):
    iteration = 1
    posts = dict()
    sub_address = 'https://api.pushshift.io/reddit/submission/search'
    comm_address = 'https://api.pushshift.io/reddit/comment/search'
    params = {
            'author': username,
            'fields': ('url', 'title', 'created_utc'),
            'size': 500,
             }
    if period is not None:
        params['after'] = '{}d'.format(period)
    while True:
        if iteration > 1:
            params.update({'before': r[-1]['created_utc']})
        r = requests.get(sub_address, params=params).json()['data']
        if len(r) == 0:
            break
        for post in r:
          posts[post['title']] = post['url']
        iteration = iteration + 1

    directory = save_loc + username
    if not os.path.exists(directory):
        os.makedirs(directory)

    for (rawTitle, rawUrl) in tqdm(posts.items()):
        urls = dict()
        try:
            title = rawTitle.encode('ascii', 'ignore').decode('ascii').rstrip('.')
            rawExt = rawUrl.split('.')[-1]
            if 'reddit.com' in rawUrl and '/comments/' in rawUrl:
                pass
            elif 'youtube.com' in rawUrl:
                pass
            elif 'gfycat' in rawUrl:
                name =  rawUrl.split('/')[-1]
                g = requests.get('https://api.gfycat.com/v1/gfycats/' + name)
                urls[g.json()['gfyItem']['mp4Url']] = 'mp4'
            elif 'imgur.com/a/' in rawUrl:
                g = requests.get(rawUrl)
                # Imgur API requires auth, however albums embed json in the html
                # to avoid auth restriction.
                j = json.loads(re.findall('(?<=image               : ).*', g.text)[0].rstrip(','))
                c = 1
                for i in j['album_images']['images']:
                    urls['https://i.imgur.com/' + i['hash'] + i['ext']] =  str(c) + i['ext']
                    c = c + 1
            elif 'imgur.com' in rawUrl and 'gifv' in rawUrl:
                # Prevent trying downloading invalid formats, could also download gif
                urls[rawUrl.replace('gifv', 'mp4')] = 'mp4'
            elif rawUrl[-1] == '/':
                continue
            else:
                urls[rawUrl] = rawExt
            for (url, ext) in urls.items():
                if ext.lower() not in ['mp4', 'webm', 'jpg', 'jpeg', 'png', 'gif']:
                    xl = rawUrl.lower()
                    if ext[0].isdigit():
                        ext = ext
                    elif 'mp4' in xl:
                        ext = 'mp4'
                    elif 'webm' in xl:
                        ext = 'webm'
                    elif 'jpg' in xl or 'jpeg' in xl:
                        ext = 'jpg'
                    elif 'png' in xl:
                        ext = 'png'
                    elif 'gif' in xl:
                        ext = 'gif'
                    else:
                        print('FIXME: {}'.format(rawUrl))
                        pass
                download_file(url, directory + '/' + title + '.' + ext)
        except Exception as e:
            print(e)
            continue
    shutil.make_archive(directory, 'zip', directory)
    shutil.rmtree(directory)
    path = directory + '.zip'
    return save_loc + path


if __name__ == '__main__':
    pass
