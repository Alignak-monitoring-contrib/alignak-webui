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
os.environ['ALIGNAK_WEBUI_TEST_WS'] = '1'
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
    os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'] = 'alignak-webui-tests'

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

    print("Mocked request: %s" % args[0])
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
                    'reachable': False,
                    'max_check_attempts': 3,
                    'last_check': 1478064129.016136,
                    'port': 7768
                },
                'scheduler-south': {
                    'passive': False,
                    'realm_name': "All",
                    'polling_interval': 1,
                    'alive': False,
                    'manage_arbiters': False,
                    'manage_sub_realms': False,
                    'is_sent': False,
                    'spare': False,
                    'check_interval': 60,
                    'address': "127.0.0.1",
                    'reachable': False,
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
    elif args[0].startswith('http://127.0.0.1:5000/livesynthesis'):
        # This function must also be mocked-up ... do not know clearly why :(
        data = {
            '_id': 1,
            '_realm': u'1',

            'services_total': 89,
            'services_business_impact': 0,
            'services_ok_hard': 8,
            'services_ok_soft': 0,
            'services_warning_hard': 0,
            'services_warning_soft': 0,
            'services_critical_hard': 83,
            'services_critical_soft': 23,
            'services_unknown_hard': 24,
            'services_unknown_soft': 0,
            'services_unreachable_hard': 4,
            'services_unreachable_soft': 1,
            'services_acknowledged': 0,
            'services_flapping': 0,
            'services_in_downtime': 0,

            'hosts_total': 13,
            'hosts_business_impact': 0,
            'hosts_up_hard': 3,
            'hosts_up_soft': 0,
            'hosts_down_hard': 14,
            'hosts_down_soft': -4,
            'hosts_unreachable_hard': 0,
            'hosts_unreachable_soft': 0,
            'hosts_acknowledged': 0,
            'hosts_flapping': 0,
            'hosts_in_downtime': 0,

        }
        return MockResponse(data, 200)


class TestAlignakWS(unittest2.TestCase):
    def setUp(self):
        # Test application
        self.app = TestApp(alignak_webui.app.session_app)

        self.app.post('/login', {'username': 'admin', 'password': 'admin'})

    def tearDown(self):
        self.app.get('/logout')

    # @unittest2.skip("Too many requests.get to be patched :/")
    @patch('alignak_webui.backend.alignak_ws_client.requests.get', side_effect=mocked_requests_get)
    def test_daemons(self, mock_login):
        """ Web - daemons """
        print('get page /alignak_map')
        response = self.app.get('/alignak_map')
        print(response)
        response.mustcontain(
            '<div id="alignak_daemons"',
            '<tr id="#daemon-alignakdaemon_1">',
            '<tr id="#daemon-alignakdaemon_2">',
            '<tr id="#daemon-alignakdaemon_3">',
            '<tr id="#daemon-alignakdaemon_4">',
        )


if __name__ == '__main__':
    unittest.main()
