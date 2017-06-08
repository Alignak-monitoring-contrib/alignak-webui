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

from alignak_webui.objects.element import BackendElement
from alignak_webui.objects.item_user import User
from alignak_webui.objects.item_usergroup import UserGroup
from alignak_webui.objects.item_command import Command
from alignak_webui.objects.item_host import Host
from alignak_webui.objects.item_service import Service
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_hostgroup import HostGroup
from alignak_webui.objects.item_servicegroup import ServiceGroup
from alignak_webui.backend.datamanager import DataManager

from logging import getLogger, DEBUG, INFO, WARNING

loggerDm = getLogger('alignak_webui.objects.datamanager')
loggerDm.setLevel(INFO)
loggerItems = getLogger('alignak_webui.objects.element')
loggerItems.setLevel(INFO)
loggerBackend = getLogger('alignak_webui.objects.backend')
loggerBackend.setLevel(INFO)

backend_process = None
backend_address = "http://127.0.0.1:5000/"
datamgr = None

COUNT_KNOWN_CLASSES = 26


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


class TestCreation(unittest2.TestCase):
    def test_2_1_creation_load(self):
        """ Datamanager creation and load """
        print('------------------------------')
        print('test creation')

        datamanager = DataManager(alignak_webui.app.app)
        assert datamanager.backend
        assert datamanager.loaded == False
        assert datamanager.logged_in_user is None
        print('Data manager', datamanager)
        # Got known managed elements classes
        assert len(datamanager.known_classes) == COUNT_KNOWN_CLASSES

        # Initialize and load fail ...
        print('DM load failed')
        result = datamanager.load()
        # Refused because no backend logged-in user
        assert not result

        # Login error
        print('DM logging bad password')
        assert not datamanager.user_login('admin', 'fake')
        print(datamanager.connection_message)
        assert datamanager.connection_message == 'Access denied! Check your username and password.'
        print(datamanager.logged_in_user)
        assert not datamanager.logged_in_user

        # Create new datamanager - do not use default backend address
        print('DM initialization')
        datamanager = DataManager(alignak_webui.app.app)
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
        assert datamanager.connection_message == 'Access denied! Check your username and password.'
        print(datamanager.logged_in_user)
        assert not datamanager.logged_in_user

        # User login but do not load yet
        print('DM login ok')
        assert datamanager.user_login('admin', 'admin', load=False)
        assert datamanager.connection_message == 'Access granted'
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
        assert datamanager.connection_message == 'Access granted'

        assert datamanager.logged_in_user
        assert datamanager.logged_in_user is not None
        assert datamanager.logged_in_user.id is not None
        assert datamanager.logged_in_user.get_username() == 'admin'
        assert datamanager.logged_in_user.authenticated


