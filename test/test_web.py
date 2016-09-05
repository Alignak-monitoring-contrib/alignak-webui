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
import re
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
        print("Starting Alignak backend...")
        fnull = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('alignak_backend'), stdout=fnull
        )
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


class TestDashboard(unittest2.TestCase):
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
        )


class TestUsers(unittest2.TestCase):
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


class TestCommands(unittest2.TestCase):
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


class TestTimeperiods(unittest2.TestCase):
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


class TestRealms(unittest2.TestCase):
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


class TestHostgroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']

        self.group_id = None

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

        print('get page /hostgroups/tree')
        response = self.app.get('/hostgroups/tree')
        # Search for: "id": '57bebb4006fd4b149768dc3f' to find a group id
        matches = re.findall(r"""\"id\": '([0-9a-f].*)'""", response.body)
        if matches:
            for match in matches:
                print("Found id: %s" % match)
                self.group_id = match
        assert self.group_id

        print('get page /hostgroup/members')
        assert self.group_id
        response = self.app.get('/hostgroup/members/' + self.group_id)
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item
            assert 'icon' in item
            assert 'url' in item


class TestServicegroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']

        self.group_id = None

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

        print('get page /servicegroups/tree')
        response = self.app.get('/servicegroups/tree')
        # Search for: "id": '57bebb4006fd4b149768dc3f' to find a group id
        matches = re.findall(r"""\"id\": '([0-9a-f].*)'""", response.body)
        if matches:
            for match in matches:
                print("Found id: %s" % match)
                self.group_id = match
        assert self.group_id

        print('get page /servicegroup/members')
        response = self.app.get('/servicegroup/members/' + self.group_id)
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item
            assert 'icon' in item
            assert 'url' in item


class TestUsergroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(
            webapp
        )
        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']

        self.group_id = None

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

        response = self.app.get('/usergroups/tree')
        # Search for: "id": '57bebb4006fd4b149768dc3f' to find a group id
        matches = re.findall(r"""\"id\": '([0-9a-f].*)'""", response.body)
        if matches:
            for match in matches:
                print("Found id: %s" % match)
                self.group_id = match
        assert self.group_id

        print('get page /usergroup/members')
        response = self.app.get('/usergroup/members/' + self.group_id)
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item
            assert 'icon' in item
            assert 'url' in item


class TestHosts(unittest2.TestCase):
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


class TestServices(unittest2.TestCase):
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


class TestWorldmap(unittest2.TestCase):
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


class TestMinemap(unittest2.TestCase):
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


if __name__ == '__main__':
    unittest.main()
