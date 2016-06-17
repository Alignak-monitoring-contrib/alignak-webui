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
import time
import shlex
import json
import unittest2
import subprocess

from nose import with_setup # optional
from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['WEBUI_DEBUG'] = '1'
os.environ['TEST_WEBUI_CFG'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print "Configuration file", os.environ['TEST_WEBUI_CFG']

from alignak_backend_client.client import Backend, BackendException
from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

import alignak_webui.app
from alignak_webui import webapp

from alignak_webui.objects.datamanager import DataManager
from alignak_webui.utils.datatable import Datatable


from logging import getLogger, DEBUG, INFO, WARNING, ERROR
loggerDm = getLogger('alignak_webui.application')
loggerDm.setLevel(WARNING)
loggerDm = getLogger('alignak_webui.utils.datatable')
loggerDm.setLevel(INFO)
loggerDm = getLogger('alignak_webui.objects.datamanager')
loggerDm.setLevel(WARNING)
loggerDm = getLogger('alignak_webui.objects.item')
loggerDm.setLevel(ERROR)
loggerDm = getLogger('alignak_webui.objects.backend')
loggerDm.setLevel(INFO)

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


from webtest import TestApp

class test_datatable(unittest2.TestCase):
    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

        self.items_count = 0

    def tearDown(self):
        print ""

    def test_01_get(self):
        print ''
        print 'test get table'

        print 'get page /commands_table'
        response = self.app.get('/commands_table')
        response.mustcontain(
            '<div id="command_table">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" class="table ',
            '<th data-name="name" data-type="string">Command name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="command_line" data-type="string">Command line</th>',
            '<th data-name="module_type" data-type="string">Module type</th>',
            '<th data-name="enable_environment_macros" data-type="boolean">Enable environment macros</th>',
            '<th data-name="timeout" data-type="integer">Timeout</th>',
            '<th data-name="poller_tag" data-type="string">Poller tag</th>',
            '<th data-name="reactionner_tag" data-type="string">Reactionner tag</th>'
        )


    def test_02_change(self):
        print ''
        print 'test get table'

        print 'change content with /command_table_data'
        response = self.app.post('/command_table_data')
        response_value = response.json
        print response_value
        # Temporary ...
        self.items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == self.items_count
        # assert response.json['recordsFiltered'] == self.items_count if self.items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        self.assertNotEqual(response.json['data'], [])
        for x in range(0, self.items_count):
            if x < BACKEND_PAGINATION_DEFAULT:
                print response.json['data'][x]
                assert response.json['data'][x]
                assert response.json['data'][x]['name']
                assert response.json['data'][x]['definition_order']
                assert response.json['data'][x]['enable_environment_macros']
                assert response.json['data'][x]['command_line']
                assert response.json['data'][x]['timeout']
                assert response.json['data'][x]['poller_tag']
                assert response.json['data'][x]['reactionner_tag']
                assert response.json['data'][x]['enable_environment_macros']
                # No more ui in the backend
                # self.assertTrue(response.json['data'][x]['ui'])


        # Specify count number ...
        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 10,
        })
        self.assertEqual(response.json['recordsTotal'], self.items_count)
        # Because no filtering is active ... equals to total records
        self.assertEqual(response.json['recordsFiltered'], self.items_count)
        self.assertNotEqual(response.json['data'], [])
        self.assertEqual(len(response.json['data']), 10)


        # Specify count number ... greater than number of elements
        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 1000,
        })
        self.assertEqual(response.json['recordsTotal'], self.items_count)
        # Because no filtering is active ... equals to total records
        self.assertEqual(response.json['recordsFiltered'], self.items_count)
        self.assertNotEqual(response.json['data'], [])
        self.assertEqual(len(response.json['data']), BACKEND_PAGINATION_LIMIT)


        # Rows 5 by 5 ...
        print "Get rows 5 per 5"
        count = 0
        for x in range(0, self.items_count, 5):
            response = self.app.post('/command_table_data', {
                'object_type': 'command',
                'draw': x / 5,
                'start': x,
                'length': 5
            })
            response_value = response.json
            self.assertEqual(response.json['draw'], x / 5)
            self.assertEqual(response.json['recordsTotal'], self.items_count)
            # Because no filtering is active ... equals to total records
            self.assertEqual(response.json['recordsFiltered'], self.items_count)
            self.assertNotEqual(response.json['data'], [])
            self.assertIn(len(response.json['data']), [5, self.items_count % 5])
            count += len(response.json['data'])
        self.assertEqual(count, self.items_count)

        # Out of scope rows ...
        response = self.app.post('/command_table_data', {
            'start': self.items_count*2,
            'length': 5
        })
        response_value = response.json
        self.assertEqual(response.json['recordsTotal'], self.items_count)
        # Because no filtering is active ... equals to total records
        self.assertEqual(response.json['recordsFiltered'], self.items_count)
        self.assertEqual(response.json['data'], [])


    def test_03_sort(self):
        print ''
        print 'test sort table'

        # Sort ascending ...
        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 10,
            'columns': json.dumps([
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]) # Ascending
        })
        self.assertEqual(len(response.json['data']), 10)

        # Sort descending ...
        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 10,
            'columns': json.dumps([
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"desc"}])    # Descending !
        })
        self.assertEqual(len(response.json['data']), 10)

        # TODO : check order of element ?


    def test_04_filter(self):
        print ''
        print 'test filter table'

        print 'change content with /command_table_data'
        response = self.app.post('/command_table_data')
        response_value = response.json
        # Temporary ...
        self.items_count = response.json['recordsTotal']

        # Searching ...
        # Global search ...
        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]),
            # Search 'check_ping' in all columns without regex
            'search': json.dumps({"value":"check_ping","regex":False})
        })
        response_value = response.json
        # Found items_count records and sent 1
        self.assertEqual(response.json['recordsTotal'], self.items_count)
        self.assertEqual(response.json['recordsFiltered'], 1)
        self.assertEqual(len(response.json['data']), 1)

        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]),
            # Search 'close' in all columns without regex
            'search': json.dumps({"value":"check_test","regex":False})
        })
        response_value = response.json
        print response_value
        # Not found!
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 0
        assert not response.json['data']

        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]),
            # Search 'check' in all columns with regex
            'search': json.dumps({"value":"check","regex":True})
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 5
        assert response.json['data']
        assert len(response.json['data']) == 5


        # Searching ...
        # Individual search ...
        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                # Search 'check_ping' in name column ...
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"check_ping","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]),
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 1
        assert response.json['data']
        assert len(response.json['data']) == 1

        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                # Search 'op' in status column ...
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"check","regex":False}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]),
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 0
        assert not response.json['data']

        response = self.app.post('/command_table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                # Search 'check' in name column ... regex True
                {"data":"name","name":"name","searchable":True,"orderable":True,"search":{"value":"check","regex":True}},
                {"data":"definition_order","name":"definition_order","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"command_line","name":"command_line","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"module_type","name":"module_type","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"enable_environment_macros","name":"enable_environment_macros","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"timeout","name":"timeout","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"poller_tag","name":"poller_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
                {"data":"reactionner_tag","name":"reactionner_tag","searchable":True,"orderable":True,"search":{"value":"","regex":False}},
            ]),
            'order': json.dumps([{"column":0,"dir":"asc"}]),
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 5
        assert response.json['data']
        assert len(response.json['data']) == 5


