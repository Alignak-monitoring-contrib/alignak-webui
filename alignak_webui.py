#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    This file is used to run the application in production environment with WSGI server.

    With uWSGI:
        uwsgi --wsgi-file alignak_webui.py --callable app --socket 0.0.0.0:8868 --protocol=http --enable-threads
"""
import alignak_webui.app
from alignak_webui import webapp as app
