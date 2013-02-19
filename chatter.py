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

class Greeting(db.Model):
    """Models an individual Guestbook entry with an author, content, date and ip address"""
    author = db.StringProperty()
    id = db.StringProperty()
    content = db.StringProperty(multiline=True)
    date = db.DateTimeProperty(auto_now_add=True)
    ip_address = db.StringProperty()

class ConnectedUser(db.Model):
    id = db.StringProperty()


def guestbook_key(guestbook_name=None):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

def connects_key(connects_name=None):
    return db.Key.from_path('Connects', connects_name or 'default_connects')

class MainPage(webapp2.RequestHandler):
    def get(self):

        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(
                                                  guestbook_key(guestbook_name)).order('date')
        greetings = greetings_query.run()

        connects_name=self.request.get('connects_name')
        connects_query = ConnectedUser.all().ancestor(connects_key(connects_name))
        connects = connects_query.run()
        
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
            my_id = user.user_id()
        else:
            if self.request.cookies.get('user_id'):
               my_id = self.request.cookies.get('user_id')
            else:
               my_id = str(uuid.uuid4()).replace("-",'')
               self.response.headers.add_header( 
                         'Set-Cookie', 'user_id='+my_id+'; expires=31-Dec-2020 23:59:59 GMT')
            token = channel.create_channel(my_id)
            nickname = "Anonymous" 
        
        template_values = {
            'token' : token,
            'me': nickname,
            'my_id': my_id, 
            'greetings': greetings,
            'url': url,
            'url_linktext': url_linktext,
        }

        template = jinja_environment.get_template('index.html')
        self.response.out.write(template.render(template_values))

class Message (webapp2.RequestHandler):
    
    def post(self):
       # Store the chat into database so that it can be loaded back when the page is opened again.
       guestbook_name = self.request.get('guestbook_name')
       greeting = Greeting(parent=guestbook_key(guestbook_name))

       connects_name = self.request.get('connects_name')
       connects_query = ConnectedUser.all().ancestor(connects_key(connects_name))
       connects = connects_query.run()

       user = db.GqlQuery("SELECT * FROM ConnectedUser")
       
       if users.get_current_user():
         greeting.author = users.get_current_user().nickname()
         greeting.id = users.get_current_user().user_id();
       else: 
         greeting.author = "Anonymous"
         greeting.id = self.request.cookies.get('user_id')
                 
       message = self.request.get('chat')
       greeting.content = message

       ip = self.request.remote_addr
       greeting.ip_address=ip
             
       if len(message) != 0:
          greeting.put()
       
       if users.get_current_user():
          nickname = users.get_current_user().nickname()
          my_id = users.get_current_user().user_id()
       else:
          nickname = "Anonymous"
          my_id = self.request.cookies.get('user_id')
       
       # Send retrieved chat, back to all clients
       if len(message) != 0:
          push = {'message': message, 'user' : nickname, 'my_id' : my_id }
          sendMessage = simplejson.dumps(push)
          for user in connects:
               channel.send_message(user.id, sendMessage)

class OpenedPage(webapp2.RequestHandler):
    def post(self):
	
       connects_name = self.request.get('connects_name')
       connects_query = ConnectedUser.all().ancestor(connects_key(connects_name))
       connects = connects_query.run()
       new_user = ConnectedUser(parent=connects_key(connects_name))

       user = db.GqlQuery("SELECT * FROM ConnectedUser") 
   
       if(users.get_current_user()):
           new_user.id = users.get_current_user().user_id()
       else:
           new_user.id = self.request.cookies.get('user_id')

       if connects_query.count() == 0:
          new_user.put()
       
       found = False

       for user in connects:
          if user.id==new_user.id:
             found = True
             break
       
       if found==False:
          new_user.put() 

app = webapp2.WSGIApplication([('/', MainPage),
                               ('/opened', OpenedPage),
                               ('/post', Message)],
                              debug=True)
def main():
  run_wsgi_app(app)

if __name__ == "__main__":
  main()