class test_datatable_commands(unittest2.TestCase):
    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

    def tearDown(self):
        print ""

    def test_01_commands(self):
        print ''
        print 'test commands table'

        global items_count

        print 'get page /commands_table'
        response = self.app.get('/commands_table')
        response.mustcontain(
            '<div id="command_table">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" class="table ',
            '<th data-name="name" data-type="string">Command name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="command_line" data-type="string">Command line</th>',
            '<th data-name="module_type" data-type="string">Module type</th>',
            '<th data-name="enable_environment_macros" data-type="boolean">Enable environment macros</th>',
            '<th data-name="timeout" data-type="integer">Timeout</th>',
            '<th data-name="poller_tag" data-type="string">Poller tag</th>',
            '<th data-name="reactionner_tag" data-type="string">Reactionner tag</th>'
        )

        print 'change content with /command_table_data'
        response = self.app.post('/command_table_data')
        response_value = response.json
        print response_value
        # Temporary ...
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count):
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x]
                assert response.json['data'][x]['name']
                assert response.json['data'][x]['definition_order']
                assert response.json['data'][x]['enable_environment_macros']
                assert response.json['data'][x]['command_line']
                assert response.json['data'][x]['timeout']
                assert response.json['data'][x]['poller_tag']
                assert response.json['data'][x]['reactionner_tag']
                assert response.json['data'][x]['enable_environment_macros']
                # No more ui in the backend
                # assert response.json['data'][x]['ui'] == True


