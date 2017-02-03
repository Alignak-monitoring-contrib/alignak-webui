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

from webtest import TestApp

backend_process = None
backend_address = "http://127.0.0.1:5000/"


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


class tests_preferences(unittest2.TestCase):

    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        session = redirected_response.request.environ['beaker.session']
        # A host cookie now exists
        assert self.app.cookies['Alignak-WebUI']
        # Get a data manager
        self.dmg = DataManager(session=session, backend_endpoint=backend_address)

    def tearDown(self):
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_global_preferences(self):
        """ User preferences - global preferences """
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
            'admin',
            """<p class="username">
              Administrator
            </p>""",
            """<p class="usercategory">
               <small>Administrator</small>
            </p>""",
            """<div class="user-header""",
            """<div class="user-body""",
            """<table class="table table-condensed table-user-identification""",
            """<table class="table table-condensed table-user-preferences""",
            """<tr>
                        <td>
                           <a class="btn btn-default btn-xs btn-raised" href="#"
                              data-action="delete-user-preference"
                              data-element="dashboard_widgets"
                              data-message="User preference deleted"
                              data-toggle="tooltip" data-placement="top"
                              title="Delete this user preference">
                              <span class="fa fa-trash"></span>
                           </a>
                        </td>
                        <td>dashboard_widgets</td>
                        <td>
                        None
                        </td>
                     </tr>"""
        )

    @unittest2.skip("Broken test ... no more actual?")
    def test_common(self):
        """ User preferences - common preferences """
        print('test common preferences')

        ### Common preferences
        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        # datamgr = session['datamanager']
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
        # datamgr = session['datamanager']
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

    # @unittest2.skip("To be refactored test ...")
    def test_user(self):
        """ User preferences - user preferences """
        print('test user preferences')

        # Get user's preferences for the current logged-in user
        user_prefs = self.dmg.get_user_preferences(self.dmg.logged_in_user, None)
        prefs = []
        for pref in user_prefs:
            print("Item: %s = %s" % (pref, user_prefs[pref]))
            prefs.append(pref)
        for pref in prefs:
            self.dmg.delete_user_preferences(self.dmg.logged_in_user, pref)
        user_prefs = self.dmg.get_user_preferences(self.dmg.logged_in_user, None)
        assert user_prefs is None


        # Set a user's preference
        common_value = { 'foo': 'bar', 'foo_int': 1 }
        response = self.app.post('/preference/user', {'key': 'prefs', 'value': json.dumps(common_value)})
        response_value = response.json
        response.mustcontain('User preferences saved')
        assert 'status' in response_value
        assert response.json['status'] == 'ok'
        assert 'message' in response_value
        assert response.json['message'] == 'User preferences saved'

        # Get a user's preference
        response = self.app.get('/preference/user', {'key': 'prefs'})
        response_value = response.json
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 1

        # Update a user's preference
        common_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.post('/preference/user', {'key': 'prefs', 'value': json.dumps(common_value)})
        response.mustcontain("User preferences saved")

        # Get a user's preference
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

        # Get a user's preference
        response = self.app.get('/preference/user', {'key': 'prefs'})
        response_value = response.json
        # When a dict value is stored, it is always returned as a
        # dict as a json object!
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2

        # Get a user's preference
        response = self.app.get('/preference/user', {'key': 'prefs2'})
        response_value = response.json
        # When a dict value is stored, it is always returned as a
        # dict as a json object!
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
        # When a simple value is stored, it is always returned as a
        # direct 'value' and not as a json object!
        assert response_value == 10


        # Get a user preference ; default value, not existing  value name
        default_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.get('/preference/user', {'key': 'def'})
        # Response do not contain anything ...
        assert response.body == 'null'


        # Get a user preference ; default value
        default_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.get('/preference/user',
                                {'key': 'def', 'default': json.dumps(default_value)})
        response_value = response.json
        # response.mustcontain('value')
        assert response_value == default_value

        # Get user's preferences for the current logged-in user
        user_prefs = self.dmg.get_user_preferences(self.dmg.logged_in_user, None)
        for pref in user_prefs:
            print("Item: %s: %s" % (pref, user_prefs[pref]))
        # {'dashboard_widgets': [],
        # 'prefs': {'foo': 'bar2', 'foo_int': 2},
        # 'prefs2': {'foo': 'bar2', 'foo_int': 2},
        # 'simple': 10}
        assert len(user_prefs) == 4

    @unittest2.skip("To be refactored test ...")
    def test_all(self):
        """ User preferences - all preferences """
        print('test all preferences')

        ### User's preferences
        # Get all the preferences in the database
        session = self.stored_response.request.environ['beaker.session']
        # datamgr = session['datamanager']
        user_prefs = datamgr.get_user_preferences(None, None)
        assert user_prefs is None

if __name__ == '__main__':
    unittest.main()
