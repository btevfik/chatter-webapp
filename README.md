chatter-webapp
==============

A chat app with Google App Engine

work on progress...

**Update 1 (Feb 17 2013)**

-client opens a channel, server stores the client_id in a CurrentUser database

-client sends a message using AJAX

-server stores the message in a Guestbook database

-server pushes the message to all clients in the CurrentUser database using channel API

-only tested with 2 clients 

*issues:*

-no tracking of who is disconnected

-anonymous users can sign it as a guestbook (no chat functionality)
---------------------------------------------------------------------------------------

**Initial (Feb 15 2013)**

-client posts the message to server using AJAX

-server pushes the posted message to the user that sent the message using the channel

-now it acts same as a guestbook, but without reload.
