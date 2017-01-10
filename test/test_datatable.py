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

import json
import os
import shlex
import subprocess
import time
from logging import getLogger, INFO, WARNING, ERROR

import unittest2
from webtest import TestApp

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                            'settings.cfg')
print("Configuration file: %s" % os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
# To load application configuration used by the objects
import alignak_webui.app

from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

from alignak_webui import webapp
from alignak_webui.objects.backend import BackendConnection
from alignak_webui.objects.item_command import Command
from alignak_webui.objects.datamanager import DataManager

# loggerDm = getLogger('alignak_webui.application')
# loggerDm.setLevel(WARNING)
# loggerDm = getLogger('alignak_webui.utils.datatable')
# loggerDm.setLevel(INFO)
# loggerDm = getLogger('alignak_webui.objects.datamanager')
# loggerDm.setLevel(WARNING)
# loggerDm = getLogger('alignak_webui.objects.item')
# loggerDm.setLevel(ERROR)
# loggerDm = getLogger('alignak_webui.objects.backend')
# loggerDm.setLevel(WARNING)

pid = None
backend_address = "http://127.0.0.1:5000/"

items_count = 0


def setup_module():
    print("")
    print("start alignak backend")

    global pid
    global backend_address

    if backend_address == "http://127.0.0.1:5000/":
        # Set test mode for applications backend
        os.environ['TEST_ALIGNAK_BACKEND'] = '1'
        os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-backend-test'

        # Delete used mongo DBs
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        print("Starting Alignak backend...")
        # No console output for the applications backend ...
        fnull = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('uwsgi --plugin python -w alignakbackend:app --socket 0.0.0.0:5000 '
                        '--protocol=http --enable-threads --pidfile /tmp/uwsgi.pid '
                        '--logto /tmp/uwsgi.log'), stdout=fnull
        )
        time.sleep(1)

        print("Feeding backend...")
        q = subprocess.Popen(
            shlex.split('alignak-backend-import --delete cfg/default/_main.cfg'), stdout=fnull
        )
        (stdoutdata, stderrdata) = q.communicate()  # now wait
        assert exit_code == 0


def teardown_module(module):
    subprocess.call(['uwsgi', '--stop', '/tmp/uwsgi.pid'])
    time.sleep(2)


