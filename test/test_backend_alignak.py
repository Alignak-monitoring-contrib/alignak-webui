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
import json
import shlex
import subprocess
import time

import unittest2
from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

from alignak_webui.backend.backend import BackendConnection

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


class TestCreation(unittest2.TestCase):
    def test_creation(self):
        """ Backend creation - singleton object """
        print("--- creation")

        be = BackendConnection(backend_address)
        assert be
        print("Backend object:", be)

        be2 = BackendConnection(backend_address)
        assert be2
        print("Backend object:", be2)

        # Objet is a singleton
        assert be == be2


class TestLogin(unittest2.TestCase):
    def test_login(self):
        """ Backend login """
        print("--- login")

        be = BackendConnection(backend_address)
        assert be
        print("Backend object:", be)

        be.login('admin', 'fake')
        assert not be.connected

        be.login('admin', 'admin')
        assert be.connected


class TestGet(unittest2.TestCase):
    def setUp(self):
        print("Login...")
        self.be = BackendConnection(backend_address)
        assert self.be
        self.be.login('admin', 'admin')
        assert self.be.connected

        print("Logged in")

    def test_count(self):
        """ Backend count elements """
        print("--- count")

        # Count all users (no templates)
        result = self.be.count('user', params={'where': {'_is_template': False}})
        print("Result: %s" % result)
        assert result == 8

        # Count all users (and templates)
        result = self.be.count('user')
        print("Result: %s" % result)
        assert result == 10

        parameters = {'where': {"name": "admin"}}
        result = self.be.count('user', parameters)
        print("Result: %s" % result)
        assert result == 1

        parameters = {'where': {"name": "fake"}}
        result = self.be.count('user', parameters)
        print("Result: %s" % result)
        assert result == 0  # Not found !

        # Get admin user
        parameters = {'where': {"name": "admin"}}
        result = self.be.get('user', parameters)
        print(result)
        assert len(result) == 1  # Only 1 is admin

        result = self.be.count('user', result[0]['_id'])
        print("Result: %s" % result)
        assert result == 1

    def test_get(self):
        """ Backend get elements """
        print("--- get")

        # Get all users (no templates)
        result = self.be.get('user', params={'where': {'_is_template': False}})
        print("%s users: " % len(result))
        for user in result:
            assert 'name' in user
            assert '_total' in user  # Each element has an extra _total attribute !
            print(" - %s (one out of %d)" % (user['name'], user['_total']))
            assert user['_total'] == 8
        assert len(result) == 8  # Default configuration has 8 users

        parameters = {'where': {"name": "fake"}}
        result = self.be.get('user', parameters)
        print(result)
        assert len(result) == 0  # Not found

        parameters = {'where': {"name": "admin"}}
        result = self.be.get('user', parameters)
        print(result)
        assert len(result) == 1  # Only 1 is admin
        admin_id = result[0]['_id']
        print("Administrator id:", admin_id)

        result = self.be.get('user', result[0]['_id'])
        print("Result: %s", result)
        assert len(result) == 1  # Only 1 is admin
        assert result[0]['_id'] == admin_id

        # Directly address object in the backend
        result = self.be.get('user/' + result[0]['_id'])
        print("--- Result: %s", result)
        # assert len(result) == 43  # 43 attributes in the result
        assert result['_id'] == admin_id

    def test_get_all(self):
        """ Backend get all elements """
        print("--- get all")

        print("Backend pagination default:", BACKEND_PAGINATION_DEFAULT)
        print("Backend pagination limit:", BACKEND_PAGINATION_LIMIT)

        # Get one page of services
        result = self.be.get('service', all_elements=False,
                             params={'where': {'_is_template': False}})
        print("%s services: " % len(result))
        for service in result:
            print(" - %s" % service['name'])
        assert len(result) == BACKEND_PAGINATION_LIMIT
        # Should be DEFAULT and not LIMIT ...
        # See https://github.com/Alignak-monitoring-contrib/alignak-backend/issues/52
        # assert len(result) == BACKEND_PAGINATION_DEFAULT # Default backend pagination

        # Get all services (no templates)
        result = self.be.get('service', all_elements=True,
                             params={'where': {'_is_template': False}})
        print("%s services: " % len(result))
        for service in result:
            print(" - %s" % service['name'])
        # On Travis we get 74 !
        # assert len(result) == 76
        assert len(result) > BACKEND_PAGINATION_LIMIT
