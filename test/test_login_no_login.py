#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015:
#   Frederic Mohier, frederic.mohier@gmail.com
#
# This file is part of (WebUI).
#
# (WebUI) is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# (WebUI) is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
# import the unit testing module

from __future__ import print_function
import os
import time
import shlex
import unittest2
import subprocess
from calendar import timegm
from datetime import datetime, timedelta

from nose import with_setup
from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['WEBUI_DEBUG'] = '0'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(
    os.path.abspath(os.path.dirname(__file__)), 'settings.cfg'
)
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
# To load application configuration used by the objects
import alignak_webui.app

from alignak_webui import webapp

from webtest import TestApp

pid = None
backend_address = "http://127.0.0.1:5000/"


class TestNoLogin(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

    def test_1_1_ping_pong(self):
        """ Login - ping/pong"""
        print('ping/pong server alive')

        # Default ping
        response = self.app.get('/ping')
        print(response)
        response.mustcontain('pong')

        # ping action
        response = self.app.get('/ping?action=')
        response = self.app.get('/ping?action=unknown', status=204)

        # Required refresh done
        response = self.app.get('/ping?action=done')
        print(response)
        response.mustcontain('pong')

        # Required refresh done, no more action
        response = self.app.get('/ping')
        response.mustcontain('pong')

        # Required refresh done, no more action
        response = self.app.get('/ping')
        response.mustcontain('pong')

        # Expect status 401
        response = self.app.get('/heartbeat', status=401)
        print(response.status)
        print(response.json)
        response.mustcontain('Session expired')

        print('get home page /')
        response = self.app.get('/', status=302)
        print(response)
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')


class TestStaticFiles(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

        # response = self.app.get('/login')
        # response.mustcontain('<form role="form" method="post" action="/login">')
        #
        # print('login accepted - go to home page')
        # response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # # Redirected twice: /login -> / -> /dashboard !
        # redirected_response = response.follow()
        # redirected_response = redirected_response.follow()
        # redirected_response.mustcontain('<div id="dashboard">')
        # # A host cookie now exists
        # assert self.app.cookies['Alignak-WebUI']

    def tearDown(self):
        print("tearing down ...")

        # response = self.app.get('/logout')
        # redirected_response = response.follow()
        # redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_static_files(self):
        """ Static files"""
        print('test static files')

        print('get favicon')
        response = self.app.get('/static/images/favicon.ico')

        print('get opensearch')
        # response = self.app.get('/opensearch.xml')

        print('get logo')
        response = self.app.get('/static/images/default_company.png')
        response = self.app.get('/static/imeages/other_company.png', status=404)

        print('get users pictures')
        response = self.app.get('/static/images/user_default.png')
        response = self.app.get('/static/images/user_guest.png')
        response = self.app.get('/static/images/user_admin.png')
        response = self.app.get('/static/images/unknown.png', status=404)

        print('get CSS/JS')
        response = self.app.get('/static/css/alignak_webui.css')
        response = self.app.get('/static/js/alignak_webui-layout.js')
        response = self.app.get('/static/js/alignak_webui-actions.js')
        response = self.app.get('/static/js/alignak_webui-refresh.js')
        response = self.app.get('/static/js/alignak_webui-bookmarks.js')

        print('get modal dialog')
        response = self.app.get('/modal/about')
