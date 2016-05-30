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

import os
import json
import time
import shlex
import unittest2
import subprocess

from nose import with_setup
from nose.tools import *

from alignak_webui.backend.glpi_ws_client import Glpi, GlpiException
from alignak_webui.backend.glpi_ws_client import GLPI_PAGINATION_LIMIT, GLPI_PAGINATION_DEFAULT
import alignak_webui.app

pid = None
glpi_address = "http://93.93.47.81/plugins/webservices/xmlrpc.php"
# glpi_address = "http://107.191.47.221:5000"

glpi = Glpi(glpi_address)


class test_1_login(unittest2.TestCase):

    def setUp(self):
        print ""

    def tearDown(self):
        print ""

    def test_1_config(self):
        print ''
        print 'test config'

        print "Glpi URL endpoint: %s" % glpi.url_endpoint_root
        print "Glpi pagination limit", GLPI_PAGINATION_LIMIT
        print "Glpi pagination limit", GLPI_PAGINATION_DEFAULT

        assert glpi
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token

    def test_2_refused_connection_backend(self):
        print ''
        print 'test refused connection with username/password'

        glpi.url_endpoint_root = "https://93.93.47.81/plugins/"
        with assert_raises(GlpiException) as cm:
            connection = glpi.login('admin', 'admin')
        ex = cm.exception
        print ex
        assert_true(ex.code == 1001)
        assert_true(ex.message == "Access denied")
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token
        glpi.url_endpoint_root = glpi_address

    def test_2_refused_connection_username(self):
        print ''
        print 'test refused connection with username/password'

        with assert_raises(GlpiException) as cm:
            connection = glpi.login(None, None)
        ex = cm.exception
        print ex
        assert_true(ex.code == 1001)
        assert_true(ex.message == "Missing mandatory parameters")
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token

        with assert_raises(GlpiException) as cm:
            connection = glpi.login('admin', None)
        ex = cm.exception
        print ex
        assert_true(ex.code == 1001)
        assert_true(ex.message == "Missing mandatory parameters")
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token

        with assert_raises(GlpiException) as cm:
            connection = glpi.login(None, 'bad_password')
        ex = cm.exception
        print ex
        assert_true(ex.code == 1001)
        assert_true(ex.message == "Missing mandatory parameters")
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token


        with assert_raises(GlpiException) as cm:
            connection = glpi.login('test_ws', 'fake')
        ex = cm.exception
        print ex
        assert_true(ex.code == 1001)
        assert_true(ex.message == "Login failed (Identifiant ou mot de passe erroné)")
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token

    def test_3_user_login(self):
        print ''
        print 'test login with username/password'

        # Mandatory login to call any method
        with assert_raises(GlpiException) as cm:
            items = glpi.methodCall("glpi.getMyInfo")
        ex = cm.exception
        print ex
        assert_true(ex.code == 1001)
        assert_true(ex.message == "Access denied, please login before calling any method.")


        # Logout without any login is allowed
        assert glpi.logout()


        # Login
        assert glpi.login('test_ws', 'ipm-France2016')
        print 'logged in with username/password'
        assert glpi.connection is not None
        assert glpi.authenticated
        assert glpi.token

        # Logout
        assert glpi.logout()
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token

class test_2_get(unittest2.TestCase):

    def setUp(self):
        print ""
        # Login
        assert glpi.login('test_ws', 'ipm-France2016')
        print 'logged in with username/password'
        assert glpi.connection is not None
        assert glpi.authenticated
        assert glpi.token


    def tearDown(self):
        print ""
        # Logout
        assert glpi.logout()
        assert not glpi.connection
        assert not glpi.authenticated
        assert not glpi.token

    def test_1_user_info(self):
        print ''
        print 'test user information'

        items = glpi.methodCall("glpi.getMyInfo")
        print items
        assert items

    def test_2_getKiosks(self):
        print ''
        print 'test user information'


        items = glpi.methodCall("kiosks.getHosts")
        print items
        assert items
        assert len(items) == GLPI_PAGINATION_DEFAULT

        # Get only count of elements
        parameters = {'count': '1'}
        items = glpi.methodCall("kiosks.getHosts", parameters)
        print items
        assert items
        assert len(items) == 1
        print items[0]
        assert 'kiosks_counter' in items[0]
        print "Kiosks count:", items[0]['kiosks_counter']
        kiosks_count = items[0]['kiosks_counter']

        got_kiosks = 0
        while got_kiosks < kiosks_count:
            parameters = {
                'start': got_kiosks, 'limit': GLPI_PAGINATION_DEFAULT
            }
            glpi_items = glpi.methodCall("kiosks.getHosts", parameters)

            print "Got %d kiosks" % len(glpi_items)
            for item in glpi_items:
                got_kiosks += 1
                print "kiosk: %s" % item['name']

            if len(glpi_items) == 0 or \
               got_kiosks >= kiosks_count:
                break
