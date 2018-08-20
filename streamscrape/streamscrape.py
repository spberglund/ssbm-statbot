'''
streamscrape.py
includes tools to get gifs and videos from online sources of SSBM gameplay
Spencer Berglund 4/4/2018
'''

import requests
import shutil
import json
import re
import os
import sys
import datetime
from pathos.pools import ThreadPool
import cv2

############ Global Parameters ############
SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))
DOWNLOADS_DIR = os.path.join(SCRIPT_DIR, 'downloads')

DEFAULT_REQUEST_HEADERS = {
    'User-Agent': 'streamscrape 0.1',
    'From': 'spberglund@gmail.com'
}

############ Initialization ############
if not os.path.exists(DOWNLOADS_DIR): os.mkdir(DOWNLOADS_DIR)

############ Functions ############
def json_webget(url):
    resp = requests.get(url, headers=DEFAULT_REQUEST_HEADERS)
    return json.loads(resp.text)

def save_file_from_web(url, localfilepath):
    resp = requests.get(url, headers=DEFAULT_REQUEST_HEADERS, stream=True)
    if resp.status_code != 200: return None

    with open(localfilepath, 'wb') as f:
        shutil.copyfileobj(resp.raw, f)

    del resp
    return localfilepath

def create_timestamped_dir():
    dirName = os.path.join(DOWNLOADS_DIR, datetime.datetime.utcnow().isoformat().split('.')[0].replace(':', '-'))
    if not os.path.exists(dirName): os.mkdir(dirName)
    return dirName

def get_reddit_posts(subreddit, pages = 1):

    content = []
    urlParams = ''
    for i in range(pages):
        respObj = json_webget('http://www.reddit.com/{}/.json{}'.format(subreddit, urlParams))
        posts = respObj['data']['children']

        content.extend(posts)
        urlParams = '?after=' + posts[-1]['data']['name']

    return content

def get_melee_gif_urls(pages = 1):
    # filter to include only melee posts
    smashPosts = get_reddit_posts('/r/smashgifs', pages);
    meleePosts = filter(lambda post: post['data']['link_flair_text'] == 'Melee', smashPosts)
    meleeUrls = map(lambda post:post['data']['url'], meleePosts)

    return meleeUrls

def get_gfycat_metadata(gfycatID):
    return json_webget('https://gfycat.com/cajax/get/' + gfycatID)['gfyItem']

#Currently only works for gfycat
def download_gif(url, savedir, fmt = 'mp4'):
    gfyFormats = {'mp4': 'mp4Url', 'webm': 'webmUrl', 'webp': 'webpUrl', 'gif': 'gifUrl'}
    fmt = fmt.lower()

    gfyMatch = re.match(r'^https?://gfycat.com/(\w+)$', url)

    if not gfyMatch: return None #Not a gfycat url

    gfycatID = gfyMatch.group(1)
    gfycatData = get_gfycat_metadata(gfycatID)

    gfyUrl = gfycatData[gfyFormats[fmt]]

    fileName = '{}.{}'.format(gfycatID, fmt)
    filePath = os.path.join(savedir, fileName)

    print('downloading {} to {}'.format(gfyUrl, fileName))

    return save_file_from_web(gfyUrl, filePath)

def convert_gif_to_images(gifPath):
    destDir = gifPath.rsplit('.', 1)[0]
    if os.path.exists(destDir): return None
    os.mkdir(destDir)

    print('converting {} to images'.format(os.path.basename(gifPath)))

    vidcap = cv2.VideoCapture(gifPath)

    success, image = vidcap.read()
    count = 0
    success = True
    while success:
        cv2.imwrite(os.path.join(destDir, "frame_{:06d}.jpg".format(count)), image)     # save frame as JPEG file
        success, image = vidcap.read()
        count += 1

    print('generated {} images from {}'.format(count, os.path.basename(gifPath)))

    return destDir

def download_gif_and_convert_to_images(url, savedir, fmt = 'mp4'):
    gifPath = download_gif(url, savedir, fmt)
    if not gifPath: return None

    return convert_gif_to_images(gifPath)

def download_top_melee_gifs(pages = 1):
    print('Looking for gifs on the top {} reddit pages'.format(pages))

    saveDir = create_timestamped_dir()
    print('Will save to {}'.format(saveDir))

    urls = get_melee_gif_urls(pages)
    print('Found {} gif urls'.format(len(urls)))

    pool = ThreadPool(50)
    results = pool.map(lambda url:download_gif_and_convert_to_images(url, saveDir), urls)

    print('Done downloading and converting {} gifs'.format(len(filter(None, results))))

if __name__ == '__main__':
    numPages = 1 #default number of pages to load
    if len(sys.argv) == 2:
        numPages = int(sys.argv[1])

    download_top_melee_gifs(numPages)