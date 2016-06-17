.. _develop:

Development
===========

Application
-----------

Web application developed with Python Bottle micro-framework. See application.py

User authentication
~~~~~~~~~~~~~~~~~~~~~~~~

If no session exists all the requests are redirected to the /login page. User is authenticated near Alignak bakcned with username / password. Once authenticated, a Contact representing the current user is stored in the session. This contact has an *authenticated* attribute set.

Cookie name is the application name(Alignak-WebUI). Expiry delay is 6 hours.

Session stores the current user, the target user, the connection message and the data manager.


Session management
~~~~~~~~~~~~~~~~~~~~~~~~

Use Beaker middleware for session management. The configuration is made in `__init__.py`.

The session is stored in memory, mainly for performance and also because some stored objects can not be pickled (BackendConnection) to file storage.

A cookie named as the application (Alignak-WebUI) is existing as soon as a session is created. Its expiry delay is 6 hours.

The session stores the current user, the target user, the connection message and the data manager containing all the UI data.


Data manager
------------------
 The application uses a DataManager object to store all the information about the data got from the Alignak backend.

 TO BE DETAILED !


User's preferences
------------------
 `application.js` declares functions for managing user's preferences, but the `_object_list.html` declares its own functions for the datatables because the saved parameters must be loaded synchronously ...

 TO BE EXPLAINED !

Templates
---------

Good practices
~~~~~~~~~~~~~~

From Python to javascript, main javascript variables are declared in layout.tpl to be available for every HTML and Javascript files.
