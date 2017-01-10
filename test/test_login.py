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

import bottle
from bottle import BaseTemplate, TEMPLATE_PATH

from webtest import TestApp

pid = None
backend_address = "http://127.0.0.1:5000/"

def setup_module(module):
    print ("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split('mongo %s --eval "db.dropDatabase()"'
                        % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0
        time.sleep(1)

        print("Starting Alignak backend...")
        # No console output for the applications backend ...
        fnull = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('uwsgi --plugin python -w alignakbackend:app --socket 0.0.0.0:5000 '
                        '--protocol=http --enable-threads --pidfile /tmp/uwsgi.pid '
                        '--logto /tmp/uwsgi.log'), stdout=fnull
        )
        time.sleep(1)

        print("Feeding backend...")
        q = subprocess.Popen(
            shlex.split('alignak-backend-import --delete cfg/default/_main.cfg'), stdout=fnull
        )
        (stdoutdata, stderrdata) = q.communicate()  # now wait
        assert exit_code == 0

def teardown_module(module):
    subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
    time.sleep(2)


class TestLogin(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

    def test_login_refused(self):
        """ Login - refused"""
        print('test login/logout process - login refused')

        print('get login page')
        response = self.app.get('/login')
        # print response.body
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login refused - credentials')
        response = self.app.post('/login', {'username': None, 'password': None})
        redirected_response = response.follow()
        redirected_response.mustcontain('Backend connection refused...')

        print('login refused - fake credentials')
        response = self.app.post('/login', {'username': 'fake', 'password': 'fake'})
        redirected_response = response.follow()
        redirected_response.mustcontain('Backend connection refused...')

        # /heartbeat sends a status 401
        response = self.app.get('/heartbeat', status=401)
        response.mustcontain('Session expired')

    def test_login_accepted_session(self):
        """ Login - accepted session """
        print('test login accepted')

        print('get login page')
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        print('Response: %s' % response)

        # A session cookie now exists
        assert self.app.cookies['Alignak-WebUI']
        print('cookies: ', self.app.cookiejar)
        for cookie in self.app.cookiejar:
            print('cookie: ', cookie.name, cookie.expires)
            if cookie.name=='Alignak-WebUI':
                assert cookie.expires

        # A session exists and it contains: current user, his realm and his live synthesis
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].name == 'admin'
        assert 'current_realm' in session and session['current_realm']
        assert session['current_realm'].name == 'All'
        assert 'current_ls' in session and session['current_ls']

    def test_login_accepted(self):
        """ Login - accepted"""
        print('test login accepted')

        print('get login page')
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        print('Response: %s' % response)

        # Redirected twice: /login -> / -> /dashboard
        redirected_response = response.follow()
        print('Redirected response: %s' % redirected_response)
        redirected_response = redirected_response.follow()
        print('Redirected response: %s' % redirected_response)
        redirected_response.mustcontain('<div id="dashboard">')

        print('get home page /dashboard')
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')

        # /ping, still sends a status 200
        response = self.app.get('/ping')
        response.mustcontain('pong')

        # /heartbeat, now sends a status 200
        response = self.app.get('/heartbeat', status=200)
        response.mustcontain('Current logged-in user: admin')

        # Require header refresh
        response = self.app.get('/ping?action=header', status=204)
        response = self.app.get('/ping?action=refresh&template=_header_states', status=200)
        print(response)
        response.mustcontain('"hosts-states-popover-content')
        response.mustcontain('"services-states-popover-content')

        print('logout - go to login page')
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')
        # A host cookie still exists
        assert self.app.cookies['Alignak-WebUI']
        print('cookies: ', self.app.cookiejar)
        for cookie in self.app.cookiejar:
            print('cookie: ', cookie.name, cookie.expires)
            if cookie.name=='Alignak-WebUI':
                assert cookie.expires

        # /heartbeat sends a status 401: unauthorized
        response = self.app.get('/heartbeat', status=401)
        response.mustcontain('Session expired')

    def test_dashboard_logout(self):
        """ Logout dashboard"""
        print('test dashboard logout')

        print('login accepted - got to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']

        print('get home page /')
        response = self.app.get('/')
        redirected_response = response.follow()
        redirected_response.mustcontain('<div id="dashboard">')

        print('get home page /dashboard')
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')

        # /ping, still sends a status 200, but refresh is required
        print('ping refresh required, data loaded')
        response = self.app.get('/ping')
        print(response)
        # response.mustcontain('refresh')

        # Reply with required refresh done
        response = self.app.get('/ping?action=done')
        print(response)
        # response.mustcontain('pong')

        print('logout')
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')
        # print 'click on logout'
        # response = response.click(href='/logout')
        # redirected_response = response.follow()
        # redirected_response.mustcontain('<form role="form" method="post" action="/login">')

        # /heartbeat sends a status 401: unauthorized
        response = self.app.get('/heartbeat', status=401)
        response.mustcontain('Session expired')

        print('get home page /')
        response = self.app.get('/')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')


class TestStaticFiles(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']

    def tearDown(self):
        print("tearing down ...")

        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

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


if __name__ == '__main__':
    unittest.main()
