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


def setup_module(module):
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

    test_dir = os.path.dirname(os.path.realpath(__file__))
    print("Current test directory: %s" % test_dir)

    print("Starting Alignak backend...")
    fnull = open(os.devnull, 'w')
    subprocess.Popen(shlex.split('alignak-backend'), stdout=fnull)
    print("Started")

    print("Feeding Alignak backend...")
    exit_code = subprocess.call(
        shlex.split('alignak-backend-import --delete %s/cfg/default/_main.cfg' % test_dir),
        stdout=fnull
    )
    assert exit_code == 0
    print("Fed")


def teardown_module(module):
    print("Stopping Alignak backend...")
    subprocess.call(['pkill', 'alignak-backend'])
    print("Stopped")
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
