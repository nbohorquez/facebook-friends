# -*- coding: utf-8 -*-

# Scrapy settings for tutorial project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

from commons import config

BOT_NAME = 'facebook-friends'

SPIDER_MODULES = ['facebook-friends.spiders']
NEWSPIDER_MODULE = 'facebook-friends.spiders'

# My XPATH searches are based in spanish language
DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'es',
}

ITEM_PIPELINES = {
  'scrapy.contrib.pipeline.images.ImagesPipeline': 1,
  'facebook-friends.pipelines.items.ItemsPipeline': 300
}
IMAGES_STORE = config.get('project', 'pictures')

# This is to force Breadth-First Search algorithm
DEPTH_PRIORITY = 1
SCHEDULER_DISK_QUEUE = 'scrapy.squeue.PickleFifoDiskQueue'
SCHEDULER_MEMORY_QUEUE = 'scrapy.squeue.FifoMemoryQueue'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'facebook-friends (+http://charlotte.zuliaworks.com)'
