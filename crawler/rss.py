import json
from time import mktime

from feedparser import parse

from common.models import Item


class RSSFeed():
    url = ''
    source = ''
    type = 'link'

    def __init__(self, url):
        self.url = url

    def crawl(self):
        feed = parse(self.url)
        feed_items = feed['items']
        for feed_item in feed_items:
            item = Item()
            item.title = feed_item['title'] if feed_item.has_key('title') else ''
            item.content = feed_item['summary'] if feed_item.has_key('summary') else ''
            if feed_item.has_key('published_parsed') and feed_item['published_parsed']:
                item.created_on = mktime(feed_item['published_parsed']) * 1000
            meta = {
                'protocol': 'rss',
                'type': self.type,
                'link': feed_item['link'] if feed_item.has_key('link') else '',
            }
            item.source = self.source
            item.meta = json.dumps(meta)
            item.save()

