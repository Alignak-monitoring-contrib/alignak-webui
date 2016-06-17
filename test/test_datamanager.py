#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import json
import time
import shlex
import unittest2
import subprocess

from nose import with_setup
from nose.tools import *

# Test environment variables
os.environ['TEST_WEBUI'] = '1'
os.environ['TEST_WEBUI_CFG'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print "Configuration file", os.environ['TEST_WEBUI_CFG']

from alignak_backend_client.client import Backend, BackendException
from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

from alignak_webui.objects.item import User, Host, Service, Command
from alignak_webui.objects.datamanager import DataManager
from alignak_webui import get_app_config, _
import alignak_webui.app

from logging import getLogger, DEBUG, INFO, WARNING
loggerDm = getLogger('alignak_webui.objects.datamanager')
loggerDm.setLevel(INFO)
loggerItems = getLogger('alignak_webui.objects.item')
loggerItems.setLevel(WARNING)
loggerItems = getLogger('alignak_webui.objects.backend')
loggerItems.setLevel(WARNING)

pid = None
backend_address = "http://127.0.0.1:5000/"
# backend_address = "http://94.76.229.155:80"


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

        print ("Starting Alignak backend...")
        pid = subprocess.Popen(
            shlex.split('alignak_backend')
        )
        print ("PID: %s" % pid)
        time.sleep(1)

        print ("Feeding backend...")
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


datamgr = None

class test_1_find_and_search(unittest2.TestCase):

    def test_1_1_find_objects(self):
        print ''
        print 'test find_objects - no objects in cache'

        # Create new datamanager - do not use default backend address
        datamanager = DataManager(backend_endpoint=backend_address)
        assert datamanager.backend
        assert datamanager.loaded == False
        assert datamanager.get_logged_user() is None

        # Login ...
        assert datamanager.backend.login('admin', 'admin')
        assert datamanager.loaded == False
        assert datamanager.backend.connected
        print 'logged in as admin in the backend'
        # Datamanager is not yet aware of the user login !!!
        assert datamanager.get_logged_user() is None

        # Get current user
        # 'name' is not existing!
        parameters = {'where': {"name":"admin"}}
        items = datamanager.backend.get('user', params=parameters)
        print items
        assert len(items) == 1
        assert items[0]["_id"]
        admin_id = items[0]["_id"]

        users = datamanager.find_object('user', admin_id)
        print users
        assert len(users) == 1
        # New user object created in the DM cache ...
        assert datamanager.get_objects_count('user') == 1

        # Unknown user not found
        with assert_raises(ValueError) as cm:
            user = datamanager.find_object('user', 'fake_id')
        ex = cm.exception
        print ex
        assert str(ex) == """user, search: {'max_results': 50, 'where': '{"_id": "%s"}', 'page': 0} was not found in the backend""" % 'fake_id'


class test_2_creation(unittest2.TestCase):

    def test_2_1_creation_load(self):
        print ''
        print 'test creation'

        datamanager = DataManager()
        assert datamanager.backend
        assert datamanager.loaded == False
        assert datamanager.get_logged_user() == None
        print 'Data manager', datamanager

        # Initialize and load fail ...
        print 'DM load failed'
        result = datamanager.load()
        # Refused because no backend logged-in user
        assert not result

        # Login error
        print 'DM logging bad password'
        assert not datamanager.user_login('admin', 'fake')
        print datamanager.connection_message
        assert datamanager.connection_message == 'Backend connection refused...'
        print datamanager.logged_in_user
        assert not datamanager.logged_in_user

        # Create new datamanager - do not use default backend address
        print 'DM initialization'
        datamanager = DataManager(backend_endpoint=backend_address)
        assert datamanager.backend
        assert datamanager.loaded == False
        assert datamanager.get_logged_user() == None
        print 'Data manager', datamanager

        # Initialize and load fail ...
        print 'DM load fail'
        result = datamanager.load()
        # Refused because no backend logged-in user
        assert not result

        # Login error
        print 'DM logging bad password'
        assert not datamanager.user_login('admin', 'fake')
        print datamanager.connection_message
        assert datamanager.connection_message == 'Backend connection refused...'
        print datamanager.logged_in_user
        assert not datamanager.logged_in_user

        # User login but do not load yet
        print 'DM login ok'
        assert datamanager.user_login('admin', 'admin', load=False)
        assert datamanager.connection_message == 'Connection successful'
        print datamanager.logged_in_user
        assert datamanager.logged_in_user
        assert datamanager.get_logged_user() != None
        assert datamanager.get_logged_user().id != None
        assert datamanager.get_logged_user().get_username() == 'admin'
        assert datamanager.get_logged_user().authenticated
        user_token = datamanager.get_logged_user().token
        print User._cache[datamanager.get_logged_user().id].__dict__

        print 'DM reset'
        datamanager.reset()
        # Still logged-in...
        assert datamanager.logged_in_user
        assert datamanager.get_logged_user() != None

        print 'DM reset - logout'
        datamanager.reset(logout=True)
        # Logged-out...
        assert not datamanager.logged_in_user
        assert datamanager.get_logged_user() == None

        # User login with an authentication token
        print 'DM login - token'
        assert datamanager.user_login(user_token)
        # When user authentication is made thanks to a token, DM is not loaded ... it is assumed that load already occured!

        print 'DM login'
        assert datamanager.user_login('admin', 'admin', load=False)
        print datamanager.get_logged_user()
        print datamanager.get_logged_user().token
        user_token = datamanager.get_logged_user().token
        assert datamanager.user_login(user_token)
        assert datamanager.connection_message == 'Connection successful'

        assert datamanager.logged_in_user
        assert datamanager.get_logged_user() != None
        assert datamanager.get_logged_user().id != None
        assert datamanager.get_logged_user().get_username() == 'admin'
        assert datamanager.get_logged_user().authenticated
        # assert False


class test_3_load_create(unittest2.TestCase):

    def setUp(self):
        print ""

        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

    def tearDown(self):
        print ""

    def test_3_1_load(self):
        print ''
        print 'test load as admin'

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print "Result:", result
        self.assertEqual(result, 0)  # No new objects created ...

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print "Result:", result
        # Must have loaded some objects ...
        self.assertNotEqual(result, 0)

    def test_3_3_get_errors(self):
        print ''
        print 'test get errors'

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print "Result:", result
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

        # ... to be completed ...


class test_4_not_admin(unittest2.TestCase):

    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

    def tearDown(self):
        print ""

    def test_4_1_load(self):
        print ''
        print 'test load not admin user'

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print "Result:", result
        assert result == 0  # No new objects created ...

        # Get main realm
        realm_all = self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        tp_all = self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Create a non admin user ...
        # Create a new user
        print 'create a user'
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
            "service_notification_commands": [ ],
            "service_notification_options": [
                "w",
                "u",
                "c",
                "r"
            ],
            "note": "Monitoring template : default",
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
        assert self.dmg.add_user(data)

        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.get_logged_user() == None
        assert self.dmg.loaded == False

        # Login as not_admin created user
        assert self.dmg.user_login('not_admin', 'NOPASSWORDSET', load=False)
        assert self.dmg.backend.connected
        assert self.dmg.get_logged_user().get_username() == 'not_admin'
        print 'logged in as not_admin'

        # Initialize and load ...
        result = self.dmg.load()
        print "Result:", result
        print "Objects count:", self.dmg.get_objects_count()
        # assert result == 0                          # Only the newly created user, so no new objects loaded
        # assert self.dmg.get_objects_count() == 1    # not_admin user

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print "Result:", result
        print "Objects count:", self.dmg.get_objects_count()
        # assert result == 3                          # not_admin user + test_service + relation
        # assert self.dmg.get_objects_count() == 3    # not_admin user + test_service + relation


        # Not admin user can see only its own data, ...
        # -------------------------------------------

        # Do not check the length because the backend contains more elements than needed ...
        # dump_backend(not_admin_user=True, test_service=True)

        # Get users
        items = self.dmg.get_users()
        print "Users:", items
        # assert len(items) == 1
        # 1 user only ...

        # Get commands
        items = self.dmg.get_commands()
        print "Commands:", items
        # assert len(items) == 1

        # Get realms
        items = self.dmg.get_realms()
        print "Commands:", items
        # assert len(items) == 1

        # Get timeperiods
        items = self.dmg.get_timeperiods()
        print "Commands:", items
        # assert len(items) == 1

        # Get hosts
        items = self.dmg.get_hosts()
        print "Hosts:", items
        # assert len(items) == 1

        # Get services
        items = self.dmg.get_services()
        print "Services:", items
        # assert len(items) == 1


class test_5_basic_tests(unittest2.TestCase):

    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()

    def tearDown(self):
        print ""
        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.get_logged_user() == None
        assert self.dmg.loaded == False

    def test_5_1_get(self):
        print ''
        print 'test objects get'

        # Get users
        items = self.dmg.get_users()
        for item in items:
            print "Got", item
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 5)

        # Get realms
        items = self.dmg.get_realms()
        for item in items:
            print "Got: ", item
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 5)

        # Get commands
        items = self.dmg.get_commands()
        for item in items:
            print "Got: ", item
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 50)    # Backend pagination limit ...

        # Get hosts
        items = self.dmg.get_hosts()
        for item in items:
            print "Got: ", item
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 13)

        # Get services
        items = self.dmg.get_services()
        for item in items:
            print "Got: ", item
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 50)    # Backend pagination limit ...

        # Get timeperiods
        items = self.dmg.get_timeperiods()
        for item in items:
            print "Got: ", item
            assert item.id
            icon_status = item.get_html_state()
        self.assertEqual(len(items), 4)

    def test_5_2_total_count(self):
        print ''
        print 'test objects count'

        # Get each object type count
        self.assertEqual(self.dmg.count_objects('realm'), 5)
        self.assertEqual(self.dmg.count_objects('command'), 103)
        self.assertEqual(self.dmg.count_objects('timeperiod'), 4)
        self.assertEqual(self.dmg.count_objects('user'), 4+1)    #Because a new user is created during the tests
        self.assertEqual(self.dmg.count_objects('host'), 13)
        self.assertEqual(self.dmg.count_objects('service'), 89)
        self.assertEqual(self.dmg.count_objects('livestate'), 13+89)
        self.assertEqual(self.dmg.count_objects('servicegroup'), 5)
        self.assertEqual(self.dmg.count_objects('hostgroup'), 8)
        # self.assertEqual(self.dmg.count_objects('livesynthesis'), 1)

        # Use global method
        self.assertEqual(self.dmg.get_objects_count(object_type=None, refresh=True, log=True), 337)

        # No refresh so get current cached objects count
        self.assertEqual(self.dmg.get_objects_count('realm'), 5)
        self.assertEqual(self.dmg.get_objects_count('command'), 50)
        self.assertEqual(self.dmg.get_objects_count('timeperiod'), 4)
        self.assertEqual(self.dmg.get_objects_count('user'), 4+1)
        # Not loaded on login in the data manager ... so 0
        self.assertEqual(self.dmg.get_objects_count('host'), 0)
        self.assertEqual(self.dmg.get_objects_count('service'), 0)
        self.assertEqual(self.dmg.get_objects_count('livestate'), 0)
        # self.assertEqual(self.dmg.get_objects_count('livesynthesis'), 1)  # Not loaded on login ...

        # With refresh to get total backend objects count
        self.assertEqual(self.dmg.get_objects_count('realm', refresh=True), 5)
        self.assertEqual(self.dmg.get_objects_count('command', refresh=True), 103)
        self.assertEqual(self.dmg.get_objects_count('timeperiod', refresh=True), 4)
        self.assertEqual(self.dmg.get_objects_count('user', refresh=True), 4+1)
        self.assertEqual(self.dmg.get_objects_count('host', refresh=True), 13)
        self.assertEqual(self.dmg.get_objects_count('service', refresh=True), 89)
        self.assertEqual(self.dmg.get_objects_count('livestate', refresh=True), 13+89)
        # self.assertEqual(self.dmg.get_objects_count('livesynthesis', refresh=True), 1)


class test_6_relations(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

        # Initialize and do not load
        assert self.dmg.user_login('admin', 'admin', load=False)

    def tearDown(self):
        print ""
        print "tearing down ..."
        # Logout
        self.dmg.reset(logout=True)

    def test_01_host_command(self):
        print "--- test Item"

        # Get main realm
        realm_all = self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        tp_all = self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Get host
        host = self.dmg.get_host({'where': {'name': 'webui'}})

        print host.__dict__
        print host.check_period
        assert isinstance(host.check_command, Command)
        assert host.check_command


    def test_02_host_service(self):
        print "--- test Item"

        # Get main realm
        realm_all = self.dmg.get_realm({'where': {'name': 'All'}})

        # Get main TP
        tp_all = self.dmg.get_timeperiod({'where': {'name': '24x7'}})

        # Get host
        host = self.dmg.get_host({'where': {'name': 'webui'}})
        print "Host: ", host.__dict__

        # Get services of this host
        service = self.dmg.get_service({'where': {'name': 'Shinken2-broker', 'host_name': host.id}})
        print "Services: ", service
