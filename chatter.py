# Copyright (c) Baris Tevfik
# refer to License.txt
import cgi
import datetime
import urllib
import webapp2
import jinja2
import logging
import json
import os
import re
from google.appengine.ext import db
from google.appengine.api import users
from google.appengine.api import channel
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
import uuid
import hashlib

jinja_environment = jinja2.Environment(
                                       loader=jinja2.FileSystemLoader(os.path.dirname(__file__)))

#Greeting to hold each chat entry
class Greeting(db.Model):
    author = db.StringProperty() #the author nickname (email or anonymous)
    id = db.StringProperty() #author id
    content = db.StringProperty(multiline=True)  #the content
    date = db.DateTimeProperty(auto_now_add=True) #date of entry
    ip_address = db.StringProperty() #ip address of the author

#Connected user entry to hold the id of the user
class ConnectedUser(db.Model):
    id = db.StringProperty()

#Keys for entities
def guestbook_key(guestbook_name=None):
    """Constructs a Datastore key for a Guestbook entity with guestbook_name."""
    return db.Key.from_path('Guestbook', guestbook_name or 'default_guestbook')

def connects_key(connects_name=None):
    return db.Key.from_path('Connects', connects_name or 'default_connects')

#When main page is loaded this function is called first
class MainPage(webapp2.RequestHandler):
    def get(self):

        #get datastore entities
        guestbook_name=self.request.get('guestbook_name')
        greetings_query = Greeting.all().ancestor(guestbook_key(guestbook_name)).order('date')
        greetings = greetings_query.run()

        connects_name=self.request.get('connects_name')
        connects_query = ConnectedUser.all().ancestor(connects_key(connects_name))
        
        #get login/logout links
        if users.get_current_user():
            url = users.create_logout_url(self.request.uri)
            url_linktext = 'Logout'
        else:
            url = users.create_login_url(self.request.uri)
            url_linktext = 'Login'
        
        #get current user
        user = users.get_current_user()
     
        #if the user is logged in
        if user:
            #create a token, get nickname and id
            userID = user.user_id()
            salt = 'thisIsaVeryLongSaltThatWillBeUsedToSalt'
            my_id = hashlib.sha1('%s$%s' % (userID, salt)).hexdigest()
            token = channel.create_channel(my_id)
            nickname = user.nickname()
        #if the user is not logged in (anonymous)
        else:
            #if the anonymous user has been around before and has an id stored in cookie
            if self.request.cookies.get('user_id'):
               my_id = self.request.cookies.get('user_id')
            #if not create a cookie
            else:
               my_id = str(uuid.uuid4()).replace("-",'')
               self.response.headers.add_header( 
                         'Set-Cookie', 'user_id='+my_id+'; expires=31-Dec-2020 23:59:59 GMT')
            #create a token and assign a nickname
            token = channel.create_channel(my_id)
            nickname = "Anonymous" 
        
        #inject thes values into client
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

#A message is received
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
         userID = users.get_current_user().user_id()
         salt = 'thisIsaVeryLongSaltThatWillBeUsedToSalt'
         logged_user_id =  hashlib.sha1('%s$%s' % (userID, salt)).hexdigest()
         greeting.id = logged_user_id
       else: 
         greeting.author = "Anonymous"
         greeting.id = self.request.cookies.get('user_id')
                 
       message = self.request.get('chat')
       greeting.content = message

       ip = self.request.remote_addr
       greeting.ip_address=ip
             
       if len(message) != 0:
          greeting.put()
       
       ###########################################################

       # Send the received message to all users stored in connected users database
       if users.get_current_user():
          nickname = users.get_current_user().nickname()
          my_id = logged_user_id
       else:
          nickname = "Anonymous"
          my_id = self.request.cookies.get('user_id')
      
       if len(message) != 0:
          push = {'message': message, 'user' : nickname, 'my_id' : my_id }
          sendMessage = json.dumps(push)
          for user in connects:
               channel.send_message(user.id, sendMessage)

#A channel is opened by a client
class OpenedPage(webapp2.RequestHandler):
    def post(self):

       connects_name = self.request.get('connects_name')
       connects_query = ConnectedUser.all().ancestor(connects_key(connects_name))
       connects = connects_query.run()
       new_user = ConnectedUser(parent=connects_key(connects_name))

       user = db.GqlQuery("SELECT * FROM ConnectedUser") 
   
       # if there the user is logged in
       if(users.get_current_user()):
           userID = users.get_current_user().user_id()
           salt = 'thisIsaVeryLongSaltThatWillBeUsedToSalt'
           new_user.id = hashlib.sha1('%s$%s' % (userID, salt)).hexdigest() 
       #if the user is anonymous then the id is stored in a cookie when MainPage is called, retreive that
       else:
           new_user.id = self.request.cookies.get('user_id')

       #Put the user id into connected users database if it doesn't exist already
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
