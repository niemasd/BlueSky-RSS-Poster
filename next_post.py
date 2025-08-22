#! /usr/bin/env python3
'''
Print the text of the next BlueSky post to stdout, or print nothing if there are no new posts.
'''

# imports
from datetime import datetime
from pathlib import Path
from sys import argv, stderr, stdout
from urllib.request import urlopen
from xml.etree import ElementTree

# constants
POSTS_DELIM = '=== NIEMA POSTS DELIM ==='
CHAR_LIMIT = 300

# print warning message
def warn(s, end='\n', file=stderr):
    print(s, end=end, file=file)

# print error message and exit
def error(s, end='\n', file=stderr, status=1):
    warn(s, end=end, file=file); exit(status)

# run script
if __name__ == "__main__":
    # check user args
    if len(argv) != 3 or argv[1].replace('-','').strip().lower() in {'h','help'}:
        error("USAGE: %s <feeds.txt> <posts.txt>" % argv[0])
    feeds_path = Path(argv[1])
    posts_path = Path(argv[2])
    for p in [feeds_path, posts_path]:
        if not p.is_file():
            error("File not found: %s" % p)

    # load old posts
    with open(posts_path, 'rt') as posts_f:
        old_posts = {s.strip() for s in posts_f.read().split(POSTS_DELIM)}

    # load RSS feed URLs
    with open(feeds_path, 'rt') as feeds_f:
        feed_urls = [l.strip() for l in feeds_f]
    feed_urls = [l for l in feed_urls if l != '' and not l.startswith('#')] # remove empty and comment lines

    # determine and print next post
    for url in feed_urls:
        # try to load current RSS feed
        try:
            with urlopen(url) as url_f:
                url_data = url_f.read()
        except:
            warn("Unable to download data from URL: %s" % url); continue

        # try to parse current RSS feed data as XML
        try:
            rss_root = ElementTree.fromstring(url_data)
        except:
            warn("Unable to parse valid RSS from URL: %s" % url); continue

        # try to load global information about this RSS feed
        try:
            rss_channel_root = rss_root.find('channel')
            try:
                channel_title = rss_channel_root.find('title').text.strip()
            except:
                channel_title = ''
        except:
            pass

        # iterate over RSS items (reverse order since first is usually the newest item)
        for curr_item in list(rss_root.iter('item'))[::-1]:
            # parse current RSS item
            try:
                curr_title = curr_item.find('title').text.strip()
            except:
                curr_title = ''
            try:
                curr_link = curr_item.find('link').text.strip()
            except:
                curr_link = ''
            try:
                curr_pubDate = curr_item.find('pubDate').text.strip()
            except:
                curr_pubDate = ''

            # build post for current RSS item, and if it's new, print it
            curr_post = ''
            for s in [curr_link, curr_pubDate, channel_title, curr_title]:
                if s != '':
                    curr_post += (s + '\n')
            curr_post = curr_post.strip()[:CHAR_LIMIT].strip()
            if curr_post not in old_posts:
                print(curr_post); exit()