class test_datatable_hosts(unittest2.TestCase):
    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

    def tearDown(self):
        print ""

    def test_02_hosts(self):
        print ''
        print 'test hosts table'

        global items_count

        print 'get page /hosts_table'
        response = self.app.get('/hosts_table')
        response.mustcontain(
            '<div id="host_table">',
            "$('#tbl_host').DataTable( {",
            '<table id="tbl_host" class="table ',
            '<th data-name="name" data-type="string">Host name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Host alias</th>',
            '<th data-name="display_name" data-type="string">Host display name</th>',
            '<th data-name="address" data-type="string">Address</th>',
            '<th data-name="check_command" data-type="objectid">Check command</th>',
            '<th data-name="check_command_args" data-type="string">Check command arguments</th>',
            '<th data-name="active_checks_enabled" data-type="boolean">Active checks enabled</th>',
            '<th data-name="passive_checks_enabled" data-type="boolean">Passive checks enabled</th>',
            '<th data-name="parents" data-type="list">Parents</th>',
            '<th data-name="hostgroups" data-type="list">Hosts groups</th>',
            '<th data-name="business_impact" data-type="integer">Business impact</th>'
        )

        response = self.app.post('/host_table_data')
        response_value = response.json
        print response_value
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count+0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x]
                assert response.json['data'][x]['name']


    def test_02_1_hosts_groups(self):
        print ''
        print 'test hostgroup table'

        global items_count

        print 'get page /hostgroup_table'
        response = self.app.get('/hostgroup_table')
        response.mustcontain(
            '<div id="hostgroup_table">',
            "$('#tbl_hostgroup').DataTable( {",
            '<table id="tbl_hostgroup" class="table ',
            '<th data-name="#" data-type="string"></th>',
            '<th data-name="name" data-type="string">Hosts group name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Hosts group alias</th>',
            '<th data-name="hosts" data-type="list">Hosts members</th>',
            '<th data-name="hostgroups" data-type="list">Hosts groups members</th>'
        )

        response = self.app.post('/hostgroup_table_data')
        response_value = response.json
        print response_value
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count+0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print response.json['data'][x]
                assert response.json['data'][x]
                assert response.json['data'][x]['name']
                assert response.json['data'][x]['definition_order']
                assert response.json['data'][x]['alias']
                assert 'hosts' in response.json['data'][x]
                assert 'hostgroups' in response.json['data'][x]


class test_datatable_users(unittest2.TestCase):
    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

    def tearDown(self):
        print ""

    def test_03_users(self):
        print ''
        print 'test users table'

        global items_count

        print 'get page /users_table'
        response = self.app.get('/users_table')
        response.mustcontain(
            '<div id="user_table">',
            "$('#tbl_user').DataTable( {",
            '<table id="tbl_user" class="table ',
            '<th data-name="name" data-type="string">User name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">User alias</th>',
        )

        response = self.app.post('/user_table_data')
        response_value = response.json
        print response_value
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count+0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x]
                assert response.json['data'][x]['name']


