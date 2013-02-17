import cgi
import datetime
import urllib
import webapp2
import jinja2
import logging
import json
import os
import re
from django.utils import simplejson
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import uuid

jinja_environment = jinja2.Environment(
                                       loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))
token = 0

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content, date and ip address"""
    author = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    ip_address = db.StringProperty()


def guestbook_key(guestbook_name=None):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')


class MainPage(webapp2.RequestHandler):
    def get(self):
        global token

        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
                                                  guestbook_key(guestbook_name)).order('date')
        greetings = greetings_query.run()
        
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        user = users.get_current_user()
        
        if user:
            token = channel.create_channel(user.user_id())
            nickname = user.nickname()
        else:
            token = channel.create_channel(str(uuid.uuid4()))
            nickname = "Anonymous"

        
        template_values = {
            'token' : token,
            'me': nickname,
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class Message (webapp2.RequestHandler):
    
    def post(self):
       global token
       # Store the chat into database so that it can be loaded back when the page is opened again.
       guestbook_name = self.request.get('guestbook_name')
       greeting = Greeting(parent=guestbook_key(guestbook_name))
       
       if users.get_current_user():
         greeting.author = users.get_current_user().nickname()
                 
       message = self.request.get('chat')
       greeting.content = message

       ip = self.request.remote_addr
       logging.info("IP:"+ip)
       greeting.ip_address=ip
             
       if len(message) != 0:
          greeting.put()
       
       if users.get_current_user():
          nickname = users.get_current_user().nickname()
       else:
          nickname = "Anonymous"

       # Send retrieved chat, back to the client
       if len(message) != 0:
          push = {'message': message, 'user' : nickname }
          sendMessage = simplejson.dumps(push)
          channel.send_message(users.get_current_user().user_id(), sendMessage)

class OpenedPage(webapp2.RequestHandler):
    def post(self):
        a=0
        # updater().send_update()  

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/opened', OpenedPage),
                               ('/post', Message)],
                              debug=True)
def main():
  run_wsgi_app(app)

if __name__ == "__main__":
  main()
