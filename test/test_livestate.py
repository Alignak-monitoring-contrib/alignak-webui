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
import shlex
import subprocess
import time

import unittest2
from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                                            'settings.cfg')
print("Configuration file: %s" % os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
# To load application configuration used by the objects
import alignak_webui.app

from alignak_webui.objects.element import BackendElement
from alignak_webui.objects.item_user import User
from alignak_webui.objects.item_command import Command
from alignak_webui.objects.item_host import Host
from alignak_webui.objects.item_service import Service
from alignak_webui.objects.item_livestate import LiveState
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_hostgroup import HostGroup
from alignak_webui.objects.item_servicegroup import ServiceGroup
from alignak_webui.objects.datamanager import DataManager

from logging import getLogger, DEBUG, INFO, WARNING

loggerDm = getLogger('alignak_webui.objects.datamanager')
loggerDm.setLevel(INFO)
loggerobjs = getLogger('alignak_webui.objects.element')
loggerobjs.setLevel(INFO)
# loggerBackend = getLogger('alignak_webui.objects.backend')
# loggerBackend.setLevel(WARNING)

pid = None
backend_address = "http://127.0.0.1:5000/"
datamgr = None


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
        print("Dropping database...")
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

        print("Starting Alignak backend...")
        pid = subprocess.Popen(
            shlex.split('alignak_backend')
        )
        print("PID: %s" % pid)
        time.sleep(1)

        print("Feeding backend...")
        exit_code = subprocess.call(
            shlex.split('alignak_backend_import --delete cfg/default/_main.cfg')
        )
        assert exit_code == 0


def teardown_module():
    print("")
    print("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class TestLiveState(unittest2.TestCase):
    def setUp(self):
        print("")
        print("setting up ...")
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

        # Initialize and do not load
        assert self.dmg.user_login('admin', 'admin', load=False)

    def tearDown(self):
        print("")
        print("tearing down ...")
        # Logout
        self.dmg.reset(logout=True)

    def test_get(self):
        print("")
        print('test get livestate')

        count = 5


        # Get livestate
        print('Get livestate - 1')
        search = {
            'page': 1,
            'max_results': count
        }
        objs = self.dmg.get_livestates(search=search)
        self.assertEqual(len(objs), count)  # Backend pagination limit ...
        for obj in objs:
            print("Got: ", obj)
            assert obj.id
            self.assertIsInstance(obj.host, Host) # Must be an object
            self.assertIsInstance(obj.host.check_command, Command)
            self.assertIsInstance(obj.host.check_period, TimePeriod)
            if obj.type == 'service':
                self.assertIsInstance(obj.service, Service) # Must be an object
                self.assertIsInstance(obj.service.check_command, Command)
                self.assertIsInstance(obj.service.check_period, TimePeriod)
            else:
                self.assertEqual(obj.service, "service") # No linked object
            livestate = self.dmg.get_livestate({'where': {'_id': obj.id}})
            livestate = livestate[0]
            print("Got: %s" % livestate)

        # Get livestate (bis)
        print('Get livestate - 2')
        search = {
            'page': 1,
            'max_results': count
        }
        objs = self.dmg.get_livestates(search=search)
        self.assertEqual(len(objs), count)  # Backend pagination limit ...
        lv = LiveState()
        for obj in objs:
            print("Got: ", obj)
            lv = LiveState(obj) # An object from another object
            print("Got: %s" % lv)

        # Get livestate (ter)
        print('Get livestate - 3')
        search = {
            'page': 1,
            'max_results': count
        }
        result = self.dmg.backend.get('livestate', search, all_elements=False)
        for item in result:
            # Create a new object
            lv = LiveState(item)
            print("Got: %s" % lv)
