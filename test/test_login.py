#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
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


# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app

from webtest import TestApp

backend_process =  None

def setup_module(module):
    # Set test mode for applications backend
    os.environ['TEST_ALIGNAK_BACKEND'] = '1'
    os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-webui-tests'

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
    global backend_process
    fnull = open(os.devnull, 'w')
    backend_process = subprocess.Popen(['uwsgi', '--plugin', 'python',
                                        '-w', 'alignak_backend.app:app',
                                        '--socket', '0.0.0.0:5000',
                                        '--protocol=http', '--enable-threads', '--pidfile',
                                        '/tmp/uwsgi.pid'],
                                       stdout=fnull)
    print("Started")

    print("Feeding Alignak backend... %s" % test_dir)
    exit_code = subprocess.call(
        shlex.split('alignak-backend-import --delete %s/cfg/default/_main.cfg' % test_dir),
        stdout=fnull
    )
    assert exit_code == 0
    print("Fed")


def teardown_module(module):
    print("Stopping Alignak backend...")
    global backend_process
    backend_process.kill()
    # subprocess.call(['pkill', 'alignak-backend'])
    print("Stopped")
    time.sleep(2)


class TestLogin(unittest2.TestCase):

    def setUp(self):
        print("setting up ...")

        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

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
        redirected_response.mustcontain('Access denied! Check your username and password.')

        print('login refused - fake credentials')
        response = self.app.post('/login', {'username': 'fake', 'password': 'fake'})
        redirected_response = response.follow()
        redirected_response.mustcontain('Access denied! Check your username and password.')

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
            print('cookie: ', cookie.__dict__)
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

        # Redirected twice: /login -> / -> /livestate
        redirected_response = response.follow()
        print('Redirected response: %s' % redirected_response)
        redirected_response = redirected_response.follow()
        print('Redirected response: %s' % redirected_response)
        redirected_response.mustcontain('<div id="livestate">')

        # /ping, still sends a status 200
        response = self.app.get('/ping')
        response.mustcontain('pong')

        # /heartbeat, now sends a status 200
        response = self.app.get('/heartbeat', status=200)
        response.mustcontain('Current logged-in user: admin')

        # Require header refresh
        self.app.get('/ping?action=header', status=204)
        response = self.app.get('/ping?action=refresh', status=200)
        assert response.json == {u'status': u'ok', u'message': u'missing template name. Use /ping?action=refresh&template=name.'}
        response = self.app.get('/ping?action=refresh&template=_header_states', status=200)
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

    def test_logout(self):
        """ Logout from the application"""
        print('test logout')

        print('login accepted - got to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /livestate !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="livestate">')
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']

        print('get home page /')
        response = self.app.get('/')
        redirected_response = response.follow()
        redirected_response.mustcontain('<div id="livestate">')

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