class test_datatable_livestate(unittest2.TestCase):
    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

    def tearDown(self):
        print ""

    @unittest2.skip("Do not known why ...")
    def test_04_livestate(self):
        print ''
        print 'test livestate table'

        global items_count

        print 'get page /livestate_table'
        response = self.app.get('/livestate_table')
        response.mustcontain(
            '<div id="livestate_table">',
            "$('#tbl_livestate').DataTable( {",
            '<table id="tbl_livestate" class="table ',
            '<th data-name="#" data-type="string">#</th>',
            '<th data-name="$" data-type="string">&lt;i class=&quot;fa fa-bolt&quot;&gt;&lt;/i&gt;</th>',
            '<th data-name="type" data-type="string">Type</th>',
            '<th data-name="name" data-type="string">Element name</th>',
            '<th data-name="host" data-type="objectid">Host</th>',
            '<th data-name="display_name_host" data-type="string">Host display name</th>',
            '<th data-name="service" data-type="objectid">Service</th>',
            '<th data-name="display_name_service" data-type="string">Host display service</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="business_impact" data-type="integer">Business impact</th>',
            '<th data-name="state" data-type="string">State</th>',
            '<th data-name="state_type" data-type="string">State type</th>',
            '<th data-name="state_id" data-type="integer">State identifier</th>',
            '<th data-name="acknowledged" data-type="boolean">Acknowledged</th>',
            '<th data-name="downtime" data-type="boolean">In scheduled downtime</th>',
            '<th data-name="last_check" data-type="integer">Last check</th>',
            '<th data-name="output" data-type="string">Check output</th>',
            '<th data-name="long_output" data-type="string">Check long output</th>',
            '<th data-name="perf_data" data-type="string">Performance data</th>',
            '<th data-name="current_attempt" data-type="integer">Current attempt</th>',
            '<th data-name="max_attempts" data-type="integer">Max attempts</th>',
            '<th data-name="next_check" data-type="integer">Next check</th>',
            '<th data-name="last_state_changed" data-type="integer">Last check</th>',
            '<th data-name="last_state" data-type="string">Last state</th>',
            '<th data-name="last_state_type" data-type="string">Last state type</th>',
        )

        response = self.app.post('/livestate_table_data')
        print response
        response_value = response.json
        print response_value
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count+0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print response.json['data'][x]
                assert response.json['data'][x]
                assert response.json['data'][x]['#']
                assert response.json['data'][x]['$']
                assert response.json['data'][x]['type']
                assert response.json['data'][x]['name']
                assert response.json['data'][x]['state']
                assert response.json['data'][x]['host']
                if response.json['data'][x]['type'] == 'service':
                    assert response.json['data'][x]['service'] is not None
                else:
                    assert response.json['data'][x]['service'] is None


class test_datatable_log(unittest2.TestCase):
    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(
            webapp
        )

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

    def tearDown(self):
        print ""

    def test_05_logcheckresult(self):
        print ''
        print 'test logcheckresult table'

        global items_count

        print 'get page /logcheckresult_table'
        response = self.app.get('/logcheckresult_table')
        response.mustcontain(
            '<div id="logcheckresult_table">',
            "$('#tbl_logcheckresult').DataTable( {",
            '<table id="tbl_logcheckresult" class="table ',
            '<th data-name="#" data-type="string"></th>',
            '<th data-name="host" data-type="objectid">Host</th>',
            '<th data-name="service" data-type="objectid">Service</th>',
            '<th data-name="state" data-type="string">State</th>',
            '<th data-name="state_type" data-type="string">State type</th>',
            '<th data-name="state_id" data-type="integer">State identifier</th>',
            '<th data-name="acknowledged" data-type="boolean">Acknowledged</th>',
            '<th data-name="last_check" data-type="integer">Last check</th>',
            '<th data-name="last_state" data-type="string">Last state</th>',
            '<th data-name="output" data-type="string">Check output</th>',
            '<th data-name="long_output" data-type="string">Check long output</th>',
            '<th data-name="perf_data" data-type="string">Performance data</th>',
            '<th data-name="latency" data-type="float">Latency</th>',
            '<th data-name="execution_time" data-type="float">Execution time</th>',
        )

        response = self.app.post('/logcheckresult_table_data')
        response_value = response.json
        print response_value
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT

        # No data in the test backend