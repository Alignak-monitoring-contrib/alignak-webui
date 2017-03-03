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
import re
import time
import shlex
import unittest2
import subprocess
import requests

from mock import Mock, patch

from nose.tools import *

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app

from alignak_webui.backend.datamanager import DataManager
import alignak_webui.utils.datatable

import bottle
from bottle import BaseTemplate, TEMPLATE_PATH

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


class TestLivestate(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_livestate(self):
        """ Web - livestate """
        print('get page /livestate')
        redirected_response = self.app.get('/livestate')
        print(redirected_response)
        redirected_response.mustcontain(
            '<div id="livestate-bi--1">'
        )


class TestCurrently(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_currently(self):
        """ Web - currently """
        print('get page /currently')
        redirected_response = self.app.get('/currently')
        print(redirected_response)
        # assert False
        redirected_response.mustcontain(
            '<div id="currently">',
            '<div id="one-eye-hosts"',
            '<div id="one-eye-services"',
            '<div id="ls-history-hosts"',
            '<div id="ls-history-services"',
        )


class TestDashboard(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_dashboard(self):
        """ Web - dashboard """
        print('get page /dashboard')
        redirected_response = self.app.get('/dashboard')
        print(redirected_response)
        redirected_response.mustcontain(
            '<div id="dashboard">',
            '<div id="problems-synthesis"',
            '<div id="propose-widgets"',
            '<!-- Widgets grid -->',
            '<div class="grid-stack">'
        )


class TestCommands(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_commands(self):
        """ Web - commands """
        print('test commands')

        print('get page /commands')
        response = self.app.get('/commands')
        response.mustcontain(
            '<div id="commands">',
            '25 elements out of ',
        )
        self.app.get('/commands/config')
        self.app.get('/commands/list')
        self.app.get('/commands/table')


class TestTimeperiods(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_timeperiods(self):
        """ Web - timeperiods """
        print('test timeperiods')

        print('get page /timeperiods')
        response = self.app.get('/timeperiods')
        response.mustcontain(
            '<div id="timeperiods">',
            '4 elements out of 4',
        )
        self.app.get('/timeperiods/config')
        self.app.get('/timeperiods/list')
        self.app.get('/timeperiods/table')


class TestRealms(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

        self.realm_id = None

    def tearDown(self):
        self.app.get('/logout')

    def test_realms(self):
        """ Web - realms """
        print('test realms')

        print('get page /realms')
        response = self.app.get('/realms')
        response.mustcontain(
            '<div id="realms">',
            # '5 elements out of 5'
        )

        self.app.get('/realms/config')
        self.app.get('/realms/list')
        self.app.get('/realms/table')
        # self.app.get('/realms/all')

        print('get page /realms/tree')
        response = self.app.get('/realms/tree')
        response.mustcontain(
            '<div id="realms_tree_view">',
            # '5 elements out of 5'
        )

    def test_realm(self):
        """ Web - realm"""
        print('test realm')

        print('get page /realms')
        response = self.app.get('/realms')
        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a realm id
        matches = re.findall(r'<tr id="#([0-9a-f].*)">', response.body)
        if matches:
            for match in matches:
                self.realm_id = match
                break
        assert self.realm_id, "Did not found realm identifier in the data!"

        print('get page /realm')
        response = self.app.get('/realm/%s' % self.realm_id)
        response.mustcontain(
            '<div class="realm" id="realm-%s">' % self.realm_id
        )

        print('get page /realm/members')
        response = self.app.get('/realm/members/%s' % self.realm_id)
        # print(response)
        print(response.json)
        for item in response.json:
            print(item)
            assert "id" in item
            assert "type" in item
            assert item['type'] == "host"

            if item['id'] == -1:
                assert "tr" in item
                continue
            assert "name" in item
            assert "icon" in item
            assert "alias" in item
            assert "state" in item
            assert "status" in item


class TestHostgroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']

        self.group_id = None

    def tearDown(self):
        self.app.get('/logout')

    def test_hostgroups(self):
        """ Web - hostgroups"""
        print('test hostgroups')

        print('get page /hostgroups')
        response = self.app.get('/hostgroups')
        response.mustcontain(
            '<div id="hostgroups">',
            # '8 elements out of 8'
        )
        self.app.get('/hostgroups/config')
        self.app.get('/hostgroups/list')
        self.app.get('/hostgroups/table')
        self.app.get('/hostgroup/all')

        print('get page /hostgroups/tree')
        response = self.app.get('/hostgroups/tree')
        response.mustcontain(
            '<div id="hostgroups_tree_view">',
            # '8 elements out of 8'
        )

    def test_hostgroups_list(self):
        """ Web - hostgroups list"""
        print('test hostgroups')

        print('get page /hostgroups/list')
        response = self.app.get('/hostgroups/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item

    def test_hostgroups_members(self):
        """ Web - hostgroups members"""
        print('test hostgroups members')

        print('get page /hostgroups/tree')
        response = self.app.get('/hostgroups/tree')
        print(response)
        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a group id
        matches = re.findall(r'"id": "([0-9a-f].*)", "icon"', response.body)
        if matches:
            for match in matches:
                print("Found id: %s" % match)
                self.group_id = match
        assert self.group_id

        print('get page /hostgroup/members for %s' % self.group_id)
        assert self.group_id
        response = self.app.get('/hostgroup/members/' + self.group_id)
        print(response.json)
        for item in response.json:
            print(item)
            assert "id" in item
            assert "type" in item
            assert item['type'] == "host"

            if item['id'] == -1:
                assert "tr" in item
                continue
            assert "name" in item
            assert "icon" in item
            assert "alias" in item
            assert "state" in item
            assert "status" in item


class TestServicegroups(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']

        self.group_id = None

    def tearDown(self):
        self.app.get('/logout')

    def test_servicegroups(self):
        """ Web - servicegroups"""
        print('test servicegroups')

        print('get page /servicegroups')
        response = self.app.get('/servicegroups')
        response.mustcontain(
            '<div id="servicegroups">',
            # '5 elements out of 5'
        )
        self.app.get('/servicegroups/config')
        self.app.get('/servicegroups/list')
        self.app.get('/servicegroups/table')
        self.app.get('/servicegroup/all')

        print('get page /servicegroups/tree')
        response = self.app.get('/servicegroups/tree')
        response.mustcontain(
            '<div id="servicegroups_tree_view">',
            # '5 elements out of 5'
        )

    def test_servicegroups_list(self):
        """ Web - servicegroups list"""
        print('test servicegroups')

        print('get page /servicegroups/list')
        response = self.app.get('/servicegroups/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item

    def test_servicegroups_members(self):
        """ Web - servicegroups members"""
        print('test servicegroups members')

        print('get page /servicegroups/tree')
        response = self.app.get('/servicegroups/tree')
        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a group id
        matches = re.findall(r'"id": "([0-9a-f].*)", "icon"', response.body)
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
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        self.session = response.request.environ['beaker.session']

        self.group_id = None

    def tearDown(self):
        self.app.get('/logout')

    def test_usergroups(self):
        """ Web - usergroups"""
        print('test usergroups')

        print('get page /usergroups')
        response = self.app.get('/usergroups')
        response.mustcontain(
            '<div id="usergroups">',
            # '5 elements out of 5'
        )
        self.app.get('/usergroups/config')
        self.app.get('/usergroups/list')
        self.app.get('/usergroups/table')
        self.app.get('/usergroup/all')

        print('get page /usergroups/tree')
        response = self.app.get('/usergroups/tree')
        response.mustcontain(
            '<div id="usergroups_tree_view">',
            # '5 elements out of 5'
        )

    def test_usergroups_list(self):
        """ Web - usergroups list"""
        print('test usergroups')

        print('get page /usergroups/list')
        response = self.app.get('/usergroups/list')
        print(response.json)
        for item in response.json:
            assert 'id' in item
            assert 'name' in item
            assert 'alias' in item

    def test_usergroups_members(self):
        """ Web - usergroups members"""
        print('test usergroups members')

        response = self.app.get('/usergroups/tree')
        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a group id
        matches = re.findall(r'"id": "([0-9a-f].*)", "icon"', response.body)
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
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

        self.host_id = None

    def tearDown(self):
        self.app.get('/logout')

    def test_hosts(self):
        """ Web - hosts"""
        print('test hosts')

        print('get page /hosts')
        response = self.app.get('/hosts')
        response.mustcontain(
            '<div id="hosts">',
            '13 elements out of 13',
        )
        self.app.get('/hosts/config')
        self.app.get('/hosts/list')
        self.app.get('/hosts/table')
        self.app.get('/hosts/templates/list')
        self.app.get('/hosts/templates/table')
        self.app.get('/host/localhost')

        print('get page /hosts/widget')
        self.app.post('/hosts/widget', status=204)
        self.app.post('/hosts/widget', {'widget_id': 'test_widget'}, status=204)

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

    def test_host(self):
        """ Web - host"""
        print('test host')

        print('get page /hosts')
        response = self.app.get('/hosts')
        print(response)
        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a host id
        matches = re.findall(r'<tr id="#([0-9a-f].*)">', response.body)
        if matches:
            for match in matches:
                self.host_id = match
                break
        assert self.host_id

        print('get page /host')
        response = self.app.get('/host/%s' % self.host_id)
        print(response)
        response.mustcontain(
            '<div id="host-%s">' % self.host_id
        )


class TestServices(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

        self.host_id = None
        self.service_id = None

    def tearDown(self):
        self.app.get('/logout')

    def test_services(self):
        """ Web - services"""
        print('test services')

        print('get page /services')
        response = self.app.get('/services')
        response.mustcontain(
            '<div id="services">'
        )
        response = self.app.get('/services/config')
        response = self.app.get('/services/list')
        response = self.app.get('/services/table')
        response = self.app.get('/services/templates/list')
        response = self.app.get('/services/templates/table')

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

    def test_service(self):
        """ Web - service"""
        print('test service')

        print('get page /hosts')
        response = self.app.get('/hosts')
        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a host id
        matches = re.findall(r'<tr id="#([0-9a-f].*)">', response.body)
        if matches:
            for match in matches:
                self.host_id = match
                break
        assert self.host_id

        print('get page /host')
        response = self.app.get('/host/%s' % self.host_id)
        print(response)
        response.mustcontain(
            '<div id="host-%s">' % self.host_id
        )

        # Search for: "id": "57bebb4006fd4b149768dc3f" to find a host id
        matches = re.findall(r'<tr id="#service-([0-9a-f].*)">', response.body)
        if matches:
            for match in matches:
                print("Found id: %s" % match)
                self.service_id = match
        assert self.service_id

        print('get page /service')
        response = self.app.get('/service/%s' % self.service_id)
        response.mustcontain(
            '<div id="service-%s">' % self.service_id
        )


class TestUsers(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_users(self):
        """ Web - users """
        print('test users')

        print('get page /users')
        response = self.app.get('/users')
        response.mustcontain(
            '<div id="users">',
            '5 elements out of 5',
        )
        self.app.get('/users/config')
        self.app.get('/users/list')
        self.app.get('/users/table')
        self.app.get('/users/templates/list')
        self.app.get('/users/templates/table')


class TestWorldmap(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_worldmap(self):
        """ Web - worldmap"""
        print('test worldmap')

        print('get page /worldmap')
        response = self.app.get('/worldmap')
        response.mustcontain(
            '<div id="hostsMap">'
        )

        # Widget (temporarily disabled, as of #212)
        # response = self.app.post('/worldmap/widget', {
        #     'widget_id': 'worldmap_1',
        #     'widget_template': 'worldmap_widget'
        # })
        # response.mustcontain(
        #     '<div id="wd_panel_worldmap_1" class="panel panel-default alignak_webui_widget ">'
        # )


class TestMinemap(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_minemap(self):
        """ Web - minemap"""
        print('test minemap')

        print('get page /minemap')
        response = self.app.get('/minemap')
        response.mustcontain(
            '<div id="minemap"'
        )


class TestAlignakDaemons(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    def test_alignak(self):
        """ Web - minemap"""
        print('test daemons')

        print('get page /alignak')
        response = self.app.get('/alignak')
        response.mustcontain(
            '<div id="alignak_daemons"',
            '<div class="text-center alert alert-warning">',
            '<h4>No elements found.</h4>'
        )

        # Widget
        print('get page /alignak/widget')
        self.app.post('/alignak/widget', status=204)
        self.app.post('/alignak/widget', {'widget_id': 'test_widget'}, status=204)

        # Hosts table
        response = self.app.post('/alignak/widget', {
            'widget_id': 'alignak_table_1',
            'widget_template': 'alignak_table_widget'
        })
        print(response)
        response.mustcontain(
            '<div id="wd_panel_alignak_table_1" class="panel panel-default alignak_webui_widget ">',
            '<h4>No Alignak daemons state available...</h4>'
        )


# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

        def raise_for_status(self):
            http_error_msg = ''
            if 400 <= self.status_code < 500:
                http_error_msg = u'%s Error' % (self.status_code)
            elif 500 <= self.status_code < 600:
                http_error_msg = u'%s Error' % (self.status_code)

            if http_error_msg:
                raise requests.HTTPError(http_error_msg, response=self)

            return

    if args[0] == 'http://127.0.0.1:8888/alignak_map':
        data = {
            'arbiter': {
                'arbiter-master': {
                    'passive': False,
                    'realm_name': "All",
                    'polling_interval': 1,
                    'alive': True,
                    'manage_arbiters': False,
                    'manage_sub_realms': False,
                    'is_sent': False,
                    'spare': False,
                    'check_interval': 60,
                    'address': "127.0.0.1",
                    'reachable': True,
                    'max_check_attempts': 3,
                    'last_check': 0,
                    'port': 7770
                }
            },
            'scheduler': {
                'scheduler-master': {
                    'passive': False,
                    'realm_name': "All",
                    'polling_interval': 1,
                    'alive': True,
                    'manage_arbiters': False,
                    'manage_sub_realms': False,
                    'is_sent': False,
                    'spare': False,
                    'check_interval': 60,
                    'address': "127.0.0.1",
                    'reachable': True,
                    'max_check_attempts': 3,
                    'last_check': 1478064129.016136,
                    'port': 7768
                },
                'scheduler-north': {
                    'passive': False,
                    'realm_name': "North",
                    'polling_interval': 1,
                    'alive': True,
                    'manage_arbiters': False,
                    'manage_sub_realms': False,
                    'is_sent': False,
                    'spare': False,
                    'check_interval': 60,
                    'address': "127.0.0.1",
                    'reachable': True,
                    'max_check_attempts': 3,
                    'last_check': 1478064129.016136,
                    'port': 7768
                },
                'scheduler-south': {
                    'passive': False,
                    'realm_name': "All",
                    'polling_interval': 1,
                    'alive': True,
                    'manage_arbiters': False,
                    'manage_sub_realms': False,
                    'is_sent': False,
                    'spare': False,
                    'check_interval': 60,
                    'address': "127.0.0.1",
                    'reachable': True,
                    'max_check_attempts': 3,
                    'last_check': 1478064129.016136,
                    'port': 7768
                },
            },
            # Leave it empty for testing ...
            'reactionner': {},
            'broker': {},
            'receiver': {},
            'poller': {}
        }
        return MockResponse(data, 200)
    # elif args[0] == 'http://127.0.0.1:5000/user':
    #     data = {
    #         u'_items': [
    #             {u'_templates': [], u'_template_fields': {}, u'service_notifications_enabled': True,
    #              u'can_submit_commands': False,
    #              u'_realm': u'587329ab06fd4b0f4e5f5e4f', u'_sub_realm': True,
    #              u'can_update_livestate': True,
    #              u'service_notification_options': [u'w', u'u', u'c', u'r', u'f', u's'],
    #              u'_is_template': False, u'definition_order': 100, u'tags': [], u'address1': u'',
    #              u'address2': u'', u'address3': u'', u'address4': u'', u'address5': u'',
    #              u'address6': u'', u'customs': {}, u'is_admin': False,
    #              u'back_role_super_admin': True,
    #              u'password': u'pbkdf2:sha1:1000$wgg9w07u$53b213ec7f5a48e05828555e90a3d76197365217',
    #              u'pager': u'', u'imported_from': u'unknown', u'notificationways': [],
    #              u'host_notification_period': u'587329ac06fd4b0f4e5f5e53', u'name': u'admin',
    #              u'host_notifications_enabled': True, u'notes': u'',
    #              u'service_notification_period': u'587329ac06fd4b0f4e5f5e53',
    #              u'min_business_impact': 0, u'email': u'', u'alias': u'Administrator',
    #              u'token': u'1483942317310-b4545669-e5d0-48a9-90fe-7195a6608998',
    #              u'ui_preferences': {}, u'_created': u'Mon, 09 Jan 2017 06:11:56 GMT',
    #              u'_id': u'587329ac06fd4b0f4e5f5e58',
    #              u'host_notification_options': [u'd', u'u', u'r', u'f', u's']}],
    #         u'_status': u'OK'
    #     }
    #     return MockResponse(data, 200)
    # elif args[0] == 'http://127.0.0.1:5000/realm':
    #     data = {
    #         u'_items': [
    #             {'_notes': u'',
    #              '_all_children': [u'58732aef06fd4b1039cc0bca', u'58732aef06fd4b1039cc0bcb',
    #                                u'58732aef06fd4b1039cc0bcc', u'58732aef06fd4b1039cc0bcd'],
    #              'services_warning_threshold': 3, 'global_critical_threshold': 5, '_name': u'All',
    #              '_links': {
    #                  u'self': {u'href': u'realm/58732aed06fd4b1039cc0bbf', u'title': u'Realm'}},
    #              '_linked__parent': 'realm', '_tree_parents': [], 'services_critical_threshold': 5,
    #              '_total': 5, '_type': 'realm', 'global_warning_threshold': 3,
    #              'definition_order': 100, '_default_date': 0, 'hosts_critical_threshold': 5,
    #              'imported_from': u'unknown', '_updated': 1483942639, '_level': 0, 'default': True,
    #              'hosts_warning_threshold': 3, '_alias': u'',
    #              '_created': 1483942637,
    #              '_id': u'58732aed06fd4b1039cc0bbf',
    #              '_etag': u'456d8f0de882f108f793277ed4c922a7d02ed41c'
    #              }
    #         ],
    #         u'_status': u'OK'
    #     }
    #     return MockResponse(data, 200)
    #
    # return MockResponse({}, 404)


class TestAlignakWS(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    @unittest2.skip("Too many requests.get to be patched :/")
    @patch('alignak_webui.backend.alignak_ws_client.requests.get', side_effect=mocked_requests_get)
    def test_daemons(self, mock_login):
        """ Web - daemons """
        print('get page /alignak')
        response = self.app.get('/alignak')
        response.mustcontain(
            '<div id="alignak"'
        )


if __name__ == '__main__':
    unittest.main()
