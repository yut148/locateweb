# -*- coding: utf-8 -*-


import appengineutils

PRODUCTION_BASE_URL  = 'https://locateweb.appspot.com'
DEVELOPMENT_BASE_URL = 'http://localhost:8080'
ONLINE_DEVLEOPMENT_BASE_URL  = 'https://locatewebdev.appspot.com'

if appengineutils.is_dev_server():
    SELF_URL = DEVELOPMENT_BASE_URL
else:
    SELF_URL = PRODUCTION_BASE_URL
    #SELF_URL = ONLINE_DEVLEOPMENT_BASE_URL

# logout url
LOGOUT_URL = SELF_URL + '/logout'

# Callback path for Facebook
FACEBOOK_AUTH_CALLBACK_PATH = '/facebookauthcallback/'
FACEBOOK_AUTH_CALLBACK_URL = SELF_URL + FACEBOOK_AUTH_CALLBACK_PATH

# Facebook API
# App ID for production
PRODUCTION_FB_APP_ID     = '<YOUR APP ID>'
PRODUCTION_FB_APP_SECRET = '<YOUR APP SECRET>'

# App ID for development
DEV_FB_APP_ID     = '<YOUR APP ID>'
DEV_FB_APP_SECRET = '<YOUR APP SECRET>'

if appengineutils.is_dev_server():
    FB_APP_ID     = DEV_FB_APP_ID
    FB_APP_SECRET = DEV_FB_APP_SECRET
else:
    FB_APP_ID     = PRODUCTION_FB_APP_ID
    FB_APP_SECRET = PRODUCTION_FB_APP_SECRET
    #FB_APP_ID     = DEV_FB_APP_ID
    #FB_APP_SECRET = DEV_FB_APP_SECRET