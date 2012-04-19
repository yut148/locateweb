# -*- coding: utf-8 -*-

import uuid
import urllib
import urllib2
import urlparse
import hashlib
import json
import os
import datetime
import logging

import jinja2
import webapp2

from google.appengine.ext import db
from google.appengine.ext.db import Key

import settings
from models import User
from crawler import crawl, INITIAL_CRAWL, NEXT_CRAWL, PREVIOUS_CRAWL
from searcher import search
from crawler_task import task_crawl

class UtcTzinfo(datetime.tzinfo):
    def utcoffset(self, dt): return datetime.timedelta(0)
    def dst(self, dt): return datetime.timedelta(0)
    def tzname(self, dt): return 'UTC'
    def olsen_name(self): return 'UTC'

class PstTzinfo(datetime.tzinfo):
    def utcoffset(self, dt):
        return datetime.timedelta(hours=-8) + self.dst(dt)
    def _FirstSunday(self, dt):
        return dt + datetime.timedelta(days=(6-dt.weekday()))
    def dst(self, dt):
        dst_start = self._FirstSunday(datetime.datetime(dt.year, 3, 8, 2))
        dst_end = self._FirstSunday(datetime.datetime(dt.year, 11, 1, 1))
        if dst_start <= dt.replace(tzinfo=None) < dst_end:
            return datetime.timedelta(hours=1)
        else:
            return datetime.timedelta(hours=0)
    def tzname(self, dt):
        if self.dst(dt) == datetime.timedelta(hours=0):
            return "PST"
        else:
            return "PDT"

