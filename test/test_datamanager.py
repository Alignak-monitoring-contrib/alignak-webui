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

from alignak_webui.objects.item import Contact, Host, Service, Command
from alignak_webui.objects.datamanager import DataManager
from alignak_webui import get_app_config, _
import alignak_webui.app

from logging import getLogger, DEBUG, INFO, WARNING
loggerDm = getLogger('alignak_webui.objects.datamanager')
loggerDm.setLevel(DEBUG)
loggerItems = getLogger('alignak_webui.objects.item')
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
            shlex.split('cfg_to_backend --delete cfg/default/_main.cfg')
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

    def setUp(self):
        print ""

    def tearDown(self):
        print ""

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
        assert datamanager.backend.authenticated
        print 'logged in as admin in the backend'
        # Datamanager is not yet aware of the user login !!!
        assert datamanager.get_logged_user() is None

        # Get current user
        # 'name' is not existing!
        parameters = {'where': '{"name":"admin"}'}
        items = datamanager.backend.get('contact', params=parameters)
        print items
        assert '_items' in items
        assert len(items['_items']) == 1
        assert items['_items'][0]["_id"]
        admin_id = items['_items'][0]["_id"]

        users = datamanager.find_object('contact', admin_id)
        print users
        assert len(users) == 1
        # New user object created in the DM cache ...
        assert datamanager.get_objects_count('contact') == 1

        # Unknown user not found
        with assert_raises(ValueError) as cm:
            user = datamanager.find_object('contact', 'fake_id')
        ex = cm.exception
        print ex
        assert str(ex) == """contact, {"_id": "%s"} was not found in the cache nor in the backend""" % 'fake_id'


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
        assert datamanager.connection_message == 'Backend is not available'
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
        assert datamanager.get_logged_user().get_username() == 'admin'
        assert datamanager.get_logged_user().authenticated
        user_token = datamanager.get_logged_user().token

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
        # assert datamanager.connection_message == 'Backend connected'
        # When user authentication is made thanks to a token, DM is not loaded ... it is assumed that load already occured!

        print 'DM login'
        assert datamanager.user_login('admin', 'admin', load=False)
        user_token = datamanager.get_logged_user().token
        assert datamanager.user_login(user_token)
        assert datamanager.connection_message == 'Backend connected'


        assert datamanager.logged_in_user
        assert datamanager.get_logged_user() != None
        assert datamanager.get_logged_user().get_username() == 'admin'
        assert datamanager.get_logged_user().authenticated


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
        assert result == 0  # No new objects created ...

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print "Result:", result
        # Must have loaded some objects ...
        assert result != 0

    def test_3_3_get_errors(self):
        print ''
        print 'test get errors'

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print "Result:", result
        assert result == 0  # No new objects created ...

        # Get users error
        item = self.dmg.get_contact('unknown')
        assert not item


class test_4_not_admin(unittest2.TestCase):

    def setUp(self):
        print ""
        self.dmg = DataManager(backend_endpoint=backend_address)
        print 'Data manager', self.dmg

    def tearDown(self):
        print ""

    @unittest2.skip("To be completed test ...")
    def test_4_1_load(self):
        print ''
        print 'test load not admin user'

        # Initialize and load ... no reset
        assert self.dmg.user_login('admin', 'admin')
        result = self.dmg.load()
        print "Result:", result
        assert result == 0  # No new objects created ...

        # Create a non admin user ...
        # TODO
        # ***************************************
        return

        # Logout
        self.dmg.reset(logout=True)
        assert not self.dmg.backend.connected
        assert self.dmg.get_logged_user() == None
        assert self.dmg.loaded == False

        # Login as not_admin created user
        assert self.dmg.user_login('not_admin', 'NOPASSWORDSET', load=False)
        assert self.dmg.backend.authenticated
        assert self.dmg.get_logged_user().get_username() == 'not_admin'
        print 'logged in as not_admin'

        # Initialize and load ...
        result = self.dmg.load()
        print "Result:", result
        print "Objects count:", self.dmg.get_objects_count()
        assert result == 2                          # test_service + relation
        assert self.dmg.get_objects_count() == 3    # not_admin user + test_service + relation

        # Initialize and load ... with reset
        result = self.dmg.load(reset=True)
        print "Result:", result
        print "Objects count:", self.dmg.get_objects_count()
        assert result == 3                          # not_admin user + test_service + relation
        assert self.dmg.get_objects_count() == 3    # not_admin user + test_service + relation


        # Not admin user can see only its own data, ...
        # -------------------------------------------

        # Do not check the length because the backend contains more elements than needed ...
        dump_backend(not_admin_user=True, test_service=True)


        # Get users
        items = self.dmg.get_contacts()
        print "Contacts:", items
        assert len(items) == 1
        # 1 user only ...

        # Get hosts
        items = self.dmg.get_commands()
        print "Commands:", items
        assert len(items) == 1

        # Get services
        items = self.dmg.get_hosts()
        print "Hosts:", items
        assert len(items) == 1

        # Get services
        items = self.dmg.get_services()
        print "Services:", items
        assert len(items) == 1

        assert False



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

    def test_5_1_status(self):
        print ''
        print 'test objects status'

        # Get users
        items = self.dmg.get_contacts()
        for item in items:
            print "Got", item
            assert item.get_id()
            icon_status = item.get_html_state()

        # Get commands
        items = self.dmg.get_commands()
        for item in items:
            print "Got: ", item
            assert item.get_id()
            icon_status = item.get_html_state()

