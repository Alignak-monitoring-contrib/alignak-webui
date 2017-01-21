.. raw:: LaTeX

    \newpage

.. _run:

Run
===

Production mode
---------------

The alignak WebUI installation script used when you install with pip:

* creates a *alignak-webui-uwsgi* launch script located in */usr/local/bin*

* stores the *uwsgi.ini* configuration file in */usr/local/etc/alignak-webui*

Thanks to this, you can simply run:
::

    alignak-webui-uwsgi

The Alignak webui logs its activity in two files that are located in */usr/local/var/log*:

* *alignak-webui-access.log* contains all the API HTTP requests

* *alignak-webui-error.log* contains the other messages: start, stop, activity log, ...

.. warning:: If you do not have those files when the WebUI is started, make sure that the user account used to run the backend is allow to write in the */usr/local/var/log* directory ;)


Developer mode
--------------

To run in developper mode (single threaded Web server with few connections), you can start the application with::

    alignak-webui

The default configuration parameter makes the application start on your localhost, port 5001, so you can point your Web browser to::

    http://localhost:5001/


To gain more control on the application start::

    cd alignak_webui
    ./app.py -n 0.0.0.0 -b http://127.0.0.1:5000 -d ../etc/settings.cfg

All the command line options::

    ./app.py -h

