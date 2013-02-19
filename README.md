Chatterv1 - web: http://chatter-now.appspot.com
==============

A chat app with Google App Engine

**Version 1.2 (Feb 19 2013)**

-the app is now working as a hybrid btw a guestbook and a chat app (planning to keep that functionality)

-the chat history is saved in database so if page is reloaded, it will show up

-anonymous users can now chat

-anonymous user id is stored in a cookie

-as long as the cookies are not deleted or expire, anonymous users will see their messages with "you:" bubble,
even if they reload the page.

*possible additions*

-creating private rooms

-be able to delete chat history


**Version 1.1 (Feb 17 2013)**

-client opens a channel, server stores the client_id in a CurrentUser database

-client sends a message using AJAX

-server stores the message in a Guestbook database

-server pushes the message to all clients in the CurrentUser database using channel API

-only tested with 2 clients 

*issues:*

-no tracking of who is disconnected

-anonymous users can sign it as a guestbook (no chat functionality)


**Version 0.9 (Feb 15 2013)**

-client posts the message to server using AJAX

-server pushes the posted message to the user that sent the message using the channel

-now it acts same as a guestbook, but without reload.
