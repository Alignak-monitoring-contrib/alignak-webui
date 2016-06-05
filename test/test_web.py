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
os.environ['WEBUI_DEBUG'] = '1'
os.environ['TEST_WEBUI_CFG'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print "Configuration file", os.environ['TEST_WEBUI_CFG']

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
backend_address = "http://127.0.0.1:5002/"

def setup_module(module):
    print ("")
    print ("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['TEST_ALIGNAK_BACKEND_DB'] = 'alignak-backend'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split('mongo %s --eval "db.dropDatabase()"' % os.environ['TEST_ALIGNAK_BACKEND_DB'])
        )
        assert exit_code == 0

        # No console output for the applications backend ...
        FNULL = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('alignak_backend')
        )
        print ("PID: %s" % pid)
        time.sleep(1)

        print ("")
        print ("populate backend content")
        fh = open("NUL","w")
        exit_code = subprocess.call(
            shlex.split('alignak_backend_import --delete cfg/default/_main.cfg')
        )
        assert exit_code == 0


def teardown_module(module):
    print ("")
    print ("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class tests_1(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

        # Test application
        self.app = TestApp(
            webapp
        )

    def tearDown(self):
        print ""
        print "tearing down ..."

    def test_1_1_ping_pong(self):
        print ''
        print 'ping/pong server alive'

        # Default ping
        response = self.app.get('/ping')
        print response
        response.mustcontain('pong')

        # ping action
        response = self.app.get('/ping?action=')
        response = self.app.get('/ping?action=unknown', status=204)

        # Required refresh done
        response = self.app.get('/ping?action=done')
        print response
        response.mustcontain('pong')

        # Required refresh done, no more action
        response = self.app.get('/ping')
        response.mustcontain('pong')

        # Required refresh done, no more action
        response = self.app.get('/ping')
        response.mustcontain('pong')

        # Expect status 401
        response = self.app.get('/heartbeat', status=401)
        print response.status
        print response.json
        response.mustcontain('Session expired')

        print 'get home page /'
        response = self.app.get('/', status=302)
        print response
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_1_2_login_refused(self):
        print ''
        print 'test login/logout process - login refused'

        print 'get login page'
        response = self.app.get('/login')
        # print response.body
        response.mustcontain('<form role="form" method="post" action="/login">')

        print 'login refused - credentials'
        response = self.app.post('/login', {'username': None, 'password': None})
        redirected_response = response.follow()
        redirected_response.mustcontain('Backend connection refused...')

        print 'login refused - fake credentials'
        response = self.app.post('/login', {'username': 'fake', 'password': 'fake'})
        redirected_response = response.follow()
        redirected_response.mustcontain('Backend connection refused...')

        # /heartbeat sends a status 401
        response = self.app.get('/heartbeat', status=401)
        response.mustcontain('Session expired')

    def test_1_3_login_accepted(self):
        print ''
        print 'test login accepted'

        print 'get login page'
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print 'login accepted - go to home page'
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /hosts !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        # A host cookie now exists
        assert self.app.cookies['beaker.session.id']
        print 'cookies: ', self.app.cookiejar
        for cookie in self.app.cookiejar:
            print 'cookie: ', cookie.name, cookie.expires
            if cookie.name=='beaker.session.id':
                assert cookie.expires

        host = response.request.environ['beaker.session']
        print "host:", host

        assert 'current_user' in host and host['current_user']
        print host['current_user']
        assert host['current_user'].get_username() == 'admin'

        assert 'datamanager' in host and host['datamanager']
        print host['datamanager']
        assert host['datamanager'].get_logged_user().get_username() == 'admin'
        dm1 = host['datamanager']

        print 'get home page /dashboard'
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')

        # A host cookie now exists
        assert self.app.cookies['beaker.session.id']
        print 'cookies: ', self.app.cookiejar
        for cookie in self.app.cookiejar:
            print 'cookie: ', cookie.name, cookie.expires
            if cookie.name=='beaker.session.id':
                assert cookie.expires

        host = response.request.environ['beaker.session']
        print "host:", host

        assert 'current_user' in host and host['current_user']
        print host['current_user']
        assert host['current_user'].get_username() == 'admin'

        assert 'datamanager' in host and host['datamanager']
        print host['datamanager']
        assert host['datamanager'].get_logged_user().get_username() == 'admin'
        dm2 = host['datamanager']

        # Datamanager (eg host) is never the same object because response is a different object !
        assert dm1 != dm2

        # Despite different objects, content is identical !
        assert dm1.id == dm2.id
        print dm1.__dict__
        print dm2.__dict__
        # Expect for the updated time ...
        # assert dm1.updated != dm2.updated

        # /ping, still sends a status 200, but refresh is required
        response = self.app.get('/ping')
        print response
        response.mustcontain('refresh')

        # Reply with required refresh done
        response = self.app.get('/ping?action=done')
        print response
        response.mustcontain('pong')

        # /heartbeat, now sends a status 200
        response = self.app.get('/heartbeat', status=200)
        response.mustcontain('Current logged-in user: admin')

        # Require header refresh
        response = self.app.get('/ping?action=header', status=204)
        response = self.app.get('/ping?action=refresh&template=_header_hosts_state', status=200)
        print response
        response.mustcontain('"hosts-states-popover-content')
        response = self.app.get('/ping?action=refresh&template=_header_services_state', status=200)
        print response
        response.mustcontain('"services-states-popover-content')

        print 'logout - go to login page'
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')
        # A host cookie still exists
        assert self.app.cookies['beaker.session.id']
        print 'cookies: ', self.app.cookiejar
        for cookie in self.app.cookiejar:
            print 'cookie: ', cookie.name, cookie.expires
            if cookie.name=='beaker.session.id':
                assert cookie.expires

        # /heartbeat sends a status 401: unauthorized
        response = self.app.get('/heartbeat', status=401)
        response.mustcontain('Session expired')

    def test_1_4_dashboard_logout(self):
        print ''
        print 'test dashboard logout'

        print 'login accepted - got to home page'
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        # A host cookie now exists
        assert self.app.cookies['beaker.session.id']

        print 'get home page /'
        response = self.app.get('/')
        redirected_response = response.follow()
        redirected_response.mustcontain('<div id="dashboard">')

        print 'get home page /dashboard'
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')

        # /ping, still sends a status 200, but refresh is required
        print 'ping refresh required, data loaded'
        response = self.app.get('/ping')
        print response
        # response.mustcontain('refresh')

        # Reply with required refresh done
        response = self.app.get('/ping?action=done')
        print response
        # response.mustcontain('pong')

        print 'logout'
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

        print 'get home page /'
        response = self.app.get('/')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')


class tests_1_prefs(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

        # Test application
        self.app = TestApp(
            webapp
        )

        print 'get login page'
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print 'login accepted - go to home page'
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')

    def tearDown(self):
        print ""
        print "tearing down ..."

        print 'logout - go to login page'
        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    @unittest2.skip("Broken test ...")
    def test_1_1_global_preferences(self):
        print ''
        print 'test global user preferences page'

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

    def test_1_2_common(self):
        print ''
        print 'test common preferences'

        ### Common preferences

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

    def test_1_3_user(self):
        print ''
        print 'test common preferences'

        ### User's preferences


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
        response_value = response.json
        print response_value
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 1

        # Update a user's preference
        common_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.post('/preference/user', {'key': 'prefs', 'value': json.dumps(common_value)})
        print response
        response.mustcontain("User preferences saved")

        response = self.app.get('/preference/user', {'key': 'prefs'})
        response_value = response.json
        print response_value
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2


        # Set another user's preference
        common_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.post('/preference/user', {'key': 'prefs2', 'value': json.dumps(common_value)})
        print response
        response.mustcontain("User preferences saved")

        response = self.app.get('/preference/user', {'key': 'prefs'})
        response_value = response.json
        print response_value
        assert 'foo' in response_value
        assert response.json['foo'] == 'bar2'
        assert 'foo_int' in response_value
        assert response.json['foo_int'] == 2

        response = self.app.get('/preference/user', {'key': 'prefs2'})
        response_value = response.json
        print response_value
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
        response.mustcontain('value')
        # When a simple value is stored, it is always returned in a json object containing a 'value' field !
        assert 'value' in response_value
        assert response.json['value'] == 'test string'


        # Get a user preference ; default value
        default_value = { 'foo': 'bar2', 'foo_int': 2 }
        response = self.app.get('/preference/user', {'key': 'simple'})
        response_value = response.json
        response.mustcontain('value')
        # When a simple value is stored, it is always returned in a json object containing a 'value' field !
        assert 'value' in response_value
        assert response.json['value'] == 'test string'


class tests_2(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print 'login accepted - go to home page'
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        # A host cookie now exists
        assert self.app.cookies['beaker.session.id']

    def tearDown(self):
        print ""
        print "tearing down ..."

        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_2_1_static_files(self):
        print ''
        print 'test static files'

        print 'get favicon'
        response = self.app.get('/favicon.ico')

        print 'get opensearch'
        # response = self.app.get('/opensearch.xml')

        print 'get logo'
        response = self.app.get('/static/logo/default_company')
        response = self.app.get('/static/logo/other_company', status=404)

        print 'get users pictures'
        response = self.app.get('/static/photos/user_default')
        response = self.app.get('/static/photos/user_guest')
        response = self.app.get('/static/photos/user_admin')
        response = self.app.get('/static/photos/unknown', status=404)

        print 'get CSS/JS'
        response = self.app.get('/static/css/alignak_webui.css')
        response = self.app.get('/static/js/alignak_webui-layout.js')
        response = self.app.get('/static/js/alignak_webui-actions.js')
        response = self.app.get('/static/js/alignak_webui-refresh.js')
        response = self.app.get('/static/js/alignak_webui-bookmarks.js')

        print 'get modal dialog'
        response = self.app.get('/modal/about')


class tests_3(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print 'login accepted - go to home page'
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()
        redirected_response.mustcontain('<div id="dashboard">')
        # A host cookie now exists
        assert self.app.cookies['beaker.session.id']

    def tearDown(self):
        print ""
        print "tearing down ..."

        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    @unittest2.skip("To be completed  test ...")
    def test_3_1_dashboard(self):
        print ''
        print 'test dashboard'

        print 'get page /dashboard'
        redirected_response = self.app.get('/dashboard')
        redirected_response.mustcontain(
            '<div id="dashboard">',
            '<nav id="sidebar-menu" class="navbar navbar-default">',
            '<div id="dashboard">',
            '<div class="panel panel-default alert-warning" id="propose-widgets" style="margin:10px; display:none">',
            '<div id="widgets_loading" style="position: absolute; top: 0px; left: 0px;"></div>',

        )

        print 'get home page /dashboard'
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')
        host = response.request.environ['beaker.session']
        assert 'current_user' in host and host['current_user']
        print host['current_user']
        assert host['current_user'].get_username() == 'admin'
        assert 'target_user' in host and host['target_user']
        print host['target_user']
        assert host['target_user'].get_username() == 'anonymous'

        # Only one user in the host data manager !
        host = response.request.environ['beaker.session']
        assert 'current_user' in host and host['current_user']
        print host['current_user']
        assert host['current_user'].get_username() == 'admin'

        # Data manager
        datamgr = host['datamanager']
        search = {'where': {'name': 'admin'}}
        user = datamgr.get_contact(search)
        print user
        assert user
        search = {'where': {'name': 'not_admin'}}
        user = datamgr.get_contact(search)
        print user
        assert not user













        #TODO: to be tested later ...



        # Create a new contact
        print 'create a contact'
        data = {
            "name": "not_admin",
            "alias": "Not an administrator ... test user.",
            "min_business_impact": 0,
            "email": "frederic.mohier@gmail.com",

            "is_admin": False,
            "expert": False,
            "can_submit_commands": False,

            "host_notifications_enabled": True,
            "host_notification_period": tp_all.get_id(),
            "host_notification_commands": [
            ],
            "host_notification_options": [
                "d",
                "u",
                "r"
            ],

            "service_notifications_enabled": True,
            "service_notification_period": tp_all.get_id(),
            "service_notification_commands": [ ],
            "service_notification_options": [
                "w",
                "u",
                "c",
                "r"
            ],
            "retain_status_information": False,
            "note": "Monitoring template : default",
            "retain_nonstatus_information": False,
            "definition_order": 100,
            "address1": "",
            "address2": "",
            "address3": "",
            "address4": "",
            "address5": "",
            "address6": "",
            "pager": "",
            "notificationways": [],
            "_realm": realm_all.get_id()
        }
        response = self.app.post('/user/add', {
            'user_name': 'not_admin', 'comment': 'Not an administrator ... test user.'
        })
        print response
        assert response.json['status'] == "ok"
        assert response.json['message'] == "User created"

        print 'get page /users'
        response = self.app.get('/users')
        response.mustcontain(
            '<div id="users">',
            '2 elements',
            'admin',
            'not_admin'
        )
        # Test one request later ... because the test in the request environ not in the response environ !
        host = response.request.environ['beaker.session']
        datamgr = host['datamanager']

        print 'get home page /dashboard - no target user'
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')
        assert 'current_user' in host and host['current_user']
        print host['current_user']
        assert 'target_user' in host and host['target_user']
        print host['target_user']
        assert host['target_user'].get_username() == 'anonymous'

        print 'get home page /dashboard - set target user'
        response = self.app.get('/dashboard', {'target_user': 'not_admin'})
        response.mustcontain(
            '<div id="dashboard">'
        )
        print 'get home page /dashboard - no target user'
        response = self.app.get('/dashboard')
        response.mustcontain(
            '<div id="dashboard">'
        )
        assert 'current_user' in host and host['current_user']
        assert 'target_user' in host and host['target_user']
        assert host['target_user'].get_username() == 'anonymous'

        print "Current user is:", response.request.environ['beaker.session']['current_user']
        print "Target user is:", response.request.environ['beaker.session']['target_user']
        response = self.app.get('/dashboard', {'target_user': 'not_admin'})
        response.mustcontain('<div id="dashboard">')
        print "Current user is:", response.request.environ['beaker.session']['current_user']
        print "Target user is:", response.request.environ['beaker.session']['target_user']
        print "Not testable !"

        print 'get home page /dashboard - reset target user'
        response = self.app.get('/dashboard', {'target_user': ''})
        response.mustcontain('<div id="dashboard">')

    @unittest2.skip("To be completed  test ...")
    def test_3_2_users(self):
        print ''
        print 'test users'

        print 'get page /contacts'
        response = self.app.get('/contacts')
        response.mustcontain(
            '<div id="contacts">',
            '0 elements',
        )





        # TODO : to be completed ...






        # Create user
        print 'create user'
        response = self.app.post('/user/add', {
            'user_name': 'test_user', 'comment': 'Not an administrator ... test user.'
        })
        print response
        assert response.json['status'] == "ok"
        assert response.json['message'] == "User created"

        print 'get page /contacts'
        response = self.app.get('/contacts')
        response.mustcontain(
            '<div id="contacts">',
            '3 elements',
            'admin',
            'not_admin',
            'test_user'
        )

    def test_3_3_commands(self):
        print ''
        print 'test commands'

        print 'get page /commands'
        response = self.app.get('/commands')
        response.mustcontain(
            '<div id="commands">',
            '5 elements out of 5',
        )

    def test_3_4_hosts(self):
        print ''
        print 'test hosts'

        print 'get page /hosts'
        response = self.app.get('/hosts')
        response.mustcontain(
            '<div id="hosts">',
            '25 elements out of',
        )

    def test_3_5_services(self):
        print ''
        print 'test services'

        print 'get page /services'
        response = self.app.get('/services')
        response.mustcontain(
            '<div id="services">',
            '25 elements out of',
        )

if __name__ == '__main__':
    unittest.main()
