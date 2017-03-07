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

import json
import os
import shlex
import subprocess
import time

import unittest2

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app

from webtest import TestApp

from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

from alignak_webui.backend.backend import BackendConnection
from alignak_webui.objects.item_command import Command
from alignak_webui.backend.datamanager import DataManager

items_count = 0
backend_process = None

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

# ---
# Generic tests for the data tables
# ---
class TestDataTable(unittest2.TestCase):

    """Generic datatables tests

    Those tests are done with the commands table. It was needed to use one :)
    """
    def setUp(self):
        self.dmg = DataManager(backend_endpoint='http://127.0.0.1:5000')
        print('Data manager', self.dmg)

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /livestate
        redirected_response = response.follow()
        redirected_response.follow()

        self.items_count = 0

    def test_get(self):
        """ Datatable - get table """
        print('test get table')

        print('get page /commands/table')
        response = self.app.get('/commands/table')
        # Other fields exist but they are declared as hidden!
        response.mustcontain(
            '<div id="commands_table" class="alignak_webui_table ">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" ',
            '<th data-name="name" data-type="string"',
            # '<th data-name="_realm" data-type="objectid">Realm</th>',
            # '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string"',
            '<th data-name="notes" data-type="string"',
            '<th data-name="command_line" data-type="string"',
            '<th data-name="timeout" data-type="integer"',
            # '<th data-name="enable_environment_macros" data-type="boolean">Enable environment macros</th>',
            '<th data-name="poller_tag" data-type="string"',
            '<th data-name="reactionner_tag" data-type="string"'
        )

    def test_02_change(self):
        """ Datatable - change content """
        print('test get table')

        print('change content with /commands/table_data')
        response = self.app.post('/commands/table_data')
        response_value = response.json
        # Temporary ...
        self.items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == self.items_count
        # assert response.json['recordsFiltered'] == self.items_count
        # if self.items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data'] != []
        for x in range(0, self.items_count):
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x] is not None
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['alias'] is not None
                assert response.json['data'][x]['notes'] is not None
                # assert response.json['data'][x]['definition_order'] is not None
                # assert response.json['data'][x]['enable_environment_macros'] is not None
                assert response.json['data'][x]['command_line'] is not None
                assert response.json['data'][x]['timeout'] is not None
                assert response.json['data'][x]['poller_tag'] is not None
                assert response.json['data'][x]['reactionner_tag'] is not None
                # assert response.json['data'][x]['enable_environment_macros'] is not None

        # Specify count number ...
        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 10,
        })
        assert response.json['recordsTotal'] == self.items_count
        # Because no filtering is active ... equals to total records
        assert response.json['recordsFiltered'] == self.items_count
        assert response.json['data'] != []
        assert len(response.json['data']) == 10

        # Specify count number ... greater than number of elements
        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 1000,
        })
        assert response.json['recordsTotal'] == self.items_count
        # Because no filtering is active ... equals to total records
        assert response.json['recordsFiltered'] == self.items_count
        assert response.json['data'] != []
        assert len(response.json['data']) == BACKEND_PAGINATION_LIMIT

        # Rows 5 by 5 ...
        print("Get rows 5 per 5")
        count = 0
        for x in range(0, self.items_count, 5):
            response = self.app.post('/commands/table_data', {
                'object_type': 'command',
                'draw': x / 5,
                'start': x,
                'length': 5
            })
            response_value = response.json
            assert response.json['draw'] == x / 5
            assert response.json['recordsTotal'] == self.items_count
            # Because no filtering is active ... equals to total records
            assert response.json['recordsFiltered'] == self.items_count
            assert response.json['data'] != []
            assert len(response.json['data']) in [5, self.items_count % 5]
            count += len(response.json['data'])
        assert count == self.items_count

        # Out of scope rows ...
        response = self.app.post('/commands/table_data', {
            'start': self.items_count * 2,
            'length': 5
        })
        response_value = response.json
        # No records!
        assert response.json['recordsTotal'] == 0
        assert response.json['recordsFiltered'] == 0
        assert response.json['data'] == []

    def test_03_sort(self):
        """ Datatable - sort table """
        print('test sort table')

        # Sort ascending ...
        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 10,
            'columns': json.dumps([
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}])  # Ascending
        })
        assert len(response.json['data']) == 10

        # Sort descending ...
        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 10,
            'columns': json.dumps([
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "desc"}])  # Descending !
        })
        assert len(response.json['data']) == 10

        # TODO : check order of element ?

    def test_04_filter(self):
        """ Datatable - filter table """
        print('test filter table')

        print('change content with /commands/table_data')
        response = self.app.post('/commands/table_data')
        response_value = response.json
        # Temporary ...
        self.items_count = response.json['recordsTotal']

        # Searching ...
        # Global search ...
        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}]),
            # Search 'check_ping' in all columns without regex
            'search': json.dumps({"value": "check_ping", "regex": False})
        })
        response_value = response.json
        # Found items_count records and sent 1
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 1
        assert len(response.json['data']) == 1

        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}]),
            # Search 'close' in all columns without regex
            'search': json.dumps({"value": "check_test", "regex": False})
        })
        response_value = response.json
        # Not found!
        assert response.json['recordsTotal'] == 0
        assert response.json['recordsFiltered'] == 0
        assert not response.json['data']

        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}]),
            # Search 'check' in all columns with regex
            'search': json.dumps({"value": "check", "regex": True})
        })
        response_value = response.json
        print(response_value)
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 88
        assert response.json['data']
        assert len(response.json['data']) == 5

        # Searching ...
        # Individual search ...
        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                # Search 'check_ping' in name column ...
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "check_ping", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}]),
        })
        response_value = response.json
        print(response_value)
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 1
        assert response.json['data']
        assert len(response.json['data']) == 1

        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                # Search 'op' in status column ...
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "check", "regex": False}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}]),
        })
        response_value = response.json
        print(response_value)
        # Not found!
        assert response.json['recordsTotal'] == 0
        assert response.json['recordsFiltered'] == 0
        assert not response.json['data']

        response = self.app.post('/commands/table_data', {
            'object_type': 'command',
            'start': 0,
            'length': 5,
            'columns': json.dumps([
                # Search 'check' in name column ... regex True
                {"data": "name", "name": "name", "searchable": True, "orderable": True,
                 "search": {"value": "check", "regex": True}},
                {"data": "definition_order", "name": "definition_order", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "command_line", "name": "command_line", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "module_type", "name": "module_type", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "enable_environment_macros", "name": "enable_environment_macros",
                 "searchable": True, "orderable": True, "search": {"value": "", "regex": False}},
                {"data": "timeout", "name": "timeout", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "poller_tag", "name": "poller_tag", "searchable": True, "orderable": True,
                 "search": {"value": "", "regex": False}},
                {"data": "reactionner_tag", "name": "reactionner_tag", "searchable": True,
                 "orderable": True, "search": {"value": "", "regex": False}},
            ]),
            'order': json.dumps([{"column": 0, "dir": "asc"}]),
        })
        response_value = response.json
        print(response_value)
        assert response.json['recordsTotal'] == self.items_count
        assert response.json['recordsFiltered'] == 88
        assert response.json['data']
        assert len(response.json['data']) == 5