''' Jinja 2 '''
jinja_environment = jinja2.Environment(loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

def datetime_format(value, format='%m/%d/%Y %H:%M%p'):
    return value.replace(tzinfo=UtcTzinfo()).astimezone(PstTzinfo()).strftime(format)

def short_datetime_format(value, format='%m/%d %H:%M%p'):
    return value.replace(tzinfo=UtcTzinfo()).astimezone(PstTzinfo()).strftime(format)

jinja_environment.filters['datetimeformat']      = datetime_format
jinja_environment.filters['shortdatetimeformat'] = short_datetime_format


# Error
def error(handler, message):
    template_values = {'error_message':message}
    template = jinja_environment.get_template('templates/error.html')
    handler.response.out.write(template.render(template_values))

class MainHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('MainHandler : GET')
        template = jinja_environment.get_template('templates/index.html')
        self.response.out.write(template.render({}))

class LoginHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('LoginHandler : GET')
        state = hashlib.md5(str(uuid.uuid4())).hexdigest()
        logging.info('state: %s' % state)
        params = dict()
        params['client_id']     = settings.FB_APP_ID
        params['redirect_uri']  = settings.FACEBOOK_AUTH_CALLBACK_URL
        params['state'] = state
        #params['scope'] = 'read_stream,read_mailbox'
        params['scope'] = 'read_stream'
        url ='https://www.facebook.com/dialog/oauth?%s' % urllib.urlencode(params)
        logging.info('url: %s', url)
        self.response.out.write('<html><head><script type=\'text/javascript\'>window.location=\'' + url+ '\'</script></head></html>')

class LogoutHandler(webapp2.RequestHandler):
    def get(self):
        logging.info('LogoutHandler : GET')
        self.response.delete_cookie('user_id')
        self.redirect('/')

class DeleteHandler(webapp2.RequestHandler):
    def get(self):
        user_id = self.request.cookies.get('user_id')
        logging.info('DeleteHandler : GET : user_id=%s' % user_id)
        key = Key.from_path('User', user_id)
        q = db.Query()
        q.ancestor(key)
        while True:
            results = q.fetch(50, 0)
            if not len(results):
                break
            db.delete(results)
        db.delete(key)
        self.response.delete_cookie('user_id')
        self.redirect('/')

class FacebookAuthenticationCallback(webapp2.RequestHandler):
    def get(self):
        logging.info('FacebookAuthenticationCallback : GET')
        code   = self.request.get('code')
        state  = self.request.get('state')
        logging.info('code: %s'  % code)
        logging.info('state: %s' % state)
        params = dict()
        params['client_id']     = settings.FB_APP_ID
        params['redirect_uri']  = settings.FACEBOOK_AUTH_CALLBACK_URL
        params['client_secret'] = settings.FB_APP_SECRET
        params['code']          = code
        url ='https://graph.facebook.com/oauth/access_token?%s' % urllib.urlencode(params)
        logging.info('url: %s', url)
        access_token = None
        expires = None
        try:
            result = urllib2.urlopen(url)
            data = result.read()
            logging.info(data)
            d = urlparse.parse_qs(data)
            access_token = d['access_token'][0]
            expires = d['expires'][0]
            logging.info(d)
        except urllib2.URLError, e:
            logging.error(e)
            logging.error(e.read())
            error(self, e.read())
            return

        logging.info(access_token)
        logging.info(expires)
        url = 'https://graph.facebook.com/me?access_token=%s' % access_token
        logging.info('url: %s', url)
        user_data = None
        try:
            result = urllib2.urlopen(url)
            data = result.read()
            logging.info(data)
            user_data = json.loads(data)
        except urllib2.URLError, e:
            logging.error(e)
            logging.error(e.read())
            error(self, e.read())
            return
        if 'username' not in user_data:
            user_data['username'] = ''
        user = User.get_by_key_name(user_data['id'])
        if user:
            user.username=user_data['username']
            user.name=user_data['name']
            user.access_token=access_token
            user.expires=expires
        else:
            user = User(key_name=user_data['id'],
                id=user_data['id'],
                username=user_data['username'],
                name=user_data['name'],
                access_token=access_token,
                expires=expires)
        user.put()

        self.response.set_cookie('user_id', user_data['id'])
        self.redirect('/search')

        task_crawl(user_id=user_data['id'])


class CrawlHandler(webapp2.RequestHandler):
    def post(self):
        user_id = self.request.get('user_id')
        logging.info('[CrawlHandler:POST] user_id: [%s]' % user_id)
        crawl(user_id, INITIAL_CRAWL, None)

class CrawlNextHandler(webapp2.RequestHandler):
    def post(self):
        user_id = self.request.get('user_id')
        url     = self.request.get('url')
        logging.info('[CrawlNextHandler:POST] user_id: [%s] url: [%s]' % (user_id, url))
        crawl(user_id,NEXT_CRAWL,url)

class CrawlPreviousHandler(webapp2.RequestHandler):
    def post(self):
        user_id = self.request.get('user_id')
        url     = self.request.get('url')
        logging.info('[CrawlPreviousHandler:POST] user_id: [%s] url: [%s]' % (user_id, url))
        crawl(user_id, PREVIOUS_CRAWL,url)

class SearchHandler(webapp2.RequestHandler):
    def get(self):
        user_id = self.request.cookies.get('user_id')
        logging.info('[SearchHandler:GET] user_id: [%s]' % user_id)
        if user_id is None or len(user_id) == 0:
            self.redirect("/")
            return
        q = self.request.get('q')
        p = self.request.get('p')
        logging.info('[SearchHandler:GET] q: [%s] p:[%s]' % (q, p))
        user = User.get_by_key_name(user_id,parent=None)
        posts = search(user, q, p)
        results = []
        for post in posts:
            if post:
                ids = post.id.split('_')
                result ={}
                result['from_name'] = post.from_name
                result['created_time'] = post.created_time
                result['date_time'] = datetime.datetime.strptime(post.created_time, '%Y-%m-%dT%H:%M:%S+0000')
                result['message'] = post.message
                result['url'] = 'http://www.facebook.com/'+ids[0]+'/posts/' + ids[1]
                results.append(result)
        template_values = {
            'user':user,
            'logout_url':settings.LOGOUT_URL,
            'results': results,
            'query': q,
            'phrase':p
        }
        template = jinja_environment.get_template('templates/search.html')
        self.response.out.write(template.render(template_values))