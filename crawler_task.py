# -*- coding: utf-8 -*-

import logging
from google.appengine.api import taskqueue

def task_crawl(user_id):
    logging.info('task_crawl: user_id=%s' % user_id)
    taskqueue.add(url='/crawl', params={'user_id': user_id})

def task_crawl_next(user_id, url):
    logging.info('task_crawl_next: user_id=%s url=%s' % (user_id,url))
    taskqueue.add(url='/crawlnext', params={'user_id': user_id, 'url':url})

def task_crawl_previous(user_id, url):
    logging.info('task_crawl_previous: user_id=%s' % user_id)
    taskqueue.add(url='/crawlprevious', params={'user_id': user_id, 'url':url})