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
PRODUCTION_FB_APP_ID     = '287480874659591'
PRODUCTION_FB_APP_SECRET = '758eb4feab89cdecd46c7d77e3ec84bc'

# App ID for development
DEV_FB_APP_ID     = '339326259464725'
DEV_FB_APP_SECRET = '78db54c94055b98dd65d81abc14e79ad'

if appengineutils.is_dev_server():
    FB_APP_ID     = DEV_FB_APP_ID
    FB_APP_SECRET = DEV_FB_APP_SECRET
else:
    FB_APP_ID     = PRODUCTION_FB_APP_ID
    FB_APP_SECRET = PRODUCTION_FB_APP_SECRET
    #FB_APP_ID     = DEV_FB_APP_ID
    #FB_APP_SECRET = DEV_FB_APP_SECRET