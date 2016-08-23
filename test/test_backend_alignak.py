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
from alignak_backend_client.client import BACKEND_PAGINATION_LIMIT, BACKEND_PAGINATION_DEFAULT

from alignak_webui.objects.backend import BackendConnection

pid = None
backend_address = "http://127.0.0.1:5000/"


# backend_address = "http://94.76.229.155:80"


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
        time.sleep(1)

        # No console output for the applications backend ...
        print("Starting Alignak backend...")
        fnull = open(os.devnull, 'w')
        pid = subprocess.Popen(
            shlex.split('alignak_backend'), stdout=fnull
        )
        time.sleep(1)

        print("Feeding backend...")
        q = subprocess.Popen(
            shlex.split('alignak_backend_import --delete cfg/default/_main.cfg')
        )
        (stdoutdata, stderrdata) = q.communicate()  # now wait
        assert exit_code == 0


def teardown_module():
    print("stop applications backend")

    if backend_address == "http://127.0.0.1:5000/":
        global pid
        pid.kill()


class TestCreation(unittest2.TestCase):
    def test_creation(self):
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
        print("--- count")

        # Count all users
        result = self.be.count('user')
        print("Result: %s", result)
        self.assertEqual(result, 5)

        parameters = {'where': {"name": "admin"}}
        result = self.be.count('user', parameters)
        print("Result: %s", result)
        self.assertEqual(result, 1)

        parameters = {'where': {"name": "fake"}}
        result = self.be.count('user', parameters)
        print("Result: %s", result)
        self.assertEqual(result, 0)  # Not found !

        # Get admin user
        parameters = {'where': {"name": "admin"}}
        result = self.be.get('user', parameters)
        print(result)
        self.assertEqual(len(result), 1)  # Only 1 is admin

        result = self.be.count('user', result[0]['_id'])
        print("Result: %s", result)
        self.assertEqual(result, 1)

    def test_get(self):
        print("--- get")

        # Get all users
        result = self.be.get('user')
        print("%s users: " % len(result))
        for user in result:
            self.assertIn('name', user)
            self.assertIn('_total', user)  # Each element has an extra _total attribute !
            print(" - %s (one out of %d)" % (user['name'], user['_total']))
            self.assertEqual(user['_total'], 5)
        self.assertEqual(len(result), 5)  # Default configuration has 5 users

        parameters = {'where': {"name": "fake"}}
        result = self.be.get('user', parameters)
        print(result)
        self.assertEqual(len(result), 0)  # Not found

        parameters = {'where': {"name": "admin"}}
        result = self.be.get('user', parameters)
        print(result)
        self.assertEqual(len(result), 1)  # Only 1 is admin
        admin_id = result[0]['_id']
        print("Administrator id:", admin_id)

        result = self.be.get('user', result[0]['_id'])
        print("Result: %s", result)
        self.assertEqual(len(result), 1)  # Only 1 is admin
        self.assertEqual(result[0]['_id'], admin_id)

        # Directly address object in the backend
        result = self.be.get('user/' + result[0]['_id'])
        print("--- Result: %s", result)
        self.assertEqual(len(result), 40)  # 40 attributes in the result
        self.assertEqual(result['_id'], admin_id)

    def test_get_all(self):
        print("--- get all")

        # Get one page of services
        result = self.be.get('service')
        print("Backend pagination default:", BACKEND_PAGINATION_DEFAULT)
        print("Backend pagination limit:", BACKEND_PAGINATION_LIMIT)

        print("%s services: " % len(result))
        for service in result:
            print(" - %s" % service['name'])
        assert len(result) == BACKEND_PAGINATION_LIMIT
        # Should be DEFAULT and not LIMIT ...
        # See https://github.com/Alignak-monitoring-contrib/alignak-backend/issues/52
        # assert len(result) == BACKEND_PAGINATION_DEFAULT # Default backend pagination

        # Get all services
        result = self.be.get('service', all_elements=True)
        print("%s services: " % len(result))
        for service in result:
            print(" - %s" % service['name'])
        self.assertEqual(len(result), 94)
