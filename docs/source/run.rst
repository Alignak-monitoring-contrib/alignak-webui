.. _run:

Run
===

Developer mode
--------------

To run in developper mode (single threaded Web server with few connections), you can start the application with::

    alignak_webui

The default configuration parameter make the application start on your localhost, port 8868, so you can point your Web browser to::

    http://localhost:8090/


To gain more control on the application start::

    cd alignak_webui
    ./app.py -n 0.0.0.0 -b http://127.0.0.1:5000 -d ../etc/settings.cfg

All the command line options::

    ./app.py -h


Production mode
---------------

You can use many possibilities to start the application, but we suggest you use ``uwsgi``.

With socket (+ nginx / apache as a front-end)::

   uwsgi --wsgi-file alignak_webui.py --callable app -s /tmp/uwsgi.sock --enable-threads

With direct HTTP connexion::

   uwsgi --wsgi-file alignak_webui.py --callable app --socket 0.0.0.0:8090 --protocol=http --enable-threads

Alignak WebUI runs on port 8090 like specified in arguments, so you can point your Web browser to::

    http://server-ip-address:8090

**Note**: As you may have guessed, the application installed a file called ``alignak_webui.py`` that imports the callable Python object named app.