class TestDataTable(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

        # Test application
        self.app = TestApp(webapp)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

        self.items_count = 0

    def test_01_get(self):
        """ Datatable - get table """
        print('test get table')

        print('get page /commands/table')
        response = self.app.get('/commands/table')
        response.mustcontain(
            '<div id="commands_table" class="alignak_webui_table ">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" ',
            '<th data-name="name" data-type="string">Command name</th>',
            '<th data-name="_realm" data-type="objectid">Realm</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Command alias</th>',
            '<th data-name="notes" data-type="string">Notes</th>',
            '<th data-name="command_line" data-type="string">Command line</th>',
            '<th data-name="enable_environment_macros" data-type="boolean">Enable environment macros</th>',
            '<th data-name="poller_tag" data-type="string">Poller tag</th>',
            '<th data-name="reactionner_tag" data-type="string">Reactionner tag</th>',
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
                print(response.json['data'][x])
                assert response.json['data'][x] is not None
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['enable_environment_macros'] is not None
                assert response.json['data'][x]['command_line'] is not None
                assert response.json['data'][x]['timeout'] is not None
                assert response.json['data'][x]['poller_tag'] is not None
                assert response.json['data'][x]['reactionner_tag'] is not None
                assert response.json['data'][x]['enable_environment_macros'] is not None

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
        assert response.json['recordsFiltered'] == 5
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
        assert response.json['recordsFiltered'] == 5
        assert response.json['data']
        assert len(response.json['data']) == 5


class TestDatatableCommands(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(webapp)

        response = self.app.post('/login', {'username': 'admin', 'password': 'admin'})
        # Redirected twice: /login -> / -> /dashboard !
        redirected_response = response.follow()
        redirected_response = redirected_response.follow()

    def test_01_commands(self):
        """ Datatable - commands table """
        print('test commands table')

        global items_count

        print('get page /commands/table')
        response = self.app.get('/commands')
        # print(response)
        response = self.app.get('/commands/table')
        # print(response)
        response.mustcontain(
            '<div id="commands_table" class="alignak_webui_table ">',
            "$('#tbl_command').DataTable( {",
            '<table id="tbl_command" ',
            '<th data-name="name" data-type="string">Command name</th>',
            '<th data-name="_realm" data-type="objectid">Realm</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Command alias</th>',
            '<th data-name="notes" data-type="string">Notes</th>',
            '<th data-name="command_line" data-type="string">Command line</th>',
            '<th data-name="enable_environment_macros" data-type="boolean">Enable environment macros</th>',
            '<th data-name="poller_tag" data-type="string">Poller tag</th>',
            '<th data-name="reactionner_tag" data-type="string">Reactionner tag</th>',
        )

        print('change content with /commands/table_data')
        response = self.app.post('/commands/table_data')
        response_value = response.json
        # Temporary ...
        items_count = response.json['recordsTotal']
        # assert response.json['recordsTotal'] == items_count
        # assert response.json['recordsFiltered'] == items_count
        # if items_count < BACKEND_PAGINATION_DEFAULT else BACKEND_PAGINATION_DEFAULT
        assert response.json['data']
        for x in range(0, items_count):
            if x < BACKEND_PAGINATION_DEFAULT:
                assert response.json['data'][x] is not None
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['definition_order'] is not None
                assert response.json['data'][x]['enable_environment_macros'] is not None
                assert response.json['data'][x]['command_line'] is not None
                assert response.json['data'][x]['timeout'] is not None
                assert response.json['data'][x]['poller_tag'] is not None
                assert response.json['data'][x]['reactionner_tag'] is not None
                assert response.json['data'][x]['enable_environment_macros'] is not None


class TestDatatableRealms(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_01_realms(self):
        """ Datatable - realms table """
        print('test realm table')

        global items_count

        print('get page /realms/table')
        response = self.app.get('/realms/table')
        response.mustcontain(
            '<div id="realms_table" class="alignak_webui_table ">',
            "$('#tbl_realm').DataTable( {",
            '<table id="tbl_realm" ',
            '<th data-name="name" data-type="string">Realm name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Realm alias</th>',
            '<th data-name="default" data-type="boolean">Default realm</th>',
            '<th data-name="_level" data-type="integer">Level</th>',
            '<th data-name="_parent" data-type="objectid">Parent</th>',
            '<th data-name="hosts_critical_threshold" data-type="integer">Hosts critical threshold</th>',
            '<th data-name="hosts_warning_threshold" data-type="integer">Hosts warning threshold</th>',
            '<th data-name="services_critical_threshold" data-type="integer">Services critical threshold</th>',
            '<th data-name="services_warning_threshold" data-type="integer">Services warning threshold</th>',
            '<th data-name="global_critical_threshold" data-type="integer">Global critical threshold</th>',
            '<th data-name="global_warning_threshold" data-type="integer">Global warning threshold</th>'
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


class TestDatatableHosts(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_02_hosts(self):
        """ Datatable - hosts table """
        print('test hosts table')

        global items_count

        print('get page /hosts/table')
        response = self.app.get('/hosts/table')
        response.mustcontain(
            '<div id="hosts_table" class="alignak_webui_table ">',
            "$('#tbl_host').DataTable( {",
            '<table id="tbl_host" ',
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
            '<th data-name="business_impact" data-type="integer">Business impact</th>'
        )

        response = self.app.post('/hosts/table_data')
        response_value = response.json
        print(response_value)
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


class TestDatatableHostgroups(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_01_hosts_groups(self):
        """ Datatable - hosts groups table """
        print('test hostgroup table')

        global items_count

        print('get page /hostgroups/table')
        response = self.app.get('/hostgroups/table')
        response.mustcontain(
            '<div id="hostgroups_table" class="alignak_webui_table ">',
            "$('#tbl_hostgroup').DataTable( {",
            '<table id="tbl_hostgroup" ',
            '<th data-name="name" data-type="string">Hosts group name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Hosts group alias</th>',
            '<th data-name="_level" data-type="integer">Level</th>',
            '<th data-name="_parent" data-type="objectid">Parent</th>',
            '<th data-name="hostgroups" data-type="list">Hosts groups</th>'
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


class TestDatatableServices(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_02_services(self):
        """ Datatable - services table """
        print('test services table')

        global items_count

        print('get page /services/table')
        response = self.app.get('/services/table')
        response.mustcontain(
            '<div id="services_table" class="alignak_webui_table ">',
            "$('#tbl_service').DataTable( {",
            '<table id="tbl_service" ',
            '<th data-name="name" data-type="string">Service name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Service alias</th>',
            '<th data-name="display_name" data-type="string">Service display name</th>',
            '<th data-name="host" data-type="objectid">Host</th>',
            '<th data-name="check_command" data-type="objectid">Check command</th>',
            '<th data-name="check_command_args" data-type="string">Check command arguments</th>',
            '<th data-name="check_period" data-type="objectid">Check period</th>',
            '<th data-name="check_interval" data-type="integer">Check interval</th>',
            '<th data-name="retry_interval" data-type="integer">Retry interval</th>',
            '<th data-name="max_check_attempts" data-type="integer">Maximum check attempts</th>',
            '<th data-name="active_checks_enabled" data-type="boolean">Active checks enabled</th>',
            '<th data-name="passive_checks_enabled" data-type="boolean">Passive checks enabled</th>',
            '<th data-name="business_impact" data-type="integer">Business impact</th>',
            '<th data-name="users" data-type="list">Users</th>',
            '<th data-name="usergroups" data-type="list">Users groups</th>',
            '<th data-name="notifications_enabled" data-type="boolean">Notifications enabled</th>',
            '<th data-name="notification_period" data-type="objectid">Notification period</th>',
            '<th data-name="notification_interval" data-type="integer">Notification interval</th>',
            '<th data-name="first_notification_delay" data-type="integer">First notification delay</th>',
            '<th data-name="notification_options" data-type="list">Notification options</th>',
            '<th data-name="stalking_options" data-type="list">Stalking options</th>',
            '<th data-name="check_freshness" data-type="boolean">Freshness check enabled</th>',
            '<th data-name="freshness_threshold" data-type="integer">Freshness threshold</th>',
            '<th data-name="flap_detection_enabled" data-type="boolean">Flapping detection enabled</th>',
            '<th data-name="flap_detection_options" data-type="list">Flapping detection options</th>',
            '<th data-name="low_flap_threshold" data-type="integer">Low flapping threshold</th>',
            '<th data-name="high_flap_threshold" data-type="integer">High flapping threshold</th>',
            '<th data-name="event_handler_enabled" data-type="boolean">Event handler enabled</th>',
            '<th data-name="event_handler" data-type="objectid">Event handler command</th>',
            '<th data-name="process_perf_data" data-type="boolean">Process performance data</th>'
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


class TestDatatableServicegroups(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_01_services_groups(self):
        """ Datatable - services groups table """
        print('test servicegroup table')

        global items_count

        print('get page /servicegroups/table')
        response = self.app.get('/servicegroups/table')
        response.mustcontain(
            '<div id="servicegroups_table" class="alignak_webui_table ">',
            "$('#tbl_servicegroup').DataTable( {",
            '<table id="tbl_servicegroup" ',
            '<th data-name="name" data-type="string">Services group name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Services group alias</th>',
            '<th data-name="_level" data-type="integer">Level</th>',
            '<th data-name="_parent" data-type="objectid">Parent</th>',
            '<th data-name="services" data-type="list">Services</th>',
            '<th data-name="servicegroups" data-type="list">Services groups</th>'
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


class TestDatatableUsers(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_03_users(self):
        """ Datatable - users table """
        print('test users table')

        global items_count

        print('get page /users/table')
        response = self.app.get('/users/table')
        response.mustcontain(
            '<div id="users_table" class="alignak_webui_table ">',
            "$('#tbl_user').DataTable( {",
            '<table id="tbl_user" ',
            '<th data-name="name" data-type="string">User name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">User alias</th>',
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


class TestDatatableUsergroups(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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
            '<th data-name="name" data-type="string">Users group name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Users group alias</th>',
            '<th data-name="_level" data-type="integer">Level</th>',
            '<th data-name="_parent" data-type="objectid">Parent</th>',
            '<th data-name="users" data-type="list">Users</th>',
            '<th data-name="usergroups" data-type="list">Users groups</th>'
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


class TestDatatableTimeperiod(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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
            '<th data-name="name" data-type="string">Timeperiod name</th>',
            '<th data-name="definition_order" data-type="integer">Definition order</th>',
            '<th data-name="alias" data-type="string">Timeperiod alias</th>',
            '<th data-name="is_active" data-type="boolean">Currently active</th>',
            '<th data-name="dateranges" data-type="list">Date ranges</th>',
            '<th data-name="exclude" data-type="list">Exclusions</th>'
        )

        response = self.app.post('/timeperiods/table_data')
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
                assert response.json['data'][x]['name'] is not None
                assert response.json['data'][x]['alias'] is not None
                assert response.json['data'][x]['is_active'] is not None


class TestDatatableUserRestrictRole(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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
            '<th data-name="user" data-type="objectid">User</th>',
            '<th data-name="realm" data-type="objectid">Realm</th>',
            '<th data-name="subrealm" data-type="boolean">Sub realms</th>',
            '<th data-name="resource" data-type="string">Resource</th>',
            '<th data-name="crud" data-type="list">CRUD</th>'
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


class TestDatatableLog(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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

    def test_05_logcheckresult(self):
        """ Datatable - logs table """
        print('test logcheckresult table')

        global items_count

        print('get page /logcheckresults/table')
        response = self.app.get('/logcheckresults/table')
        response.mustcontain(
            '<div id="logcheckresults_table" class="alignak_webui_table ">',
            "$('#tbl_logcheckresult').DataTable( {",
            '<table id="tbl_logcheckresult" ',
            """<tr>
            <th data-name="last_check" data-type="datetime">Last check</th>
            <th data-name="host" data-type="objectid">Host</th>
            <th data-name="service" data-type="objectid">Service</th>
            <th data-name="state" data-type="string">State</th>
            <th data-name="state_type" data-type="string">State type</th>
            <th data-name="state_id" data-type="integer">State id</th>
            <th data-name="latency" data-type="float">False</th>
            <th data-name="execution_time" data-type="float">Execution time</th>
            <th data-name="state_changed" data-type="boolean">State changed</th>
            <th data-name="acknowledged" data-type="boolean">Acknowledged</th>
            <th data-name="last_state" data-type="string">Last state</th>
            <th data-name="last_state_type" data-type="string">Last state type</th>
            <th data-name="last_state_id" data-type="integer">Last state id</th>
            <th data-name="output" data-type="string">Output</th>
            <th data-name="long_output" data-type="string">Long output</th>
            <th data-name="perf_data" data-type="string">Performance data</th>
         </tr>""",

        )

        response = self.app.post('/logcheckresults/table_data')
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']

        # No data in the test backend


class TestDatatableHistory(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

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
            '<th data-name="_created" data-type="integer">Date</th>',
            '<th data-name="host" data-type="objectid">Host</th>',
            '<th data-name="service" data-type="objectid">Service</th>',
            '<th data-name="user" data-type="objectid">User</th>',
            '<th data-name="type" data-type="string">Type</th>',
            '<th data-name="message" data-type="string">Message</th>',
            '<th data-name="check_result" data-type="objectid">Check result</th>'
        )

        response = self.app.post('/historys/table_data')
        print(response)
        response_value = response.json
        print(response_value)
        # Temporary
        items_count = response.json['recordsTotal']

        # No data in the test backend
