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
import requests
from calendar import timegm
from datetime import datetime, timedelta

from nose.tools import *

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app
# from alignak_webui import webapp
from alignak_webui.backend.datamanager import DataManager
import alignak_webui.utils.datatable

# from logging import getLogger, DEBUG, INFO
# loggerDm = getLogger('alignak_webui.objects.datamanager')
# loggerDm.setLevel(DEBUG)

import bottle
from bottle import BaseTemplate, TEMPLATE_PATH

from webtest import TestApp

backend_process = None
backend_address = "http://127.0.0.1:5000/"


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


class tests_users(unittest2.TestCase):

    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        # redirected_response.mustcontain('<div id="dashboard">')
        self.stored_response = redirected_response
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']

    def tearDown(self):
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_change_password(self):
        """ Actions - acknowledge"""
        print('test password change')

        print('get page /password_change_request')
        response = self.app.get('/password_change_request')
        response.mustcontain(
            '<form id="password_change" class="form-horizontal" data-action="password" method="post" action="/change_password" role="form">'
        )

        # Get Data manager in the session
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        assert session['current_user'].get_username() == 'admin'

        datamgr = DataManager(alignak_webui.app.app, session=session)

        # Get guest user in the backend
        user = datamgr.get_user({'where': {'name': 'guest'}})

        # -------------------------------------------
        # Change a password
        # Missing element_id!
        data = {
            # "element_id": user.id,
            "elements_type": 'user',
            "elements_name": 'guest',
            "password1": "NewPassword2017",
            "password2": "NewPassword2017",
            "valid_form": "true"
        }
        self.app.post('/change_password', data, status=400)

        # Empty passwords
        data = {
            "element_id": user.id,
            "elements_type": 'user',
            "elements_name": 'guest',
            "password1": "",
            "password2": "",
            "valid_form": "true"
        }
        self.app.post('/change_password', data, status=400)
        data = {
            "element_id": user.id,
            "elements_type": 'user',
            "elements_name": 'guest',
            "password1": "NewPassword2017",
            "password2": "",
            "valid_form": "true"
        }
        self.app.post('/change_password', data, status=400)

        # Invalid form
        data = {
            "element_id": user.id,
            "elements_type": 'user',
            "elements_name": 'guest',
            "password1": "NewPassword2017",
            "password2": "NewPassword2017",
            "valid_form": "false"
        }
        self.app.post('/change_password', data, status=400)

        # -------------------------------------------
        # Change a password
        data = {
            "element_id": user.id,
            "elements_type": 'user',    # Default value, can be omitted ...
            "elements_name": 'guest',
            "password1": "NewPassword2017",
            "password2": "NewPassword2017",
            "valid_form": "true"
        }
        response = self.app.post('/change_password', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == "User guest updated."

        # -------------------------------------------
        # Log-out the admin user
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

        # Log-in with the new password
        response = self.app.post('/login', {'username': 'guest', 'password': 'NewPassword2017'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        # redirected_response.mustcontain('<div id="dashboard">')
        self.stored_response = redirected_response
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']

        # Redirected twice: /login -> / -> /livestate
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="livestate">')


if __name__ == '__main__':
    unittest.main()
