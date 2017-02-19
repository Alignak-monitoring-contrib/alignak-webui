#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This file is used to run the application in production environment with WSGI server.

    With uWSGI:
        uwsgi --plugin python --wsgi-file bin/alignak_webui.py --callable app \
              --socket 0.0.0.0:5001 --protocol=http --enable-threads -p 1
"""
# import alignak_webui.app
from alignak_webui import session_app as app