class TestLoadCreate(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(alignak_webui.app.app)
        print('Data manager', self.dmg)

    def test_3_1_load(self):
        """ Datamanager load """
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
        """ Datamanager objects get errors """
        print('test get errors')

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print("Result:", result)
        assert result == 0  # No new objects created ...

        # Get elements error
        item = self.dmg.get_user('unknown')
        assert not item
        item = self.dmg.get_userrestrictrole('unknown')
        assert not item
        item = self.dmg.get_realm('unknown')
        assert not item
        item = self.dmg.get_host('unknown')
        assert not item
        item = self.dmg.get_hostgroup('unknown')
        assert not item
        item = self.dmg.get_hostdependency('unknown')
        assert not item
        item = self.dmg.get_service('unknown')
        assert not item
        item = self.dmg.get_servicegroup('unknown')
        assert not item
        item = self.dmg.get_servicedependency('unknown')
        assert not item
        item = self.dmg.get_command('unknown')
        assert not item
        item = self.dmg.get_history('unknown')
        assert not item
        item = self.dmg.get_logcheckresult('unknown')
        assert not item
        item = self.dmg.get_timeperiod('unknown')
        assert not item


class TestNotAdmin(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(alignak_webui.app.app)
        print('Data manager', self.dmg)

    @unittest2.skip("Skipped because creating a new user do not allow him to get its own data (timeperiod get is 404)!")
    def test_4_1_load(self):
        """ Datamanager load, not admin user """
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
        print("Objects count:", self.dmg.get_objects_count('host'))
        print("Objects count:", self.dmg.get_objects_count('service'))
        print("Objects count (log):", self.dmg.get_objects_count(log=True))
        # assert result == 0                          # Only the newly created user, so no new objects loaded
        # assert self.dmg.get_objects_count() == 1    # not_admin user

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print("Result:", result)
        print("Objects count:", self.dmg.get_objects_count())
        print("Objects count:", self.dmg.get_objects_count('host'))
        print("Objects count:", self.dmg.get_objects_count('service'))
        print("Objects count (log):", self.dmg.get_objects_count(log=True))
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


class TestBasic(unittest2.TestCase):
    def setUp(self):
        self.dmg = DataManager(alignak_webui.app.app)
        print('Data manager', self.dmg)

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

    def tearDown(self):
        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.logged_in_user is None
        assert self.dmg.loaded == False

    def test_5_1_get_simple(self):
        """ Datamanager objects get - simple elements """
        print('test objects get simple objects')

        # Get realms
        items = self.dmg.get_realms()
        for item in items:
            print("Got: ", item)
            assert item.id
            item.get_html_state()
        assert len(items) == 5

        # Get commands
        items = self.dmg.get_commands()
        for item in items:
            print("Got: ", item)
            assert item.id
            icon_status = item.get_html_state()
        assert len(items) == 50  # Backend pagination limit ...

        # Get timeperiods
        items = self.dmg.get_timeperiods()
        for item in items:
            print("Got: ", item)
            assert item.id
            item.get_html_state()
        assert len(items) == 5

    def test_5_1_get_linked(self):
        """ Datamanager objects get - linked elements """
        print('test objects get linked')

        # Get hosts
        items = self.dmg.get_hosts()
        for item in items:
            print("Got: ", item)
            assert item.id
            assert isinstance(item.check_command, Command) # Must be an object
            assert isinstance(item.check_period, TimePeriod) # Must be an object
        assert len(items) == 13

        # Get services
        items = self.dmg.get_services()
        for item in items:
            print("Got: ", item)
            assert item.id
            assert isinstance(item.check_command, Command) # Must be an object
            assert isinstance(item.check_period, TimePeriod) # Must be an object
        assert len(items) == 50  # Backend pagination limit ...

    def test_5_1_get_linked_groups(self):
        """ Datamanager objects get - group elements """
        print('test objects get self linked')

        # Get hostgroups
        items = self.dmg.get_hostgroups()
        for item in items:
            print("Got: ", item)
            assert item.id
            if item.level != 0:
                assert isinstance(item._parent, HostGroup) # Must be an object
        assert len(items) == 9

        # Get servicegroups
        items = self.dmg.get_servicegroups()
        for item in items:
            print("Got: ", item)
            assert item.id
            if item.level != 0:
                assert isinstance(item._parent, ServiceGroup) # Must be an object
        assert len(items) == 6

        # Get usergroups
        items = self.dmg.get_usergroups()
        for item in items:
            print("Got: ", item)
            assert item.id
            if item.level != 0:
                assert isinstance(item._parent, UserGroup) # Must be an object
        assert len(items) == 4

    def test_5_3_livesynthesis(self):
        """ Datamanager objects get - livesynthesis """
        print('test livesynthesis')

        self.maxDiff = None

        # Get livesynthesis - user logged-in realm and its sub-realms
        expected_ls = {
            '_id': self.dmg.my_ls['_id'],
            'hosts_synthesis': {
                'nb_elts': 11,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_up': 0, 'pct_up': 0.0,
                'nb_up_hard': 0, 'nb_up_soft': 0,
                'nb_down': 0, 'pct_down': 0.0,
                'nb_down_hard': 0, 'nb_down_soft': 0,
                'nb_unreachable': 11, 'pct_unreachable': 100.0,
                'nb_unreachable_hard': 11, 'nb_unreachable_soft': 0,

                'nb_problems': 11, 'pct_problems': 100.0,
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
                'nb_unreachable': 0, 'pct_unreachable': 0.0,
                'nb_unreachable_hard': 0, 'nb_unreachable_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0
            }
        }
        got_ls = self.dmg.get_livesynthesis({'concatenation': '1',
                                             'where': {'_realm': self.dmg.my_realm.id}})
        assert got_ls['hosts_synthesis'] == expected_ls['hosts_synthesis']
        assert got_ls['services_synthesis'] == expected_ls['services_synthesis']

        # Get livesynthesis - user logged-in realm and no sub realms
        expected_ls = {
            '_id': self.dmg.my_ls['_id'],
            'hosts_synthesis': {
                'nb_elts': 11,
                'business_impact': 0,

                'warning_threshold': 2.0, 'global_warning_threshold': 2.0,
                'critical_threshold': 5.0, 'global_critical_threshold': 5.0,

                'nb_up': 0, 'pct_up': 0.0,
                'nb_up_hard': 0, 'nb_up_soft': 0,
                'nb_down': 0, 'pct_down': 0.0,
                'nb_down_hard': 0, 'nb_down_soft': 0,
                'nb_unreachable': 11, 'pct_unreachable': 100.0,
                'nb_unreachable_hard': 11, 'nb_unreachable_soft': 0,

                'nb_problems': 11, 'pct_problems': 100.0,
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
                # Travis says 74 whereas it is 76 !
                'nb_unknown': 94, 'pct_unknown': 100.0,
                'nb_unknown_hard': 94, 'nb_unknown_soft': 0,
                # 'nb_unknown': 76, 'pct_unknown': 100.0,
                # 'nb_unknown_hard': 76, 'nb_unknown_soft': 0,
                'nb_unreachable': 0, 'pct_unreachable': 0.0,
                'nb_unreachable_hard': 0, 'nb_unreachable_soft': 0,

                'nb_problems': 0, 'pct_problems': 0.0,
                'nb_flapping': 0, 'pct_flapping': 0.0,
                'nb_acknowledged': 0, 'pct_acknowledged': 0.0,
                'nb_in_downtime': 0, 'pct_in_downtime': 0.0
            }
        }
        got_ls = self.dmg.get_livesynthesis(self.dmg.my_ls['_id'])
        assert got_ls['hosts_synthesis'] == expected_ls['hosts_synthesis']
        assert got_ls['services_synthesis'] == expected_ls['services_synthesis']


class TestRelations(unittest2.TestCase):
    def setUp(self):
        print("setting up ...")
        self.dmg = DataManager(alignak_webui.app.app)
        print('Data manager', self.dmg)

        # Initialize and do not load
        assert self.dmg.user_login('admin', 'admin', load=False)

    def tearDown(self):
        print("tearing down ...")
        # Logout
        self.dmg.reset(logout=True)

    def test_relation_host_command(self):
        """ Datamanager objects get - host/command relation """
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

    def test_relation_host_service(self):
        """ Datamanager objects get - host/services relation """
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


class TestHosts(unittest2.TestCase):
    def setUp(self):
        print("setting up ...")
        self.dmg = DataManager(alignak_webui.app.app)
        print('Data manager', self.dmg)

        # Initialize and do not load
        assert self.dmg.user_login('admin', 'admin', load=False)

    def tearDown(self):
        print("tearing down ...")
        # Logout
        self.dmg.reset(logout=True)

    def test_hosts(self):
        """ Datamanager objects get - hosts """
        print("Get all hosts")

        # Get main realm
        self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Get all hosts
        hosts = self.dmg.get_hosts()
        assert 13 == len(hosts)
        print("---")
        for host in hosts:
            print("Got host: %s" % host)

        # Get all hosts (really all...)
        hosts = self.dmg.get_hosts(all_elements=True)
        assert 13 == len(hosts)
        print("---")
        for host in hosts:
            print("Got host: %s" % host)

        # Get all hosts (with all embedded relations)
        hosts = self.dmg.get_hosts(embedded=True)
        assert 13 == len(hosts)
        print("---")
        for host in hosts:
            print("Got host: %s" % host)

        # Get all hosts templates
        hosts = self.dmg.get_hosts(template=True)
        assert 30 == len(hosts)
        print("---")
        for host in hosts:
            print("Got host template: %s" % host)

        # Get one host
        hosts = self.dmg.get_hosts({'where': {'name': 'webui'}})
        assert 1 == len(hosts)
        print("---")
        for host in hosts:
            print("Got host: %s" % host)
        assert hosts[0].name == 'webui'

        # Get one host
        host = self.dmg.get_host({'where': {'name': 'webui'}})
        assert host.name == 'webui'

        # Get one host
        host = self.dmg.get_host(host._id)
        assert host.name == 'webui'
        assert host.status == 'UNREACHABLE'

        # Get host services
        services = self.dmg.get_host_services({'where': {'name': 'unknown'}})
        assert services == -1

        services = self.dmg.get_host_services({'where': {'name': 'webui'}})
        print("---")
        service_name = ''
        for service in services:
            print("Got service: %s" % service)
            service_name = service['name']
        assert len(services) > 1
        services = self.dmg.get_host_services({'where': {'name': 'webui'}}, search={'where': {'name': service_name}})
        services = self.dmg.get_host_services(host)
        assert len(services) > 1

        # Get host overall state
        (state, status) = self.dmg.get_host_overall_state(host)
        print("Host overall state: %s %s" % (state, status))
        assert state == 3
        assert status == 'warning'

    def test_host(self):
        """ Datamanager objects get - host """
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