# ---
# then specific tests for each defined table
# ---
class TestDatatableBase(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response.follow()

class TestDatatableCommands(TestDatatableBase):
    def test_commands(self):
        """ Datatable - commands table """
        print('test commands table')

        print('get page /commands')
        response = self.app.get('/commands')

        print('get page /commands/table')
        response = self.app.get('/commands/table')
        response.mustcontain(
            '<div id="commands_table" class="alignak_webui_table ">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="notes" data-type="string"',
            '<th data-name="command_line" data-type="string"',
            '<th data-name="poller_tag" data-type="string"',
            '<th data-name="reactionner_tag" data-type="string"',
        )

        print('change content with /commands/table_data')
        response = self.app.post('/commands/table_data')
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count):
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x] is not None
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['alias'] is not None
                assert response.json['data'][x]['notes'] is not None
                # assert response.json['data'][x]['definition_order'] is not None
                # assert response.json['data'][x]['enable_environment_macros'] is not None
                assert response.json['data'][x]['command_line'] is not None
                assert response.json['data'][x]['timeout'] is not None
                assert response.json['data'][x]['poller_tag'] is not None
                assert response.json['data'][x]['reactionner_tag'] is not None
                # assert response.json['data'][x]['enable_environment_macros'] is not None


class TestDatatableRealms(TestDatatableBase):
    def test_realms(self):
        """ Datatable - realms table """
        print('test realm table')

        print('get page /realms/table')
        response = self.app.get('/realms/table')
        response.mustcontain(
            '<div id="realms_table" class="alignak_webui_table ">',
            "$('#tbl_realm').DataTable( {",
            '<table id="tbl_realm" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="definition_order" data-type="integer"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="default" data-type="boolean"',
            '<th data-name="_level" data-type="integer"',
            '<th data-name="_parent" data-type="objectid"',
            '<th data-name="hosts_critical_threshold" data-type="integer"',
            '<th data-name="hosts_warning_threshold" data-type="integer"',
            '<th data-name="services_critical_threshold" data-type="integer"',
            '<th data-name="services_warning_threshold" data-type="integer"',
            '<th data-name="global_critical_threshold" data-type="integer"',
            '<th data-name="global_warning_threshold" data-type="integer"'
        )

        response = self.app.post('/realms/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print(response.json['data'][x])
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['alias'] is not None


class TestDatatableHosts(TestDatatableBase):
    def test_hosts(self):
        """ Datatable - hosts table """
        print('test hosts table')

        print('get page /hosts/table')
        response = self.app.get('/hosts/table')
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table ">',
            "$('#tbl_host').DataTable( {",
            '<table id="tbl_host" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="ls_state" data-type="string"',
            '<th data-name="overall_state" data-type="string"',
            '<th data-name="tags" data-type="list"',
            '<th data-name="address" data-type="string"',
            '<th data-name="business_impact" data-type="integer"',
            '<th data-name="ls_last_check" data-type="datetime"',
            '<th data-name="ls_state_type" data-type="string"',
            '<th data-name="ls_state_id" data-type="integer"',
            '<th data-name="ls_acknowledged" data-type="boolean"',
            '<th data-name="ls_downtimed" data-type="boolean"',
            '<th data-name="ls_output" data-type="string"',
            '<th data-name="ls_long_output" data-type="string"',
            '<th data-name="ls_perf_data" data-type="string"',
            '<th data-name="ls_current_attempt" data-type="integer"',
            '<th data-name="ls_max_attempts" data-type="integer"',
            '<th data-name="ls_next_check" data-type="integer"',
            '<th data-name="ls_last_state_changed" data-type="datetime"',
            '<th data-name="ls_last_state" data-type="string"',
            '<th data-name="ls_last_state_type" data-type="string"',
            '<th data-name="ls_latency" data-type="float"',
            '<th data-name="ls_execution_time" data-type="float"'
        )

        response = self.app.post('/hosts/table_data')
        response_value = response.json

        # Temporary
        items_count = response.json['recordsTotal']
        print("Items count: %s" % items_count)
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x] is not None
                assert response.json['data'][x]['name'] is not None


