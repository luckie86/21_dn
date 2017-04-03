from google.appengine.ext import ndb

class Opinion(ndb.Model):
    first_last_name = ndb.StringProperty()
    email = ndb.StringProperty()
    opinion = ndb.StringProperty()
    time = ndb.DateTimeProperty(auto_now_add=True)
    deleted = ndb.BooleanProperty(default=False)