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

from alignak_webui.utils.settings import Settings


class TestSettings(unittest2.TestCase):
    def test_found_not_found(self):

        """ Settings - configuration file not found"""

        print('test configuration file')

        # Default configuration - not found because of test directory location !
        print('Search default configuration file ...')
        found_cfg_files = Settings().read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        # Normal use case ... default files and application name ...
        # But ! do not get config object ...
        found_cfg_files = Settings().read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        # Relative file path
        cfg_file = "settings.cfg"
        print('Required configuration file:', cfg_file)
        found_cfg_files = Settings(cfg_file).read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        # Absolute file path
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/settings.cfg"
        print('Required configuration file:', cfg_file)
        found_cfg_files = Settings(cfg_file).read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        # Absolute file path - bad formed file
        cfg_file = os.path.dirname(os.path.abspath(__file__)) + "/test_bad_settings.txt"
        print('Required configuration file:', cfg_file)
        found_cfg_files = Settings(cfg_file).read(None)
        print('Found:', found_cfg_files)
        assert found_cfg_files is None
        found_cfg_files = Settings(cfg_file).read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files is None

    def test_found(self):

        """ Settings - configuration file found"""

        # Relative file path
        cfg_file = "settings.cfg"
        print('Required configuration file:', cfg_file)
        # Normal use case ... default files and application name ...
        # And get config object ...
        app_config = Settings(cfg_file)
        found_cfg_files = app_config.read('Alignak-WebUI')
        print('Found:', found_cfg_files)
        assert found_cfg_files

        print(app_config)
        assert 'about_name' in app_config
        assert app_config['about_name'] == 'Alignak-WebUI'

        # Variable 1 is String 1
        assert 'test_mode' in app_config
        assert app_config['test_mode'] == '1'
        assert isinstance(app_config['test_mode'], basestring)

        # Variable True/true/False/false is boolean
        assert app_config['test_boolean1']
        assert app_config['test_boolean2']
        assert not app_config['test_boolean3']
        assert not app_config['test_boolean4']
