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
import unittest2

from nose import with_setup # optional
from nose.tools import *

import alignak_webui
from alignak_webui.utils.settings import Settings

def setup_module(module):
    print ("") # this is to get a newline after the dots
    print ("setup_module before anything in this file")

def teardown_module(module):
    print ("") # this is to get a newline after the dots
    print ("teardown_module after everything in this file")


class settings_tests(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

    def tearDown(self):
        print ""
        print "tearing down ..."


    def test_1_found_not_found(self):
        print ''
        print 'test configuration file'

        # Default configuration - not found because of test directory location !
        print 'Search default configuration file ...'
        found_cfg_files = Settings().read(None)
        print 'Found:', found_cfg_files
        assert found_cfg_files == None
        ### Normal use case ... default files and application name ...
        # But ! do not get config object ...
        found_cfg_files = Settings().read('Alignak-WebUI')
        print 'Found:', found_cfg_files
        assert found_cfg_files

        # Relative file path
        cfg_file = "settings.cfg"
        print 'Required configuration file:', cfg_file
        found_cfg_files = Settings(cfg_file).read(None)
        print 'Found:', found_cfg_files
        assert found_cfg_files == None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print 'Found:', found_cfg_files
        assert found_cfg_files

        # Absolute file path
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/settings.cfg"
        print 'Required configuration file:', cfg_file
        found_cfg_files = Settings(cfg_file).read(None)
        print 'Found:', found_cfg_files
        assert found_cfg_files == None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print 'Found:', found_cfg_files
        assert found_cfg_files

        # Absolute file path - bad formed file
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/test_settings.py"
        print 'Required configuration file:', cfg_file
        found_cfg_files = Settings(cfg_file).read(None)
        print 'Found:', found_cfg_files
        assert found_cfg_files == None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print 'Found:', found_cfg_files
        assert found_cfg_files == None

    def test_2_found(self):
        print ''

        # Relative file path
        cfg_file = "settings.cfg"
        print 'Required configuration file:', cfg_file
        ### Normal use case ... default files and application name ...
        # And get config object ...
        app_config = Settings(cfg_file)
        found_cfg_files = app_config.read('Alignak-WebUI')
        print 'Found:', found_cfg_files
        assert found_cfg_files

        print app_config
        self.assert_('about_name' in app_config)
        self.assert_(app_config['about_name'] == 'Alignak-WebUI')
