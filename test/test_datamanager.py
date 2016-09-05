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
from alignak_webui.objects.item_usergroup import UserGroup
from alignak_webui.objects.item_command import Command
from alignak_webui.objects.item_host import Host
from alignak_webui.objects.item_service import Service
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_hostgroup import HostGroup
from alignak_webui.objects.item_servicegroup import ServiceGroup
from alignak_webui.objects.datamanager import DataManager

from logging import getLogger, DEBUG, INFO, WARNING

loggerDm = getLogger('alignak_webui.objects.datamanager')
loggerDm.setLevel(INFO)
loggerItems = getLogger('alignak_webui.objects.element')
loggerItems.setLevel(INFO)
loggerBackend = getLogger('alignak_webui.objects.backend')
loggerBackend.setLevel(DEBUG)

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
        exit_code = subprocess.call(
            shlex.split(
                'mongo %s --eval "db.dropDatabase()"' % os.environ['ALIGNAK_BACKEND_MONGO_DBNAME'])
        )
        assert exit_code == 0

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


def teardown_module():
    print("")
    print("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class Test1FindAndSearch(unittest2.TestCase):
    @unittest2.skip("This test has no more reason to exist ...")
    def test_1_1_find_objects(self):
        print('test find_objects - no objects in cache')

        # Create new datamanager - do not use default backend address
        datamanager = DataManager(backend_endpoint=backend_address)
        self.assertIsNotNone(datamanager.backend)
        self.assertFalse(datamanager.loaded )
        self.assertIsNone(datamanager.logged_in_user)
        # Got known managed elements classes
        self.assertEqual(len(datamanager.known_classes), 18)

        # Login ...
        assert datamanager.backend.login('admin', 'admin')
        assert datamanager.loaded == False
        assert datamanager.backend.connected
        print('logged in as admin in the backend')
        # Datamanager is not yet aware of the user login !!!
        assert datamanager.logged_in_user is None

        # Get current user in the alignak backend
        parameters = {'where': {"name": "admin"}}
        items = datamanager.backend.get('user', params=parameters)
        assert len(items) == 1
        assert items[0]["_id"]
        admin_id = items[0]["_id"]

        ##### Cannot find any object when no user is logged-in ...
        ##### An error is raised !!!
        users = datamanager.find_object('user', admin_id)
        print("Items: %s" % users)
        assert len(users) == 1
        # New user object created in the DM cache ...
        self.assertEqual(datamanager.get_objects_count('user', refresh=True), 1)

        # Unknown user not found
        with assert_raises(ValueError) as cm:
            datamanager.find_object('user', 'fake_id')
        ex = cm.exception
        print(ex)
        assert str(
            ex) == """user, search: {'max_results': 50, 'where': '{"_id": "%s"}', 'page': 0} was not found in the backend""" % 'fake_id'


class Test2Creation(unittest2.TestCase):
    def test_2_1_creation_load(self):
        print('------------------------------')
        print('test creation')

        datamanager = DataManager()
        assert datamanager.backend
        assert datamanager.loaded == False
        assert datamanager.logged_in_user is None
        print('Data manager', datamanager)
        # Got known managed elements classes
        self.assertEqual(len(datamanager.known_classes), 18)

        # Initialize and load fail ...
        print('DM load failed')
        result = datamanager.load()
        # Refused because no backend logged-in user
        assert not result

        # Login error
        print('DM logging bad password')
        assert not datamanager.user_login('admin', 'fake')
        print(datamanager.connection_message)
        assert datamanager.connection_message == 'Backend connection refused...'
        print(datamanager.logged_in_user)
        assert not datamanager.logged_in_user

        # Create new datamanager - do not use default backend address
        print('DM initialization')
        datamanager = DataManager(backend_endpoint=backend_address)
        assert datamanager.backend
        assert datamanager.loaded == False
        assert datamanager.logged_in_user is None
        print('Data manager', datamanager)

        # Initialize and load fail ...
        print('DM load fail')
        result = datamanager.load()
        # Refused because no backend logged-in user
        assert not result

        # Login error
        print('DM logging bad password')
        assert not datamanager.user_login('admin', 'fake')
        print(datamanager.connection_message)
        assert datamanager.connection_message == 'Backend connection refused...'
        print(datamanager.logged_in_user)
        assert not datamanager.logged_in_user

        # User login but do not load yet
        print('DM login ok')
        assert datamanager.user_login('admin', 'admin', load=False)
        assert datamanager.connection_message == 'Connection successful'
        print("Logged user: %s" % datamanager.logged_in_user)
        assert datamanager.logged_in_user
        assert datamanager.logged_in_user is not None
        assert datamanager.logged_in_user.id is not None
        assert datamanager.logged_in_user.get_username() == 'admin'
        assert datamanager.logged_in_user.authenticated
        user_token = datamanager.logged_in_user.token
        print(User._cache[datamanager.logged_in_user.id].__dict__)

        print('DM reset')
        datamanager.reset()
        # Still logged-in...
        assert datamanager.logged_in_user
        assert datamanager.logged_in_user is not None

        print('DM reset - logout')
        datamanager.reset(logout=True)
        # Logged-out...
        assert not datamanager.logged_in_user
        assert datamanager.logged_in_user is None

        # User login with an authentication token
        print('DM login - token')
        assert datamanager.user_login(user_token)
        # When user authentication is made thanks to a token, DM is not loaded ... it is assumed that load already occured!

        print('DM login')
        assert datamanager.user_login('admin', 'admin', load=False)
        print(datamanager.logged_in_user)
        print(datamanager.logged_in_user.token)
        user_token = datamanager.logged_in_user.token
        assert datamanager.user_login(user_token)
        assert datamanager.connection_message == 'Connection successful'

        assert datamanager.logged_in_user
        assert datamanager.logged_in_user is not None
        assert datamanager.logged_in_user.id is not None
        assert datamanager.logged_in_user.get_username() == 'admin'
        assert datamanager.logged_in_user.authenticated


class Test3LoadCreate(unittest2.TestCase):
    def setUp(self):
        print("")

        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

    def tearDown(self):
        print("")

    def test_3_1_load(self):
        print("")
        print('test load as admin')

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print("Result:", result)
        # self.assertEqual(result, 0)  # No new objects created ...

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print("Result:", result)
        # Must not have loaded any objects ... behavior changed, no more objects loading on login
        # self.assertEqual(result, 0)

    def test_3_3_get_errors(self):
        print("")
        print('test get errors')

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print("Result:", result)
        assert result == 0  # No new objects created ...

        # Get users error
        item = self.dmg.get_user('unknown')
        assert not item
        item = self.dmg.get_realm('unknown')
        assert not item
        item = self.dmg.get_host('unknown')
        assert not item
        item = self.dmg.get_service('unknown')
        assert not item
        item = self.dmg.get_command('unknown')
        assert not item


class Test4NotAdmin(unittest2.TestCase):
    def setUp(self):
        print("")
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

    def tearDown(self):
        print("")

    @unittest2.skip("Skipped because creating a new user do not allow him to get its own data (timeperiod get is 404)!")
    def test_4_1_load(self):
        print("")
        print('test load not admin user')

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print("Result:", result)
        assert result == 0  # No new objects created ...

        # Get main realm
        realm_all = self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        tp_all = self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Create a non admin user ...
        # Create a new user
        print('create a user')
        data = {
            "name": "not_admin",
            "alias": "Testing user - not administrator",
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
            "service_notification_commands": [],
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
        new_user_id = self.dmg.add_user(data)
        print("New user id: %s" % new_user_id)

        # Logout
        # self.dmg.reset(logout=True)
        # assert not self.dmg.backend.connected
        # assert self.dmg.logged_in_user is None
        # assert self.dmg.loaded == False

        # Login as not_admin created user
        assert self.dmg.user_login('admin', 'admin', load=False)
        print("-----")

        assert self.dmg.user_login('not_admin', 'NOPASSWORDSET', load=False)
        assert self.dmg.backend.connected
        assert self.dmg.logged_in_user
        print("Logged-in user: %s" % self.dmg.logged_in_user)
        assert self.dmg.logged_in_user.get_username() == 'not_admin'
        print('logged in as not_admin')

        # Initialize and load ...
        result = self.dmg.load()
        print("Result:", result)
        print("Objects count:", self.dmg.get_objects_count())
        # assert result == 0                          # Only the newly created user, so no new objects loaded
        # assert self.dmg.get_objects_count() == 1    # not_admin user

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print("Result:", result)
        print("Objects count:", self.dmg.get_objects_count())
        # assert result == 3                          # not_admin user + test_service + relation
        # assert self.dmg.get_objects_count() == 3    # not_admin user + test_service + relation


        # Not admin user can see only its own data, ...
        # -------------------------------------------

        # Do not check the length because the backend contains more elements than needed ...
        # dump_backend(not_admin_user=True, test_service=True)

        # Get users
        items = self.dmg.get_users()
        print("Users:", items)
        # assert len(items) == 1
        # 1 user only ...

        # Get commands
        items = self.dmg.get_commands()
        print("Commands:", items)
        # assert len(items) == 1

        # Get realms
        items = self.dmg.get_realms()
        print("Commands:", items)
        # assert len(items) == 1

        # Get timeperiods
        items = self.dmg.get_timeperiods()
        print("Commands:", items)
        # assert len(items) == 1

        # Get hosts
        items = self.dmg.get_hosts()
        print("Hosts:", items)
        # assert len(items) == 1

        # Get services
        items = self.dmg.get_services()
        print("Services:", items)
        # assert len(items) == 1

        result = self.dmg.delete_user(new_user_id)
        # Cannot delete the current logged-in user
        assert not result

        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.logged_in_user is None
        assert self.dmg.loaded == False

        # Login as admin
        assert self.dmg.user_login('admin', 'admin', load=False)
        assert self.dmg.backend.connected
        assert self.dmg.logged_in_user.get_username() == 'admin'

        result = self.dmg.delete_user(new_user_id)
        # Can delete the former logged-in user
        assert result


class Test5Basic(unittest2.TestCase):
    def setUp(self):
        print("")
        self.dmg = DataManager(backend_endpoint=backend_address)
        print('Data manager', self.dmg)

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

    def tearDown(self):
        print("")
        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.logged_in_user is None
        assert self.dmg.loaded == False

    def test_5_1_get_simple(self):
        print("")
        print('test objects get simple objects')

        # Get realms
        items = self.dmg.get_realms()
        for item in items:
            print("Got: ", item)
            assert item.id
            item.get_html_state()
        self.assertEqual(len(items), 5)

        # Get commands
        items = self.dmg.get_commands()
        for item in items:
            print("Got: ", item)
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 50)  # Backend pagination limit ...

        # Get timeperiods
        items = self.dmg.get_timeperiods()
        for item in items:
            print("Got: ", item)
            assert item.id
            item.get_html_state()
        self.assertEqual(len(items), 4)

    def test_5_1_get_linked(self):
        print("")
        print('test objects get linked')

        # Get hosts
        items = self.dmg.get_hosts()
        for item in items:
            print("Got: ", item)
            assert item.id
            self.assertIsInstance(item.check_command, Command) # Must be an object
            self.assertIsInstance(item.check_period, TimePeriod) # Must be an object
        self.assertEqual(len(items), 13)

        # Get services
        items = self.dmg.get_services()
        for item in items:
            print("Got: ", item)
            assert item.id
            self.assertIsInstance(item.check_command, Command) # Must be an object
            self.assertIsInstance(item.check_period, TimePeriod) # Must be an object
        self.assertEqual(len(items), 50)  # Backend pagination limit ...

    def test_5_1_get_linked_groups(self):
        print("")
        print('test objects get self linked')

        # Get hostgroups
        items = self.dmg.get_hostgroups()
        for item in items:
            print("Got: ", item)
            assert item.id
            if item.level != 0:
                self.assertIsInstance(item._parent, HostGroup) # Must be an object
        self.assertEqual(len(items), 9)

        # Get servicegroups
        items = self.dmg.get_servicegroups()
        for item in items:
            print("Got: ", item)
            assert item.id
            if item.level != 0:
                self.assertIsInstance(item._parent, ServiceGroup) # Must be an object
        self.assertEqual(len(items), 6)

        # Get usergroups
        items = self.dmg.get_usergroups()
        for item in items:
            print("Got: ", item)
            assert item.id
            if item.level != 0:
                self.assertIsInstance(item._parent, UserGroup) # Must be an object
        self.assertEqual(len(items), 3)

    @unittest2.skip("Skipped because not very useful and often change :/")
    def test_5_2_total_count(self):
        print("")
        print('test objects count')

        # Get each object type count
        self.assertEqual(self.dmg.count_objects('realm'), 5)
        self.assertEqual(self.dmg.count_objects('command'), 103)
        self.assertEqual(self.dmg.count_objects('timeperiod'), 4)
        self.assertEqual(self.dmg.count_objects('user'), 5)
        self.assertEqual(self.dmg.count_objects('host'), 13)
        self.assertEqual(self.dmg.count_objects('service'), 94)
        self.assertEqual(self.dmg.count_objects('servicegroup'), 6)
        self.assertEqual(self.dmg.count_objects('hostgroup'), 9)
        # self.assertEqual(self.dmg.count_objects('livesynthesis'), 1)

        # Use global method
        self.assertEqual(self.dmg.get_objects_count(object_type=None, refresh=True, log=True), 350)

        # No refresh so get current cached objects count
        self.assertEqual(self.dmg.get_objects_count('realm'), 5)
        self.assertEqual(self.dmg.get_objects_count('command'), 50)
        self.assertEqual(self.dmg.get_objects_count('timeperiod'), 4)
        self.assertEqual(self.dmg.get_objects_count('user'), 5)
        # Not loaded on login in the data manager ... so 0
        self.assertEqual(self.dmg.get_objects_count('host'), 0)
        self.assertEqual(self.dmg.get_objects_count('service'), 0)
        # self.assertEqual(self.dmg.get_objects_count('livesynthesis'), 1)  # Not loaded on login ...

        # With refresh to get total backend objects count
        self.assertEqual(self.dmg.get_objects_count('realm', refresh=True), 5)
        self.assertEqual(self.dmg.get_objects_count('command', refresh=True), 103)
        self.assertEqual(self.dmg.get_objects_count('timeperiod', refresh=True), 4)
        self.assertEqual(self.dmg.get_objects_count('user', refresh=True), 5)
        self.assertEqual(self.dmg.get_objects_count('host', refresh=True), 13)
        self.assertEqual(self.dmg.get_objects_count('service', refresh=True), 94)
        # self.assertEqual(self.dmg.get_objects_count('livesynthesis', refresh=True), 1)

    def test_5_3_livesynthesis(self):
        print("")
        print('test livesynthesis')

        self.maxDiff = None
        expected_ls = {
            'hosts_synthesis': {
                'nb_elts': 13,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_up': 0, 'pct_up': 0.0,
                'nb_up_hard': 0, 'nb_up_soft': 0,
                'nb_down': 0, 'pct_down': 0.0,
                'nb_down_hard': 0, 'nb_down_soft': 0,
                'nb_unreachable': 13, 'pct_unreachable': 100.0,
                'nb_unreachable_hard': 13, 'nb_unreachable_soft': 0,

                'nb_problems': 13, 'pct_problems': 100.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0,
            },
            'services_synthesis': {
                'nb_elts': 94,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_ok': 0, 'pct_ok': 0.0,
                'nb_ok_hard': 0, 'nb_ok_soft': 0,
                'nb_warning': 0, 'pct_warning': 0.0,
                'nb_warning_hard': 0, 'nb_warning_soft': 0,
                'nb_critical': 0, 'pct_critical': 0.0,
                'nb_critical_hard': 0, 'nb_critical_soft': 0,
                'nb_unknown': 94, 'pct_unknown': 100.0,
                'nb_unknown_hard': 94, 'nb_unknown_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0
            }
        }

        # Get livesynthesis
        self.dmg.get_livesynthesis()
        self.assertEqual(self.dmg.get_livesynthesis(), expected_ls)


class Test6Relations(unittest2.TestCase):
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

    def test_01_host_command(self):
        print("--- test Item")

        # Get main realm
        self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Get host
        host = self.dmg.get_host({'where': {'name': 'webui'}})

        print(host.__dict__)
        print(host.check_period)
        assert isinstance(host.check_command, Command)
        assert host.check_command

    def test_02_host_service(self):
        print("--- test Item")

        # Get main realm
        self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Get host
        host = self.dmg.get_host({'where': {'name': 'webui'}})
        print("Host: ", host.__dict__)

        # Get services of this host
        service = self.dmg.get_service({'where': {'name': 'Shinken2-broker', 'host_name': host.id}})
        print("Services: ", service)
