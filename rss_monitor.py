# monitor https://threatpost.com/feed/ rss feed for new articles and print them to console

import feedparser
import time

# RSS feed url
url = 'https://threatpost.com/feed/'

# Parse the feed
feed = feedparser.parse(url)
print('Monitoring feed: ' + feed['feed']['title'])

# Get the latest article
latest_article = feed['entries'][-1]['title']
print('Latest article: ' + latest_article)

