import logging
import urllib2
import json
import datetime

from google.appengine.ext import db

from models import User, Post
from indexer import add_page_to_index, store_index_in_db
from crawler_task import task_crawl_previous, task_crawl_next

INITIAL_CRAWL  = 0
NEXT_CRAWL     = 1
PREVIOUS_CRAWL = 2

def crawl(user_id,type=INITIAL_CRAWL, url=None):
    # retrieve user info
    user = User.get_by_key_name(user_id)

    if type == INITIAL_CRAWL:
        # already indexed, ignore
        if user.indexed:
            logging.info('Already crawled %d for %s' % (user.num_indexed, user_id))
            task_crawl_previous(user_id, user.previous_url)
            return

        # Initial crawl url
        url = 'https://graph.facebook.com/%s/posts?access_token=%s' % (user.id, user.access_token)

    logging.info('start crawl: type=%d user_id=%s url=%s' % (type, user_id, url))

    try:
        result = urllib2.urlopen(url)
        data = result.read()
        logging.info(data)
        json_data = json.loads(data)
        posts = []
        index = {}
        for entity in json_data['data']:
            if 'message' in entity:
                post = Post(parent=user,key_name=entity['id'],id = entity['id'],from_name = entity['from']['name'],from_id=entity['from']['id'])
                post.message = entity['message']
                post.type = entity['type']
                post.created_time = entity['created_time']
                post.likes_count = 0
                if 'likes' in entity:
                    post.likes_count = entity['likes']['count']
                post.comments_count = 0
                if 'comments' in entity:
                    post.comments_count =entity['comments']['count']
                add_page_to_index(index, entity['id'], entity['message'])
                posts.append(post)
        if len(posts):
            # store posts
            db.put(posts)
            store_index_in_db(index, user)

        # store previous url in queue
        if type == INITIAL_CRAWL:
            if 'paging' in json_data:
                if 'previous' in json_data['paging']:
                    previous = json_data['paging']['previous']
                    logging.info(previous)
                    if len(previous) > 0:
                        user.previous_url = previous

        # update user
        count = 0
        if type != INITIAL_CRAWL:
            count = user.num_indexed
        user.num_indexed = count + len(posts)
        user.last_indexed = datetime.datetime.now()
        user.indexed = True
        user.put()

        # create task for next or previous page
        if 'paging' in json_data:
            if type == INITIAL_CRAWL or type == NEXT_CRAWL:
                # store next url in queue
                if 'next' in json_data['paging']:
                    next = json_data['paging']['next']
                    logging.info(next)
                    if len(next) > 0:
                        task_crawl_next(user_id, next)
            elif type == PREVIOUS_CRAWL:
                # store previous url in queue
                if 'previous' in json_data['paging']:
                    previous = json_data['paging']['previous']
                    logging.info(previous)
                    if len(previous) > 0:
                        task_crawl_previous(user_id, previous)
    except urllib2.URLError, e:
        logging.error(e)
        logging.error(e.read())