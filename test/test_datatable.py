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


from logging import getLogger, DEBUG, INFO, WARNING
loggerDm = getLogger('alignak_webui.utils.datatable')
loggerDm.setLevel(DEBUG)

pid = None
backend_address = "http://127.0.0.1:5000/"

def setup_module(module):
    print ("")
    print ("start applications backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['TEST_ALIGNAK_BACKEND_DB'] = 'test_alignak_webui-datatable'

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

    def tearDown(self):
        print ""
        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.get_logged_user() == None
        assert self.dmg.loaded == False

    def test_01_ccomands(self):
        print ''
        print 'test commands table'

        global items_count

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

        print 'get page /commands_table'
        response = self.app.get('/commands_table')
        response.mustcontain(
            '<div id="commands_table">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" class="table table-striped" cellspacing="0" width="100%">',
            '<th data-name="name" data-type="string">Command name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="command_line" data-type="string">Command line</th>',
            '<th data-name="module_type" data-type="string">Module type</th>',
            '<th data-name="enable_environment_macros" data-type="boolean">Enable environment macros</th>',
            '<th data-name="timeout" data-type="integer">Timeout</th>',
            '<th data-name="poller_tag" data-type="string">Poller tag</th>',
            '<th data-name="reactionner_tag" data-type="string">Reactionner tag</th>'
        )

        print 'change content with /commands_table_data'
        response = self.app.post('/commands_table_data')
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
                assert response.json['data'][x]['ui'] == True


        # Rows 5 by 5 ...
        for x in range(0, items_count, 5):
            response = self.app.post('/commands_table_data', {
                'draw': x / 5,
                'start': x,
                'length': 5
            })
            response_value = response.json
            print response_value
            assert response.json['draw'] == x / 5
            assert response.json['recordsTotal'] == items_count
            assert response.json['recordsFiltered'] == 5
            assert response.json['data']
            assert len(response.json['data']) == 5

        # Out of scope rows ...
        response = self.app.post('/commands_table_data', {
            'start': items_count+1,
            'length': 5
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == items_count
        assert not response.json['data']

        # Sorting ...
        response = self.app.post('/commands_table_data', {
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
            'order': json.dumps([{"column":0,"dir":"asc"}]) # Ascending
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == 5
        assert response.json['data']
        assert len(response.json['data']) == 5

        response = self.app.post('/commands_table_data', {
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
            'order': json.dumps([{"column":0,"dir":"desc"}])    # Descending !
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == 5
        assert response.json['data']
        assert len(response.json['data']) == 5

        # Searching ...
        # Global search ...
        response = self.app.post('/commands_table_data', {
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
            # Search 'open' in all columns without regex
            'search': json.dumps({"value":"check_ping","regex":False})
        })
        response_value = response.json
        print response_value
        # Found items_count records and sent 1
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == 1
        assert response.json['data']
        assert len(response.json['data']) == 1

        response = self.app.post('/commands_table_data', {
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
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == 0
        assert not response.json['data']

        response = self.app.post('/commands_table_data', {
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
            # Search 'open' in all columns with regex
            'search': json.dumps({"value":"check","regex":True})
        })
        response_value = response.json
        print response_value
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == items_count
        assert response.json['data']
        assert len(response.json['data']) == 5


        # Searching ...
        # Individual search ...
        response = self.app.post('/commands_table_data', {
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
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == 1
        assert response.json['data']
        assert len(response.json['data']) == 1

        response = self.app.post('/commands_table_data', {
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
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == 0
        assert not response.json['data']

        response = self.app.post('/commands_table_data', {
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
        assert response.json['recordsTotal'] == items_count
        assert response.json['recordsFiltered'] == items_count
        assert response.json['data']
        assert len(response.json['data']) == 5


    def test_02_hosts(self):
        print ''
        print 'test hosts table'

        global items_count

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

        print 'get page /sessions_table'
        response = self.app.get('/hosts_table')
        response.mustcontain(
            '<div id="hosts_table">',
            "$('#tbl_host').DataTable( {",
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

        response = self.app.post('/hosts_table_data')
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
                assert response.json['data'][x]['ui'] == True
