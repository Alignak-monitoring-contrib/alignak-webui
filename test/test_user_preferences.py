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
import json
import time
import shlex
import unittest2
import subprocess
# from gettext import gettext as _

from nose import with_setup
from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['WEBUI_DEBUG'] = '0'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print ("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
# To load application configuration used by the objects
import alignak_webui.app

from alignak_webui import webapp
from alignak_webui.objects.datamanager import DataManager
import alignak_webui.utils.datatable

# from logging import getLogger, DEBUG, INFO
# loggerDm = getLogger('alignak_webui.objects.datamanager')
# loggerDm.setLevel(DEBUG)

import bottle
from bottle import BaseTemplate, TEMPLATE_PATH

from webtest import TestApp

pid = None
backend_address = "http://127.0.0.1:5000/"

def setup_module(module):
    print ("")
    print ("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split('mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0
        time.sleep(1)

        # No console output for the applications backend ...
        pid = subprocess.Popen(
            shlex.split('alignak_backend')
        )
        print ("PID: %s" % pid)
        time.sleep(1)

        print("Feeding backend...")
        q = subprocess.Popen(
            shlex.split('alignak_backend_import --delete cfg/default/_main.cfg'), stdout=fnull
        )
        (stdoutdata, stderrdata) = q.communicate()  # now wait
        assert exit_code == 0


def teardown_module(module):
    print ("")
    print ("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class tests_preferences(unittest2.TestCase):

    def setUp(self):
        print ("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

        print('get login page')
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        self.stored_response = redirected_response

    def tearDown(self):
        print("tearing down ...")

        print('logout - return to login page')
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_1_1_global_preferences(self):
        print('test global user preferences page')

        # /ping, still sends a status 200, but refresh is required
        response = self.app.get('/ping')
        # response.mustcontain('refresh')
        response = self.app.get('/ping?action=done')
        # response.mustcontain('pong')

        # Get user's preferences page
        response = self.app.get('/preferences/user')
        response.mustcontain(
            '<div id="user-preferences">',
            'admin', 'Administrator',
            'Preferences'
        )

    @unittest2.skip("Broken test ...")
    def test_1_2_common(self):
        print('test common preferences')

        ### Common preferences
        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        datamgr = session['datamanager']
        user_prefs = datamgr.get_user_preferences('common', None)
        for pref in user_prefs:
            print("Common pref: %s: %s" % (pref['type'], pref['data']))
            datamgr.delete_user_preferences('common', pref['type'])
        user_prefs = datamgr.get_user_preferences('common', None)
        for pref in user_prefs:
            print("Item: %s: %s" % (pref['type'], pref['data']))
        assert len(user_prefs) == 0

        # Set a common preference named prefs
        common_value = { 'foo': 'bar', 'foo_int': 1 }
        # Value must be a string, so json dumps ...
        response = self.app.post('/preference/common', {'key': 'prefs', 'value': json.dumps(common_value)})
        response_value = response.json
        response.mustcontain('Common preferences saved')
        assert 'status' in response_value
        assert response.json['status'] == 'ok'
        assert 'message' in response_value
        assert response.json['message'] == 'Common preferences saved'

        # Get common preferences
        response = self.app.get('/preference/common', {'key': 'prefs'})
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 1

        # Update common preference named prefs
        common_value = { 'foo': 'bar2', 'foo_int': 2 }
        # Value must be a string, so json dumps ...
        response = self.app.post('/preference/common', {'key': 'prefs', 'value': json.dumps(common_value)})
        response.mustcontain('Common preferences saved')

        # Get common preferences
        response = self.app.get('/preference/common', {'key': 'prefs'})
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2


        # Set a common preference ; simple value
        common_value = 10
        # Value must be a string, so json dumps ...
        response = self.app.post('/preference/common', {'key': 'simple', 'value': json.dumps(common_value)})
        response_value = response.json
        response.mustcontain('Common preferences saved')
        assert 'status' in response_value
        assert response.json['status'] == 'ok'
        assert 'message' in response_value
        assert response.json['message'] == 'Common preferences saved'

        # Get common preferences ; simple value
        response = self.app.get('/preference/common', {'key': 'simple'})
        response_value = response.json
        response.mustcontain('value')
        # When a simple value is stored, it is always returned in a json object containing a 'value' field !
        assert 'value' in response_value
        assert response.json['value'] == 10

        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        datamgr = session['datamanager']
        user_prefs = datamgr.get_user_preferences('common', None)
        for pref in user_prefs:
            print("Common pref: %s: %s" % (pref['type'], pref['data']))
        assert len(user_prefs) == 2
        user_prefs = datamgr.get_user_preferences('common', None)
        for pref in user_prefs:
            print("Common pref to delete: %s: %s" % (pref['type'], pref['data']))
            datamgr.delete_user_preferences('common', pref['type'])
        user_prefs = datamgr.get_user_preferences('common', None)
        assert len(user_prefs) == 0

    def test_1_3_user(self):
        print('test user preferences')

        ### User's preferences
        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        datamgr = session['datamanager']
        user_prefs = datamgr.get_user_preferences('admin', None)
        prefs = []
        for pref in user_prefs:
            print("Item: %s = %s" % (pref, user_prefs[pref]))
            prefs.append(pref)
        for pref in prefs:
            datamgr.delete_user_preferences('admin', pref)
        user_prefs = datamgr.get_user_preferences('admin', None)
        self.assertIsNone(user_prefs)


        # Set a user's preference
        common_value = { 'foo': 'bar', 'foo_int': 1 }
        response = self.app.post('/preference/user', {'key': 'prefs', 'value': json.dumps(common_value)})
        response_value = response.json
        response.mustcontain('User preferences saved')
        assert 'status' in response_value
        assert response.json['status'] == 'ok'
        assert 'message' in response_value
        assert response.json['message'] == 'User preferences saved'

        response = self.app.get('/preference/user', {'key': 'prefs'})
        print(response)
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 1

        # Update a user's preference
        common_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.post('/preference/user', {'key': 'prefs', 'value': json.dumps(common_value)})
        response.mustcontain("User preferences saved")

        response = self.app.get('/preference/user', {'key': 'prefs'})
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2


        # Set another user's preference
        common_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.post('/preference/user', {'key': 'prefs2', 'value': json.dumps(common_value)})
        response.mustcontain("User preferences saved")

        response = self.app.get('/preference/user', {'key': 'prefs'})
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2

        response = self.app.get('/preference/user', {'key': 'prefs2'})
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2


        # Set a user preference ; simple value
        common_value = 10
        # Value must be a string, so json dumps ...
        response = self.app.post('/preference/user', {'key': 'simple', 'value': json.dumps(common_value)})
        response_value = response.json
        response.mustcontain('User preferences saved')
        assert 'status' in response_value
        assert response.json['status'] == 'ok'
        assert 'message' in response_value
        assert response.json['message'] == 'User preferences saved'

        # Get user preferences ; simple value
        response = self.app.get('/preference/user', {'key': 'simple'})
        response_value = response.json
        print("Response: %s" % response_value)
        # When a simple value is stored, it is always returned in a json object containing a 'value' field !
        self.assertEqual(response_value, 10)


        # Get a user preference ; default value, missing default
        default_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.get('/preference/user', {'key': 'def'})
        print("Body: '%s'" % response.body)
        # Response do not contain anything ...
        self.assertEqual(response.body, 'null')


        # Get a user preference ; default value
        default_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.get('/preference/user', {'key': 'def', 'default': json.dumps(default_value)})
        response_value = response.json
        # response.mustcontain('value')
        assert response_value == default_value

        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        datamgr = session['datamanager']
        user_prefs = datamgr.get_user_preferences('admin', None)
        for pref in user_prefs:
            print("Item: %s: %s" % (pref, user_prefs[pref]))
        self.assertEqual(len(user_prefs), 5)

    def test_1_4_all(self):
        print('test all preferences')

        ### User's preferences
        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        datamgr = session['datamanager']
        user_prefs = datamgr.get_user_preferences(None, None)
        self.assertIsNone(user_prefs)

if __name__ == '__main__':
    unittest.main()
