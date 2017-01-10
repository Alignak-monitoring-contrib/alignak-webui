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
import unittest2
import requests

from mock import Mock, patch

from webtest import TestApp
from alignak_webui import webapp

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = \
    os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file: %s" % os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
# To load application configuration used by the objects
import alignak_webui.app

from alignak_webui.backend.alignak_ws_client import AlignakConnection, AlignakWSException
from alignak_webui.objects.item_daemon import Daemon
from alignak_webui.objects.datamanager import DataManager


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

    return MockResponse({}, 404)


class TestAlignakWS(unittest2.TestCase):

    # We patch 'requests.get' with our own method.
    # The mock object is passed in to our test case method.
    @patch('alignak_webui.backend.alignak_ws_client.requests.get', side_effect=mocked_requests_get)
    def test_get_alignak_state(self, mock_get):
        """ Get Alignak WS state

        :return:
        """
        self.dmg = DataManager(alignak_endpoint='http://127.0.0.1:8888')
        print('Data manager: %s' % self.dmg)
        assert self.dmg.alignak_daemons == []

        # Get alignak WS state
        self.dmg.get_alignak_state()

        print('Data manager daemons: %s' % self.dmg.alignak_daemons)
        assert self.dmg.alignak_daemons != []
        assert len(self.dmg.alignak_daemons) == 4
        for daemon in self.dmg.alignak_daemons:
            assert isinstance(daemon, Daemon)
            assert daemon.status == 'UP'
