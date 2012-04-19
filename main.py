import logging
import webapp2
import settings

from views import *

logging.getLogger().setLevel(logging.DEBUG)

app = webapp2.WSGIApplication([
            ('/',       MainHandler),
            ('/login',  LoginHandler),
            ('/logout', LogoutHandler),
            ('/delete', DeleteHandler),
            ('/search', SearchHandler),
            (settings.FACEBOOK_AUTH_CALLBACK_PATH, FacebookAuthenticationCallback),
            ('/crawl', CrawlHandler),
            ('/crawlnext', CrawlNextHandler),
            ('/crawlprevious', CrawlPreviousHandler)
            ], debug=True)

