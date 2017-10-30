.. raw:: LaTeX

    \newpage

.. _run:

Run
===

Maintenance
-----------

The WebUI application uses the Beaker session middleware and it stores the user sessions in files in the */tmp/Alignak-WebUI/sessions* directory. You will need to remove the oldest files in this directory:
::

    find /tmp/Alignak-WebUI/sessions -mtime +3 -exec rm {} \;

**Note** that most often the */tmp* directory is cleant on a regular basis and nothing special is to be done;)


When using the WebUI with the provided script, some log files are stored in the */usr/local/var/log/alignak-webui* (or */var/log/alignak-webui*). Those files should also be handled else their size will grow indefinitely...

Production mode
---------------

The alignak WebUI installation script used when you install with pip:

* creates a *alignak-webui-uwsgi* launch script located in */usr/local/bin*

* stores the *uwsgi.ini* configuration file in */usr/local/etc/alignak-webui*

Thanks to this, you can simply run:
::

    alignak-webui-uwsgi

The ``alignak-webui-uwsgi`` script can receive a parameter for the configuration file to use. As default, it will use the */usr/local/etc/alignak-webui/uwsgi.ini* file.

The Alignak Web UI logs its activity in two files that are located in */usr/local/var/log/alignak-webui*:

* *webui-access.log* contains all the API HTTP requests

* *webui-error.log* contains the other messages: start, stop, activity log, ...

.. warning:: If you do not have those files when the WebUI is started, make sure that the user account used to run the backend is allow to write in the */usr/local/var/log/alignak-webui* directory ;)

To stop / reload the Alignak WebUI application:
::

    # Ctrl+C in the session where you started the alignak-webui-uwsgi script will stop the WebUI

    # To gracefully reload all the workers
    $ kill -SIGHUP `cat /tmp/alignak-webui.pid`

    # To gently kill all the workers
    $ kill -SIGTERM `cat /tmp/alignak-webui.pid`

    # To brutally kill all the workers
    $ kill -SIGINT `cat /tmp/alignak-webui.pid`

Environment variables
---------------------

If an environment variable `ALIGNAK_WEBUI_CONFIGURATION_FILE` exist, the file name defined in this variable takes precedence over the default files list.

If an environment variable `ALIGNAK_WEBUI_UWSGI_FILE` exist, the `alignak-backend-uwsgi` script will use the file name defined in this variable as the uWSGI configuration file.


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

Environment variables
---------------------

If an environment variable `ALIGNAK_WEBUI_CONFIGURATION_FILE` exist, the file name defined in this variable takes precedence over the default files list used by the application.

If an environment variable `ALIGNAK_WEBUI_UWSGI_FILE` exist, the `alignak-webui-uwsgi` script will use the file name defined in this variable as the uWSGI configuration file.