class TestDatatableHostgroups(TestDatatableBase):
    def test_hosts_groups(self):
        """ Datatable - hosts groups table """
        print('test hostgroup table')

        global items_count

        print('get page /hostgroups/table')
        response = self.app.get('/hostgroups/table')
        response.mustcontain(
            '<div id="hostgroups_table" class="alignak_webui_table ">',
            "$('#tbl_hostgroup').DataTable( {",
            '<table id="tbl_hostgroup" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="definition_order" data-type="integer"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="_level" data-type="integer"',
            '<th data-name="_parent" data-type="objectid"',
            '<th data-name="hostgroups" data-type="list"'
        )

        response = self.app.post('/hostgroups/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print(response.json['data'][x])
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['alias'] is not None
                # assert 'hosts' in response.json['data'][x]
                assert '_level' in response.json['data'][x] is not None
                assert '_parent' in response.json['data'][x] is not None
                assert 'hostgroups' in response.json['data'][x] is not None


class TestDatatableHostdependencies(TestDatatableBase):
    def test_hosts_dependencies(self):
        """ Datatable - hosts dependencies table """
        print('test hostdependency table')

        global items_count

        print('get page /hostdependencys/table')
        response = self.app.get('/hostdependencys/table')
        response.mustcontain(
            '<div id="hostdependencys_table" class="alignak_webui_table ">',
            "$('#tbl_hostdependency').DataTable( {",
            '<table id="tbl_hostdependency" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="hosts" data-type="list"',
            '<th data-name="hostgroups" data-type="list"',
            '<th data-name="dependent_hosts" data-type="list"',
            '<th data-name="dependent_hostgroups" data-type="list"',
            '<th data-name="inherits_parent" data-type="boolean"',
            '<th data-name="dependency_period" data-type="objectid"',
            '<th data-name="execution_failure_criteria" data-type="list"',
            '<th data-name="notification_failure_criteria" data-type="list"'
        )

        response = self.app.post('/hostdependencys/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['alias'] is not None


class TestDatatableServices(TestDatatableBase):
    def test_services(self):
        """ Datatable - services table """
        print('test services table')

        global items_count

        print('get page /services/table')
        response = self.app.get('/services/table')
        response.mustcontain(
            '<div id="services_table" class="alignak_webui_table ">',
            "$('#tbl_service').DataTable( {",
            '<table id="tbl_service" ',
            '<th data-name="host" data-type="objectid"',
            '<th data-name="name" data-type="string"',
            '<th data-name="ls_state" data-type="string"',
            '<th data-name="overall_state" data-type="string"',
            '<th data-name="ls_last_check" data-type="datetime"',
            '<th data-name="ls_state_type" data-type="string"',
            '<th data-name="ls_state_id" data-type="integer"',
            '<th data-name="ls_acknowledged" data-type="boolean"',
            '<th data-name="ls_downtimed" data-type="boolean"',
            '<th data-name="ls_output" data-type="string"',
            '<th data-name="ls_long_output" data-type="string"',
            '<th data-name="ls_perf_data" data-type="string"',
            '<th data-name="ls_current_attempt" data-type="integer"',
            '<th data-name="ls_max_attempts" data-type="integer"',
            '<th data-name="ls_next_check" data-type="integer"',
            '<th data-name="ls_last_state_changed" data-type="datetime"',
            '<th data-name="ls_last_state" data-type="string"',
            '<th data-name="ls_last_state_type" data-type="string"',
            '<th data-name="ls_latency" data-type="float"',
            '<th data-name="ls_execution_time" data-type="float"',
        )

        response = self.app.post('/services/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x] is not None
                assert response.json['data'][x]['name'] is not None


class TestDatatableServicegroups(TestDatatableBase):
    def test_services_groups(self):
        """ Datatable - services groups table """
        print('test servicegroup table')

        global items_count

        print('get page /servicegroups/table')
        response = self.app.get('/servicegroups/table')
        response.mustcontain(
            '<div id="servicegroups_table" class="alignak_webui_table ">',
            "$('#tbl_servicegroup').DataTable( {",
            '<table id="tbl_servicegroup" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="definition_order" data-type="integer"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="_level" data-type="integer"',
            '<th data-name="_parent" data-type="objectid"',
            '<th data-name="services" data-type="list"',
            '<th data-name="servicegroups" data-type="list"'
        )

        response = self.app.post('/servicegroups/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print(response.json['data'][x])
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['alias'] is not None
                assert '_level' in response.json['data'][x] is not None
                assert '_parent' in response.json['data'][x] is not None
                assert 'servicegroups' in response.json['data'][x] is not None


class TestDatatableServicedependencies(TestDatatableBase):
    def test_services_dependencies(self):
        """ Datatable - services dependencies table """
        print('test servicedependency table')

        global items_count

        print('get page /servicedependencys/table')
        response = self.app.get('/servicedependencys/table')
        response.mustcontain(
            '<div id="servicedependencys_table" class="alignak_webui_table ">',
            "$('#tbl_servicedependency').DataTable( {",
            '<table id="tbl_servicedependency" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="_realm" data-type="objectid"',
            '<th data-name="definition_order" data-type="integer"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="notes" data-type="string"',
            '<th data-name="hosts" data-type="list"',
            '<th data-name="hostgroups" data-type="list"',
            '<th data-name="dependent_hosts" data-type="list"',
            '<th data-name="dependent_hostgroups" data-type="list"',
            '<th data-name="services" data-type="list"',
            '<th data-name="dependent_services" data-type="list"',
            '<th data-name="inherits_parent" data-type="boolean"',
            '<th data-name="dependency_period" data-type="objectid"',
            '<th data-name="execution_failure_criteria" data-type="list"',
            '<th data-name="notification_failure_criteria" data-type="list"'
        )

        response = self.app.post('/servicedependencys/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['alias'] is not None


class TestDatatableUsers(TestDatatableBase):
    def test_users(self):
        """ Datatable - users table """
        print('test users table')

        global items_count

        print('get page /users/table')
        response = self.app.get('/users/table')
        response.mustcontain(
            '<div id="users_table" class="alignak_webui_table ">',
            "$('#tbl_user').DataTable( {",
            '<table id="tbl_user" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="is_admin" data-type="boolean"',
            '<th data-name="can_submit_commands" data-type="boolean"',
            '<th data-name="role" data-type="string"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="email" data-type="string"',
            '<th data-name="min_business_impact" data-type="integer"',
            '<th data-name="host_notifications_enabled" data-type="boolean"',
            '<th data-name="service_notifications_enabled" data-type="boolean"',
        )

        response = self.app.post('/users/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x]
                assert response.json['data'][x]['name']


class TestDatatableUsergroups(TestDatatableBase):
    def test_usergroups(self):
        """ Datatable - users groups table """
        print('test usergroup table')

        global items_count

        print('get page /usergroups/table')
        response = self.app.get('/usergroups/table')
        response.mustcontain(
            '<div id="usergroups_table" class="alignak_webui_table ">',
            "$('#tbl_usergroup').DataTable( {",
            '<table id="tbl_usergroup" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="definition_order" data-type="integer"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="_level" data-type="integer"',
            '<th data-name="_parent" data-type="objectid"',
            '<th data-name="users" data-type="list"',
            '<th data-name="usergroups" data-type="list"'
        )

        response = self.app.post('/usergroups/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print(response.json['data'][x])
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['alias'] is not None
                assert '_level' in response.json['data'][x] is not None
                assert '_parent' in response.json['data'][x] is not None
                assert 'usergroups' in response.json['data'][x] is not None


class TestDatatableTimeperiods(TestDatatableBase):
    def test_timeperiod(self):
        """ Datatable - timeperiods table """
        print('test timeperiod table')

        global items_count

        print('get page /timeperiods/table')
        response = self.app.get('/timeperiods/table')
        response.mustcontain(
            '<div id="timeperiods_table" class="alignak_webui_table ">',
            "$('#tbl_timeperiod').DataTable( {",
            '<table id="tbl_timeperiod" ',
            '<th data-name="name" data-type="string"',
            '<th data-name="definition_order" data-type="integer"',
            '<th data-name="alias" data-type="string"',
            '<th data-name="is_active" data-type="boolean"',
            '<th data-name="dateranges" data-type="list"',
            '<th data-name="exclude" data-type="list"'
        )

        response = self.app.post('/timeperiods/table_data')
        response_value = response.json
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print(response.json['data'][x])
                assert response.json['data'][x]
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['alias'] is not None
                assert response.json['data'][x]['is_active'] is not None


class TestDatatableUserRestrictRoles(TestDatatableBase):
    def test_userrestrictrole(self):
        """ Datatable - users restrictions table """
        print('test userrestrictrole table')

        global items_count

        print('get page /userrestrictroles/table')
        response = self.app.get('/userrestrictroles/table')
        response.mustcontain(
            '<div id="userrestrictroles_table" class="alignak_webui_table ">',
            "$('#tbl_userrestrictrole').DataTable( {",
            '<table id="tbl_userrestrictrole" ',
            '<th data-name="user" data-type="objectid"',
            '<th data-name="realm" data-type="objectid"',
            '<th data-name="subrealm" data-type="boolean"',
            '<th data-name="resource" data-type="string"',
            '<th data-name="crud" data-type="list"'
        )

        response = self.app.post('/userrestrictroles/table_data')
        print(response)
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count + 0):
            # Only if lower than default pagination ...
            if x < BACKEND_PAGINATION_DEFAULT:
                print(response.json['data'][x])
                assert response.json['data'][x]
                assert response.json['data'][x]['user'] is not None
                assert response.json['data'][x]['realm'] is not None
                # assert response.json['data'][x]['sub_realm'] is not None
                assert response.json['data'][x]['resource'] is not None
                assert response.json['data'][x]['crud'] is not None


class TestDatatableLogs(TestDatatableBase):
    def test_logcheckresult(self):
        """ Datatable - logs table """
        print('test logcheckresult table')

        global items_count

        print('get page /logcheckresults/table')
        response = self.app.get('/logcheckresults/table')
        response.mustcontain(
            '<div id="logcheckresults_table" class="alignak_webui_table ">',
            "$('#tbl_logcheckresult').DataTable( {",
            '<table id="tbl_logcheckresult" ',
            '<th data-name="last_check" data-type="datetime"',
            '<th data-name="host" data-type="objectid"',
            '<th data-name="service_name" data-type="string"',
            '<th data-name="state" data-type="string"',
            '<th data-name="state_type" data-type="string"',
            '<th data-name="state_id" data-type="integer"',
            '<th data-name="passive_check" data-type="boolean"',
            '<th data-name="acknowledged" data-type="boolean"',
            '<th data-name="acknowledgement_type" data-type="integer"',
            '<th data-name="downtimed" data-type="boolean"',
            '<th data-name="state_changed" data-type="boolean"',
            '<th data-name="last_state" data-type="string"',
            '<th data-name="last_state_type" data-type="string"',
            '<th data-name="last_state_id" data-type="integer"',
            '<th data-name="last_state_changed" data-type="datetime"',
            '<th data-name="output" data-type="string"',
            '<th data-name="long_output" data-type="string"',
            '<th data-name="perf_data" data-type="string"',
            '<th data-name="latency" data-type="float"',
            '<th data-name="execution_time" data-type="float"',
        )

        response = self.app.post('/logcheckresults/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']

        # No data in the test backend


class TestDatatableHistorys(TestDatatableBase):
    def test_history(self):
        """ Datatable - history table """
        print('test history table')

        global items_count

        print('get page /historys/table')
        response = self.app.get('/historys/table')
        response.mustcontain(
            '<div id="historys_table" class="alignak_webui_table ">',
            "$('#tbl_history').DataTable( {",
            '<table id="tbl_history" ',
            '<th data-name="_created" data-type="integer"',
            '<th data-name="host" data-type="objectid"',
            '<th data-name="service" data-type="objectid"',
            '<th data-name="user" data-type="objectid"',
            '<th data-name="type" data-type="string"',
            '<th data-name="message" data-type="string"',
            '<th data-name="logcheckresult" data-type="objectid"'
        )

        response = self.app.post('/historys/table_data')
        print(response)
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']

        # No data in the test backend
