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
from alignak_webui.objects.datamanager import DataManager
import alignak_webui.utils.datatable

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

        print ("")
        print ("populate backend content")
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


class Test0NoLogin(unittest2.TestCase):

    def setUp(self):
        print("")
        print("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

    def tearDown(self):
        print("")
        print("tearing down ...")

    def test_1_1_ping_pong(self):
        print('')
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


class Test1Login(unittest2.TestCase):

    def setUp(self):
        print("")
        print("setting up ...")

        # Test application
        self.app = TestApp(
            webapp
        )

    def tearDown(self):
        print("")
        print("tearing down ...")

    def test_1_2_login_refused(self):
        print('')
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

    def test_1_3_login_accepted(self):
        print('')
        print('test login accepted')

        print('get login page')
        response = self.app.get('/login')
        response.mustcontain('<form role="form" method="post" action="/login">')

        print('login accepted - go to home page')
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        print('Response: %s' % response)
        # Redirected twice: /login -> / -> /hosts !
        redirected_response = response.follow()
        print('Redirected response: %s' % redirected_response)
        redirected_response = redirected_response.follow()
        print('Redirected response: %s' % redirected_response)
        redirected_response.mustcontain('<div id="dashboard">')
        # A session cookie now exists
        print(self.app.cookies)
        assert self.app.cookies['Alignak-WebUI']
        print('cookies: ', self.app.cookiejar)
        for cookie in self.app.cookiejar:
            print('cookie: ', cookie.name, cookie.expires)
            if cookie.name=='Alignak-WebUI':
                assert cookie.expires

        session = response.request.environ['beaker.session']
        print("session:", session)

        assert 'current_user' in session and session['current_user']
        print(session['current_user'])
        assert session['current_user'].name == 'admin'

        assert 'datamanager' in session and session['datamanager']
        print(session['datamanager'])
        assert session['datamanager'].logged_in_user.name == 'admin'
        assert session['datamanager'].logged_in_user.get_username() == 'admin'
        dm1 = session['datamanager']

        print('get home page /dashboard')
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')

        # A session cookie now exists
        assert self.app.cookies['Alignak-WebUI']
        print('cookies: ', self.app.cookiejar)
        for cookie in self.app.cookiejar:
            print('cookie: ', cookie.name, cookie.expires)
            if cookie.name=='Alignak-WebUI':
                assert cookie.expires

        session = response.request.environ['beaker.session']
        print("session:", session)

        assert 'current_user' in session and session['current_user']
        assert session['current_user'].name == 'admin'

        assert 'datamanager' in session and session['datamanager']
        assert session['datamanager'].logged_in_user.name == 'admin'
        dm2 = session['datamanager']

        # Datamanager is never the same object because response is a different object !
        # assert dm1 != dm2 ????

        # Despite different objects, content is identical !
        assert dm1.id == dm2.id
        print(dm1.__dict__)
        print(dm2.__dict__)
        # Expect for the updated time ...
        # assert dm1.updated != dm2.updated

        # /ping, still sends a status 200, but refresh is required
        response = self.app.get('/ping')
        print(response)
        response.mustcontain('refresh')

        # Reply with required refresh done
        response = self.app.get('/ping?action=done')
        print(response)
        response.mustcontain('pong')

        # /heartbeat, now sends a status 200
        response = self.app.get('/heartbeat', status=200)
        response.mustcontain('Current logged-in user: admin')

        # Require header refresh
        response = self.app.get('/ping?action=header', status=204)
        response = self.app.get('/ping?action=refresh&template=_header_hosts_state', status=200)
        print(response)
        response.mustcontain('"hosts-states-popover-content')
        response = self.app.get('/ping?action=refresh&template=_header_services_state', status=200)
        print(response)
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

    def test_1_4_dashboard_logout(self):
        print('')
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


class Test2StaticFiles(unittest2.TestCase):

    def setUp(self):
        print("")
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
        print("")
        print("tearing down ...")

        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    def test_2_1_static_files(self):
        print('')
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


class Test3Dashboard(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_1_dashboard(self):
        print('')
        print('test dashboard')

        print('get page /dashboard')
        redirected_response = self.app.get('/dashboard')
        redirected_response.mustcontain(
            'This file is a part of Alignak-WebUI.',
            '<!-- Page header -->',
            '<header>',
            '<nav id="menu-bar">',
            '<!-- Dashboard widgets bar -->',
            '<a data-action="display-currently"',
            '<a data-action="toggle-page-refresh"',
            '<!-- User info -->',
            '<div id="page-wrapper" class="container-fluid header-page">',

            '<div id="dashboard">',
            '<div id="dashboard-synthesis"',
            '<div id="propose-widgets" ',
            '<!-- Widgets loading indicator -->',
            '<div id="widgets_loading"></div>',
            '<!-- Widgets grid -->',
            '<!-- Page footer -->'
        )

        print('get page /currently')
        redirected_response = self.app.get('/currently')
        redirected_response.mustcontain(
            '<div id="currently">',
            '<div id="one-eye-toolbar"',
            '<div id="one-eye-overall" ',
            '<div id="one-eye-icons" ',
            '<div id="livestate-graphs" '
        )


class Test3Users(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_2_users(self):
        print('')
        print('test users')

        print('get page /users')
        response = self.app.get('/users')
        response.mustcontain(
            '<div id="users">',
            '5 elements out of 5',
        )

        response = self.app.get('/users/config')

        response = self.app.get('/users/list')

        response = self.app.get('/users/table')

class Test3Commands(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_3_commands(self):
        print('')
        print('test commands')

        print('get page /commands')
        response = self.app.get('/commands')
        response.mustcontain(
            '<div id="commands">',
            '25 elements out of 103',
        )
        response = self.app.get('/commands/config')
        response = self.app.get('/commands/list')
        response = self.app.get('/commands/table')


class Test3Hosts(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_4_hosts(self):
        print('')
        print('test hosts')

        print('get page /hosts')
        response = self.app.get('/hosts')
        response.mustcontain(
            '<div id="hosts">',
            '13 elements out of 13',
        )
        response = self.app.get('/hosts/config')
        response = self.app.get('/hosts/list')
        response = self.app.get('/hosts/table')
        response = self.app.get('/hosts/templates')
        response = self.app.get('/host/localhost')

        print('get page /hosts/widget')
        response = self.app.post('/hosts/widget', status=204)
        response = self.app.post('/hosts/widget', {'widget_id': 'test_widget'}, status=204)

        # Hosts table
        response = self.app.post('/hosts/widget', {
            'widget_id': 'hosts_table_1',
            'widget_template': 'hosts_table_widget'
        })
        print(response)
        response.mustcontain(
            '<div id="wd_panel_hosts_table_1" class="panel panel-default alignak_webui_widget ">'
        )
        # Hosts chart
        response = self.app.post('/hosts/widget', {
            'widget_id': 'hosts_chart_1',
            'widget_template': 'hosts_chart_widget'
        })
        print(response)
        response.mustcontain(
            '<div id="wd_panel_hosts_chart_1" class="panel panel-default alignak_webui_widget ">'
        )


class Test3Services(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_5_services(self):
        print('')
        print('test services')

        print('get page /services')
        response = self.app.get('/services')
        response.mustcontain(
            '<div id="services">',
            '25 elements out of 94',
        )
        response = self.app.get('/services/config')
        response = self.app.get('/services/list')
        response = self.app.get('/services/table')
        response = self.app.get('/services/templates')

        print('get page /services/widget')
        response = self.app.post('/services/widget', status=204)
        response = self.app.post('/services/widget', {'widget_id': 'test_widget'}, status=204)

        # Hosts table
        response = self.app.post('/services/widget', {
            'widget_id': 'services_table_1',
            'widget_template': 'services_table_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_services_table_1" class="panel panel-default alignak_webui_widget ">'
        )
        # Hosts chart
        response = self.app.post('/services/widget', {
            'widget_id': 'services_chart_1',
            'widget_template': 'services_chart_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_services_chart_1" class="panel panel-default alignak_webui_widget ">'
        )


class Test3Timeperiods(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_6_timeperiods(self):
        print('')
        print('test timeperiods')

        print('get page /timeperiods')
        response = self.app.get('/timeperiods')
        response.mustcontain(
            '<div id="timeperiods">',
            '4 elements out of 4',
        )
        response = self.app.get('/timeperiods/config')
        response = self.app.get('/timeperiods/list')
        response = self.app.get('/timeperiods/table')
        response = self.app.get('/timeperiods/templates')


class Test3Livestate(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_7_livestate(self):
        print('')
        print('test livestate')

        print('get page /livestate')
        response = self.app.get('/livestate/fake_id', status=204)

        session = response.request.environ['beaker.session']
        datamgr = session['datamanager']
        lv_host = datamgr.get_livestates({'where': {'name': 'webui'}})
        lv_service = datamgr.get_livestates({'where': {'name': 'webui/Shinken2-arbiter'}})

        # Redirect to host page
        response = self.app.get('/livestate/' + lv_host[0].id)
        response = response.follow()
        response.mustcontain(
            '<div id="host">',
        )

        # Redirect to host page
        response = self.app.get('/livestate/' + lv_service[0].id)
        response = response.follow()
        response.mustcontain(
            '<div id="host">',
        )

        print('get page /livestates/widget')
        # Errors
        response = self.app.post('/livestate/widget', status=204)
        response = self.app.post('/livestate/widget', {'widget_id': 'test_widget'}, status=204)

        # Hosts/services table
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_table_1',
            'widget_template': 'livestate_table_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_livestate_table_1" class="panel panel-default alignak_webui_widget ">'
        )

        # Hosts chart
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_hosts_chart_1',
            'widget_template': 'livestate_hosts_chart_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_livestate_hosts_chart_1" class="panel panel-default alignak_webui_widget ">'
        )
        # Hosts counters
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_hosts_counters_1',
            'widget_template': 'livestate_hosts_counters_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_livestate_hosts_counters_1" class="panel panel-default alignak_webui_widget ">'
        )
        # Hosts SLA
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_hosts_sla_1',
            'widget_template': 'livestate_hosts_sla_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_livestate_hosts_sla_1" class="panel panel-default alignak_webui_widget ">'
        )

        # Services chart
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_services_chart_1',
            'widget_template': 'livestate_services_chart_widget'
        })
        print(response)
        response.mustcontain(
            '<div id="wd_panel_livestate_services_chart_1" class="panel panel-default alignak_webui_widget ">'
        )
        # Services counters
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_services_counters_1',
            'widget_template': 'livestate_services_counters_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_livestate_services_counters_1" class="panel panel-default alignak_webui_widget ">'
        )
        # Services SLA
        response = self.app.post('/livestate/widget', {
            'widget_id': 'livestate_services_sla_1',
            'widget_template': 'livestate_services_sla_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_livestate_services_sla_1" class="panel panel-default alignak_webui_widget ">'
        )


class Test3Worldmap(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_8_worldmap(self):
        print('')
        print('test worldmap')

        print('get page /worldmap')
        response = self.app.get('/worldmap')
        response.mustcontain(
            '<div id="hostsMap">'
        )

        # Widget
        response = self.app.post('/worldmap/widget', {
            'widget_id': 'worldmap_1',
            'widget_template': 'worldmap_widget'
        })
        response.mustcontain(
            '<div id="wd_panel_worldmap_1" class="panel panel-default alignak_webui_widget ">'
        )


class Test3Minemap(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_3_9_minemap(self):
        print('')
        print('test minemap')

        print('get page /min')
        response = self.app.get('/minemap')
        response.mustcontain(
            '<div id="minemap">'
        )


class Test3Hostgroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']
        self.datamgr = self.session['datamanager']

    def tearDown(self):
        response = self.app.get('/logout')

    def test_1_hostgroups(self):
        print('')
        print('test hostgroups')

        print('get page /hostgroups')
        response = self.app.get('/hostgroups')
        response.mustcontain(
            '<div id="hostgroups">',
            # '8 elements out of 8'
        )
        response = self.app.get('/hostgroups/config')
        response = self.app.get('/hostgroups/list')
        response = self.app.get('/hostgroups/table')
        response = self.app.get('/hostgroups/templates')
        response = self.app.get('/hostgroup/all')

        print('get page /hostgroups/tree')
        response = self.app.get('/hostgroups/tree')
        response.mustcontain(
            '<div id="hostgroups_tree_view">',
            # '8 elements out of 8'
        )

    def test_1_hostgroups_list(self):
        print('')
        print('test hostgroups')

        print('get page /hostgroups/list')
        response = self.app.get('/hostgroups/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item

    def test_1_hostgroups_members(self):
        print('')
        print('test hostgroups members')

        # Get a hostgroup
        ug = self.datamgr.get_hostgroup({'where': {'alias': 'Servers'}})
        self.assertEqual(ug.name, 'servers')

        print('get page /hostgroup/members')
        response = self.app.get('/hostgroup/members/' + ug.id)
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item
            assert 'icon' in item
            assert 'url' in item


class Test3Servicegroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']
        self.datamgr = self.session['datamanager']

    def tearDown(self):
        response = self.app.get('/logout')

    def test_1_servicegroups(self):
        print('')
        print('test servicegroups')

        print('get page /servicegroups')
        response = self.app.get('/servicegroups')
        response.mustcontain(
            '<div id="servicegroups">',
            # '5 elements out of 5'
        )
        response = self.app.get('/servicegroups/config')
        response = self.app.get('/servicegroups/list')
        response = self.app.get('/servicegroups/table')
        response = self.app.get('/servicegroups/templates')
        response = self.app.get('/servicegroup/all')

        print('get page /servicegroups/tree')
        response = self.app.get('/servicegroups/tree')
        response.mustcontain(
            '<div id="servicegroups_tree_view">',
            # '5 elements out of 5'
        )

    def test_1_servicegroups_list(self):
        print('')
        print('test servicegroups')

        print('get page /servicegroups/list')
        response = self.app.get('/servicegroups/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item

    def test_1_servicegroups_members(self):
        print('')
        print('test servicegroups members')

        # Get a servicegroup
        ug = self.datamgr.get_servicegroup({'where': {'alias': 'dev services group'}})
        self.assertEqual(ug.name, 'dev')

        print('get page /servicegroup/members')
        response = self.app.get('/servicegroup/members/' + ug.id)
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item
            assert 'icon' in item
            assert 'url' in item


class Test3Usergroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']
        self.datamgr = self.session['datamanager']

    def tearDown(self):
        response = self.app.get('/logout')

    def test_1_usergroups(self):
        print('')
        print('test usergroups')

        print('get page /usergroups')
        response = self.app.get('/usergroups')
        response.mustcontain(
            '<div id="usergroups">',
            # '5 elements out of 5'
        )
        response = self.app.get('/usergroups/config')
        response = self.app.get('/usergroups/list')
        response = self.app.get('/usergroups/table')
        response = self.app.get('/usergroups/templates')
        response = self.app.get('/usergroup/all')

        print('get page /usergroups/tree')
        response = self.app.get('/usergroups/tree')
        response.mustcontain(
            '<div id="usergroups_tree_view">',
            # '5 elements out of 5'
        )

    def test_1_usergroups_list(self):
        print('')
        print('test usergroups')

        print('get page /usergroups/list')
        response = self.app.get('/usergroups/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item

    def test_1_usergroups_members(self):
        print('')
        print('test usergroups members')

        # Get a usergroup
        ug = self.datamgr.get_usergroup({'where': {'alias': 'Administrators'}})
        self.assertEqual(ug.name, 'admins')

        print('get page /usergroup/members')
        response = self.app.get('/usergroup/members/' + ug.id)
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item
            assert 'icon' in item
            assert 'url' in item


class Test3Realms(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        response = self.app.get('/logout')

    def test_1_realms(self):
        print('')
        print('test realms')

        print('get page /realms')
        response = self.app.get('/realms')
        response.mustcontain(
            '<div id="realms">',
            # '5 elements out of 5'
        )

        print('get page /realms/tree')
        response = self.app.get('/realms/tree')
        response.mustcontain(
            '<div id="realms_tree_view">',
            # '5 elements out of 5'
        )

    def test_1_realms_list(self):
        print('')
        print('test realms')

        print('get page /realms/list')
        response = self.app.get('/realms/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item



class Test4TargetUser(unittest2.TestCase):

    def setUp(self):
        print("")
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
        print("")
        print("tearing down ...")

        response = self.app.get('/logout')
        redirected_response = response.follow()
        redirected_response.mustcontain('<form role="form" method="post" action="/login">')

    # @unittest2.skip("To be completed  test ...")
    def test_3_1_dashboard(self):
        print('')
        print('test dashboard')

        print('get page /dashboard')
        redirected_response = self.app.get('/dashboard')
        redirected_response.mustcontain(
            'This file is a part of Alignak-WebUI.',
            '<!-- Page header -->',
            '<header>',
            '<nav id="menu-bar">',
            '<!-- Dashboard widgets bar -->',
            '<a data-action="display-currently"',
            '<a data-action="toggle-page-refresh"',
            '<!-- User info -->',
            '<div id="page-wrapper" class="container-fluid header-page">',

            '<div id="dashboard">',
            '<div id="dashboard-synthesis"',
            '<div id="propose-widgets" ',
            '<!-- Widgets loading indicator -->',
            '<div id="widgets_loading"></div>',
            '<!-- Widgets grid -->',
            '<!-- Page footer -->'
        )

        print('get home page /dashboard')
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        print(session['current_user'])
        assert session['current_user'].get_username() == 'admin'
        assert session['current_user'].name == 'admin'
        assert 'target_user' in session and session['target_user']
        print(session['target_user'])
        assert session['target_user'].name == 'anonymous'

        print('get page /users')
        # 4 users
        response = self.app.get('/users')
        response.mustcontain(
            '<div id="users">',
            '5 elements out of 5',
            'admin', 'imported_admin', 'guest', 'anonymous', 'mohier'
        )

        # Current user is admin
        session = response.request.environ['beaker.session']
        assert 'current_user' in session and session['current_user']
        print(session['current_user'])
        assert session['current_user'].name == 'admin'

        # Data manager
        datamgr = session['datamanager']
        user = datamgr.get_user({'where': {'name': 'admin'}})
        assert user
        user = datamgr.get_user({'where': {'name': 'not_admin'}})
        assert not user


        # Get main realm
        realm_all = datamgr.get_realm({'where': {'name': 'All'}})
        assert realm_all

        # Get main TP
        tp_all = datamgr.get_timeperiod({'where': {'name': '24x7'}})
        assert tp_all

        # Create a non admin user ...
        # Create a new user
        print('create a user')
        data = {
            "name": "not_admin",
            "alias": "Testing user - not administrator",
            "note": "Monitoring template : default",
            "min_business_impact": 0,
            "email": "frederic.mohier@gmail.com",

            "is_admin": False,
            "expert": False,
            "can_submit_commands": False,

            "host_notifications_enabled": True,
            "host_notification_period": tp_all.id,
            "host_notification_commands": [
            ],
            "host_notification_options": [
                "d",
                "u",
                "r"
            ],

            "service_notifications_enabled": True,
            "service_notification_period": tp_all.id,
            "service_notification_commands": [ ],
            "service_notification_options": [
                "w",
                "u",
                "c",
                "r"
            ],
            "definition_order": 100,
            "address1": "",
            "address2": "",
            "address3": "",
            "address4": "",
            "address5": "",
            "address6": "",
            "pager": "",
            "notificationways": [],
            "_realm": realm_all.id
        }
        response = self.app.post('/user/add', data)
        assert response.json['status'] == "ok"
        assert response.json['message'] == "User created"

        users = datamgr.get_users()
        self.assertEqual(len(users), 6)

        print('get page /users')
        # Now 5 users
        response = self.app.get('/users')
        response.mustcontain(
            '<div id="users">',
            '6 elements out of 6',
            'admin', 'guest', 'anonymous', 'mohier',
            'not_admin'
        )

        print('get home page /dashboard - no target user')
        response = self.app.get('/dashboard')
        response.mustcontain('<div id="dashboard">')
        assert 'current_user' in session and session['current_user']
        print(session['current_user'])
        assert 'target_user' in session and session['target_user']
        print(session['target_user'])
        assert session['target_user'].name == 'anonymous'

        print('get home page /dashboard - set target user')
        response = self.app.get('/dashboard', {'target_user': 'not_admin'})
        response.mustcontain(
            '<div id="dashboard">'
        )
        print('get home page /dashboard - no target user')
        response = self.app.get('/dashboard')
        response.mustcontain(
            '<div id="dashboard">'
        )
        assert 'current_user' in session and session['current_user']
        assert 'target_user' in session and session['target_user']
        assert session['target_user'].name == 'anonymous'

        print("Current user is:", response.request.environ['beaker.session']['current_user'])
        print("Target user is:", response.request.environ['beaker.session']['target_user'])
        response = self.app.get('/dashboard', {'target_user': 'not_admin'})
        response.mustcontain('<div id="dashboard">')
        print("Current user is:", response.request.environ['beaker.session']['current_user'])
        print("Target user is:", response.request.environ['beaker.session']['target_user'])
        print("Not testable !")

        print('get home page /dashboard - reset target user')
        response = self.app.get('/dashboard', {'target_user': ''})
        response.mustcontain('<div id="dashboard">')

    def test_3_2_users(self):
        print('')
        print('test users')

        print('get page /users')
        response = self.app.get('/users')
        response.mustcontain(
            '<div id="users">',
            '6 elements out of 6'
        )

    def test_3_3_commands(self):
        print('')
        print('test commands')

        print('get page /commands')
        response = self.app.get('/commands')
        response.mustcontain(
            '<div id="commands">',
            '25 elements out of 103',
        )

    def test_3_4_hosts(self):
        print('')
        print('test hosts')

        print('get page /hosts')
        response = self.app.get('/hosts')
        response.mustcontain(
            '<div id="hosts">',
            '13 elements out of 13',
        )

    def test_3_5_services(self):
        print('')
        print('test services')

        print('get page /services')
        response = self.app.get('/services')
        response.mustcontain(
            '<div id="services">',
            '25 elements out of 94',
        )

if __name__ == '__main__':
    unittest.main()
