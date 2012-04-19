# -*- coding: utf-8 -*-


from google.appengine.ext import db

# https://developers.facebook.com/docs/reference/api/user/
class User(db.Model):
    id           = db.StringProperty(required=True)
    username     = db.StringProperty(required=False)
    name         = db.StringProperty(required=False)
    access_token = db.StringProperty(required=False)
    expires      = db.StringProperty(required=False)
    indexed      = db.BooleanProperty(required=False)
    num_indexed  = db.IntegerProperty(required=False)
    last_indexed = db.DateTimeProperty(required=False)
    previous_url = db.StringProperty(required=False)



# https://developers.facebook.com/docs/reference/api/post/
class Post(db.Model):
    id             = db.StringProperty(required=True)
    from_name      = db.StringProperty(required=False)
    from_id        = db.StringProperty(required=True)
    message        = db.TextProperty(required=False)
    type           = db.StringProperty(required=False)
    created_time   = db.StringProperty(required=False) # string containing ISO-8601 date-time
    likes_count    = db.IntegerProperty(required=False)
    comments_count = db.IntegerProperty(required=False)

class InvertedIndex(db.Model):
    keyword = db.StringProperty(required=True)
    doc_ids = db.TextProperty(required=True)