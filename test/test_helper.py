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


from collections import OrderedDict

import os
import time

import unittest2

# Set test mode ...
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])
os.environ['ALIGNAK_WEBUI_LOGGER_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'logging.json')
print("Logger configuration file", os.environ['ALIGNAK_WEBUI_LOGGER_FILE'])

if os.path.exists('/tmp/alignak-webui.log'):
    os.remove('/tmp/alignak-webui.log')

import alignak_webui.app

# from alignak_webui import set_app_config
from alignak_webui.objects.item_timeperiod import TimePeriod
from alignak_webui.objects.item_host import Host
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.settings import Settings

helper = Helper()


class TestDate(unittest2.TestCase):
    def test_print_date(self):
        """ Helper - date """

        now = time.time()

        # Timestamp errors
        s = helper.print_date(None)
        print("Result:", s)
        assert s == 'n/a'

        s = helper.print_date(0)
        print("Result:", s)
        assert s == 'n/a'

        # Now, default format
        s = helper.print_date(now)
        print("Result:", s)

        # Now, specified format
        s = helper.print_date(now, fmt='%Y-%m-%d')
        print("Result:", s)

        s = helper.print_date(now, fmt='%H:%M:%S')
        print("Result:", s)

        # Now, force local specified format
        s = helper.print_date(now, fmt=None)
        print("Result:", s)


class TestDuration(unittest2.TestCase):
    def test_print_duration(self):
        """ Helper - duration """
        now = int(time.time())

        # Timestamp errors
        s = helper.print_duration(None)
        print("Result:", s)
        assert s == 'n/a'
        s = helper.print_duration(0)
        print("Result:", s)
        assert s == 'n/a'

        # Now, default format
        s = helper.print_duration(now)
        print("Result:", s)
        assert s == 'Just now'
        # 2s ago
        s = helper.print_duration(now - 2)
        print("Result:", s)
        assert s == 'Just now'

        # In the past ...
        # 4s ago
        s = helper.print_duration(now - 4)
        print("Result:", s)
        assert s == ' 4s ago'

        # Only the duration string
        s = helper.print_duration(now - 4, duration_only=True)
        print("Result:", s)
        assert s == '4s'

        # Got 2minutes
        s = helper.print_duration(now - 120)
        print("Result:", s)
        assert s == ' 2m ago'

        # Go 2hours ago
        s = helper.print_duration(now - 3600 * 2)
        print("Result:", s)
        assert s == ' 2h ago'

        # Go 2 days ago
        s = helper.print_duration(now - 3600 * 24 * 2)
        print("Result:", s)
        assert s == ' 2d ago'

        # Go 2 weeks ago
        s = helper.print_duration(now - 86400 * 14)
        print("Result:", s)
        assert s == ' 2w ago'

        # Go 2 months ago
        s = helper.print_duration(now - 86400 * 56)
        print("Result:", s)
        assert s == ' 2M ago'

        # Go 1 year ago
        s = helper.print_duration(now - 86400 * 365 * 2)
        print("Result:", s)
        assert s == ' 2y ago'

        # Now a mix of all of this :)
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56)
        print("Result:", s)
        assert s == ' 2M 2w 2d 2h 2m 2s ago'

        # Now with a limit, because here it's just a nightmare to read
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=2)
        print("Result:", s)
        assert s == ' 2M 2w ago'

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=3)
        print("Result:", s)
        assert s == ' 2M 2w 2d ago'

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=4)
        print("Result:", s)
        assert s == ' 2M 2w 2d 2h ago'

        # Now with another limit
        s = helper.print_duration(
            now - 2 - 120 - 3600 * 2 - 3600 * 24 * 2 - 86400 * 14 - 86400 * 56, x_elts=5)
        print("Result:", s)
        assert s == ' 2M 2w 2d 2h 2m ago'

        # Not a timestamp but a duration !
        s = helper.print_duration(2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56,
                                  x_elts=2, duration_only=True, ts_is_duration=True)
        print("Result:", s)
        assert s == '2M 2w'
        s = helper.print_duration(2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56,
                                  x_elts=6, duration_only=True, ts_is_duration=True)
        print("Result:", s)
        assert s == '2M 2w 2d 2h 2m 2s'

        # Return to the future
        # Get the 2s ago
        s = helper.print_duration(now + 2)
        print("Result:", s)
        assert s == 'Very soon'

        s = helper.print_duration(now + 4)
        print("Result:", s)
        assert s == 'in 4s'

        # Go 2 minutes
        s = helper.print_duration(now + 120)
        print("Result:", s)
        assert s == 'in 2m'

        # Go 2 hours ago
        s = helper.print_duration(now + 3600 * 2)
        print("Result:", s)
        assert s == 'in 2h'

        # Go 2 days ago
        s = helper.print_duration(now + 3600 * 24 * 2)
        print("Result:", s)
        assert s == 'in 2d'

        # Go 2 weeks ago
        s = helper.print_duration(now + 86400 * 14)
        print("Result:", s)
        assert s == 'in 2w'

        # Go 2 months ago
        s = helper.print_duration(now + 86400 * 56)
        print("Result:", s)
        assert s == 'in 2M'

        # Go 1 year ago
        s = helper.print_duration(now + 86400 * 365 * 2)
        print("Result:", s)
        assert s == 'in 2y'

        # Now a mix of all of this :)
        s = helper.print_duration(
            now + 2 + 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56)
        print("Result:", s)
        assert s == 'in 2M 2w 2d 2h 2m 2s'

        # Now with a limit, because here it's just a nightmare to read
        s = helper.print_duration(
            now + 2 - 120 + 3600 * 2 + 3600 * 24 * 2 + 86400 * 14 + 86400 * 56, x_elts=2)
        print("Result:", s)
        assert s == 'in 2M 2w'


class TestOnOff(unittest2.TestCase):
    def test_print_on_off(self):
        """ Helper - on/off """

        # Call errors
        s = helper.get_on_off()
        print("Result:", s)
        assert s == '<span title="Disabled" class="fa fa-fw fa-close text-danger"></span>'

        # Status only
        s = helper.get_on_off(False)
        print("Result:", s)
        assert s == '<span title="Disabled" class="fa fa-fw fa-close text-danger"></span>'

        s = helper.get_on_off(True)
        print("Result:", s)
        assert s == '<span title="Enabled" class="fa fa-fw fa-check text-success"></span>'

        # Title
        s = helper.get_on_off(False, 'Title')
        print("Result:", s)
        assert s == '<span title="Title" class="fa fa-fw fa-close text-danger"></span>'

        s = helper.get_on_off(True, 'Title')
        print("Result:", s)
        assert s == '<span title="Title" class="fa fa-fw fa-check text-success"></span>'

        # Message
        s = helper.get_on_off(False, message='Message')
        print("Result:", s)
        assert s == '<span title="Disabled" class="fa fa-fw fa-close text-danger">Message</span>'

        s = helper.get_on_off(True, message='Message')
        print("Result:", s)
        assert s == '<span title="Enabled" class="fa fa-fw fa-check text-success">Message</span>'

        # Title and message
        s = helper.get_on_off(True, title='Title', message='Message')
        print("Result:", s)
        assert s == '<span title="Title" class="fa fa-fw fa-check text-success">Message</span>'

        # Title as array
        s = helper.get_on_off(True, title=['on', 'off'], message='Message')
        print("Result:", s)
        assert s == '<span title="on" class="fa fa-fw fa-check text-success">Message</span>'

        s = helper.get_on_off(False, title=['on', 'off'], message='Message')
        print("Result:", s)
        assert s == '<span title="off" class="fa fa-fw fa-close text-danger">Message</span>'


class TestNavigation(unittest2.TestCase):
    def test_navigation_control(self):
        """ Helper - navigation """

        # Parameters: page, total, start, count, nb_max_items
        s = helper.get_pagination_control('test', 0, 0, 0, 0)
        assert s == [('test', 0, 0, 0, False)]
        s = helper.get_pagination_control('test', 0, 0)
        # Default is 25 elements per page
        assert s == [('test', 0, 25, 0, False)]

        # first page, default pagination: 25 elements/page, 5 pages/sequence
        s = helper.get_pagination_control('test', 1, 0)
        print("Result:", s)
        # At least a global element and a local element ...
        assert len(s) == 2
        # Still the same page
        s = helper.get_pagination_control('test', 25, 0)
        print("Result:", s)
        assert len(s) == 2
        s = helper.get_pagination_control('test', 26, 0)
        print("Result:", s)
        assert len(s) == 3
        s = helper.get_pagination_control('test', 51, 0)
        print("Result:", s)
        assert len(s) == 4
        s = helper.get_pagination_control('test', 76, 0)
        print("Result:", s)
        assert len(s) == 5
        s = helper.get_pagination_control('test', 101, 0)
        print("Result:", s)
        # More than 5 pages ... must have forward controls (2 more elements than expected).
        assert len(s) == 8

        # first page, default pagination: 5 elements/page, 5 pages/sequence
        s = helper.get_pagination_control('test', 1, 0, 5)
        print("Result:", s)
        assert len(s) == 2
        s = helper.get_pagination_control('test', 11, 0, 5)
        print("Result:", s)
        assert len(s) == 4
        # More than 5 pages ... must have forward controls.
        s = helper.get_pagination_control('test', 26, 0, 5)
        print("Result:", s)
        assert len(s) == 8

        # List pages, default pagination: 5 elements/page, 5 pages/sequence
        # More than 5 pages ... must have forward controls.
        s = helper.get_pagination_control('test', 40, 0, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 5, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 10, 5)
        print("Result:", s)
        assert len(s) == 8
        # Current page no more in the page sequence ... must have also backward controls.
        s = helper.get_pagination_control('test', 40, 15, 5)
        print("Result:", s)
        assert len(s) == 10
        s = helper.get_pagination_control('test', 40, 20, 5)
        print("Result:", s)
        assert len(s) == 10
        # Last page is now in the page sequence ... no more forward controls.
        s = helper.get_pagination_control('test', 40, 25, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 30, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 35, 5)
        print("Result:", s)
        assert len(s) == 8
        s = helper.get_pagination_control('test', 40, 40, 5)
        print("Result:", s)
        assert len(s) == 8


class TestSearch(unittest2.TestCase):
    def setUp(self):
        # data_model
        self.data_model = OrderedDict([
            # Global table field
            ('_table',
             {'page_title': 'Hosts table (%d items)', 'searchable': True, 'paginable': True,
              'editable': True, 'visible': True, 'responsive': False, 'orderable': True,
              'selectable': True, 'template_page_title': 'Hosts templates table (%d items)',
              'css': 'display nowrap'}),
            # name field
            ('name', {'regex': True, 'required': True, 'searchable': True,
                       'hint': 'This field is the host name', 'title': 'Host name',
                       'editable': True, 'orderable': True, 'unique': True, 'type': 'string',
                       'empty': False, 'templates_table': True}),
            # ...
            ('ls_state',
             {'hint': 'This field is the host status', 'required': True, 'editable': False,
              'allowed': 'UP,DOWN,UNREACHABLE', 'title': 'Status', 'unique': True,
              'type': 'string', 'empty': False}),
            ('overall_status', {'regex': False,
                                 'hint': 'This field is the real host status, aggregating services status',
                                 'title': 'Overall status', 'editable': False, 'visible': True,
                                 'allowed': 'ok,acknowledged,in_downtime,warning,critical',
                                 'type': 'string'}),

            ('fake', {'default': 'Default value', 'searchable': False, 'type': 'string',
                       'title': 'Fake'}),

            ('_realm',
             {'regex': False, 'resource': 'realm', 'searchable': True, 'title': 'Realm',
              'visible': True, 'allowed': 'inner://realms/list', 'hidden': True,
              'type': 'objectid', 'templates_table': True}),
            ('_is_template',
             {'title': 'Template', 'default': False, 'visible': False, 'hidden': True,
              'type': 'boolean', 'templates_table': True}),
            ('_templates',
             {'regex': False, 'resource': 'host', 'format': 'multiple', 'default': '[]',
              'title': 'Templates', 'visible': False, 'content_type': 'objectid',
              'allowed': 'inner://hosts/templates/list', 'hidden': True, 'type': 'list',
              'templates_table': True}),

            ('_template_fields',
             {'format': 'multiple', 'default': '[]', 'title': 'Template fields',
              'visible': False, 'content_type': 'string', 'hidden': True, 'type': 'list'}),
            ('definition_order',
             {'title': 'Definition order', 'default': '100', 'editable': True,
              'visible': False, 'orderable': True, 'hidden': True, 'type': 'integer',
              'templates_table': True}),
            ('tags',
             {'regex': False, 'format': 'multiple', 'default': '[]', 'title': 'Tags',
              'content_type': 'string', 'allowed': 'inner://hosts/templates/list',
              'type': 'list'}),
            ('alias', {'hidden': True, 'type': 'string', 'title': 'Host alias'}),
            ('business_impact', {'hint': 'Host business impact level', 'default': '2',
                                  'title': 'Business impact', 'allowed_4': 'Very important',
                                  'allowed_5': 'Business critical', 'allowed_0': 'None',
                                  'allowed_1': 'Low', 'allowed_2': 'Normal',
                                  'allowed': '0,1,2,3,4,5', 'type': 'integer',
                                  'allowed_3': 'Important'}),

            # Some more ... removed for test purpose.

            ('ls_last_check', {'editable': False, 'type': 'datetime', 'title': 'Last check'}),
            ('ls_state_type', {'editable': False, 'allowed': 'HARD,SOFT', 'type': 'string',
                                'title': 'State type'}),
            ('ls_state_id',
             {'title': 'State', 'default': '0', 'hint': 'Choose the host state',
              'allowed_3': 'Unreachable', 'editable': False, 'allowed_0': 'Up',
              'allowed_1': 'Down (1)', 'allowed_2': 'Down (2)', 'allowed': '0,1,2,3',
              'type': 'integer'}),
            ('ls_acknowledged',
             {'editable': False, 'type': 'boolean', 'title': 'Acknowledged'}),
            ('ls_downtimed',
             {'editable': False, 'type': 'boolean', 'title': 'In scheduled downtime'}),
            ('ls_output', {'default': 'Output from WebUI', 'editable': False,
                            'hint': 'enter the desired check output', 'type': 'string',
                            'title': 'Output'}),
            ('ls_long_output', {'editable': False, 'type': 'string', 'title': 'Long output'}),
            ('ls_perf_data',
             {'editable': False, 'type': 'string', 'title': 'Performance data'}),
            ('ls_current_attempt',
             {'editable': False, 'type': 'integer', 'title': 'Current attempt'}),
            ('ls_max_attempts',
             {'editable': False, 'type': 'integer', 'title': 'Max attempts'}),
            ('ls_next_check', {'editable': False, 'type': 'integer', 'title': 'Next check'}),
            ('ls_last_state_changed',
             {'editable': False, 'type': 'datetime', 'title': 'Last state changed'}),
            ('ls_last_state',
             {'editable': False, 'allowed': 'OK,WARNING,CRITICAL,UNKNOWN,UP,DOWN,UNREACHABLE',
              'type': 'string', 'title': 'Last state'}),
            ('ls_last_state_type',
             {'editable': False, 'allowed': 'HARD,SOFT', 'type': 'string',
              'title': 'Last state type'}),
            ('ls_latency', {'editable': False, 'type': 'float', 'title': 'Latency'}),
            ('ls_execution_time',
             {'editable': False, 'type': 'float', 'title': 'Execution time'})
        ])

    def test_decode_search_simple(self):
        """Helper - decode_search, simple search"""

        # Empty search
        s = helper.decode_search("", self.data_model)
        print("Result:", s)
        assert s == {}

        # Unknown column search
        s = helper.decode_search("status:search", self.data_model)
        print("Result:", s)
        # A warning log is emitted and result is empty
        assert s == {}

        # Non searchable column search
        s = helper.decode_search("fake:search", self.data_model)
        print("Result:", s)
        # A warning log is emitted and result is empty
        assert s == {}

        # Search a default field (eg. name)
        s = helper.decode_search("test", self.data_model)
        print("Result:", s)
        # Search name with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search and specify field (yet another name) with regex
        s = helper.decode_search("name:test", self.data_model)
        print("Result:", s)
        # Search name with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search and specify field (yet another name) without regex
        s = helper.decode_search("overall_status:test", self.data_model)
        print("Result:", s)
        # Search name with no regex pattern
        assert s == {'overall_status': 'test'}

    def test_decode_search_type(self):
        """Helper - decode_search, typed fields search"""

        # Search a string field
        s = helper.decode_search("name:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search an integer field
        s = helper.decode_search("name:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'name': {'$regex': '.*test.*'}}

        # Search a boolean field
        s = helper.decode_search("_is_template:true", self.data_model)
        assert s == {'_is_template': True}
        s = helper.decode_search("_is_template:1", self.data_model)
        assert s == {'_is_template': True}
        s = helper.decode_search("_is_template:yes", self.data_model)
        assert s == {'_is_template': True}

        s = helper.decode_search("_is_template:false", self.data_model)
        assert s == {'_is_template': False}
        s = helper.decode_search("_is_template:0", self.data_model)
        assert s == {'_is_template': False}
        s = helper.decode_search("_is_template:no", self.data_model)
        assert s == {'_is_template': False}

        # Search an integer field
        s = helper.decode_search("definition_order:test", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("definition_order:1524.12", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("definition_order:1", self.data_model)
        assert s == {'definition_order': 1}
        s = helper.decode_search("definition_order:1524", self.data_model)
        assert s == {'definition_order': 1524}

        # Search a float field
        s = helper.decode_search("ls_latency:test", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("ls_latency:1", self.data_model)
        assert s == {'ls_latency': 1.0}
        s = helper.decode_search("ls_latency:1524.12", self.data_model)
        assert s == {'ls_latency': 1524.12}

        # todo: Missing some tests for objectid, list, ... fields ...

    def test_decode_search_specific(self):
        """Helper - decode_search, specific (livestate, bi, ...) field search"""

        # Search a live state field (eg. ls_output) - can omit the ls_ prefix for the field
        s = helper.decode_search("ls_output:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'ls_output': {'$regex': '.*test.*'}}
        s = helper.decode_search("output:test", self.data_model)
        # Search field with a regex pattern
        assert s == {'ls_output': {'$regex': '.*test.*'}}

        # Search business impact field - can use bi rather than business_impact
        s = helper.decode_search("business_impact:0", self.data_model)
        # Search field with a regex pattern
        assert s == {'business_impact': 0}
        s = helper.decode_search("bi:0", self.data_model)
        # Search field with a regex pattern
        assert s == {'business_impact': 0}

        # Search overall state field - can use is/isnot with a list of allowed values
        s = helper.decode_search("is:ok", self.data_model)
        assert s == {'_overall_state_id': 0}
        s = helper.decode_search("is:acknowledged", self.data_model)
        assert s == {'_overall_state_id': 1}
        s = helper.decode_search("is:in_downtime", self.data_model)
        assert s == {'_overall_state_id': 2}
        s = helper.decode_search("is:warning", self.data_model)
        assert s == {'_overall_state_id': 3}
        s = helper.decode_search("is:critical", self.data_model)
        assert s == {'_overall_state_id': 4}

        s = helper.decode_search("isnot:ok", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 0}}
        s = helper.decode_search("isnot:acknowledged", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 1}}
        s = helper.decode_search("isnot:in_downtime", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 2}}
        s = helper.decode_search("isnot:warning", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 3}}
        s = helper.decode_search("isnot:critical", self.data_model)
        assert s == {'_overall_state_id': {'$ne': 4}}

        s = helper.decode_search("is:unallowed", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}
        s = helper.decode_search("isnot:unallowed", self.data_model)
        # A warning log is emitted and result is empty
        assert s == {}

    def test_decode_search_not(self):
        """Helper - decode_search, not search"""

        # Search field that do not contain a value
        s = helper.decode_search("name:!test", self.data_model)
        # Search name with a regex pattern
        assert s == {'name': {'$regex': '/^((?!test).)*$/'}}

        # Search and specify field (yet another name) without regex
        s = helper.decode_search("overall_status:!test", self.data_model)
        # Search name with no regex pattern
        assert s == {'overall_status': {'$ne': 'test'}}

    def test_decode_search_complex(self):
        """Helper - decode_search, complex search"""

        # Search for several values in name
        s = helper.decode_search("test test2", self.data_model)
        # Search several values with a regex pattern
        assert s == {'$or': [{'name': {'$regex': '.*test.*'}}, {'name': {'$regex': '.*test2.*'}}]}
        # Search for several values in name
        s = helper.decode_search("name:test name:test2", self.data_model)
        # Search several values with a regex pattern
        assert s == {'$or': [{'name': {'$regex': '.*test.*'}}, {'name': {'$regex': '.*test2.*'}}]}

        # Search for several values in live state
        s = helper.decode_search("is:ok is:warning", self.data_model)
        # Search several values in a list
        assert s == {'_overall_state_id': {'$in': [0, 3]}}
        # Search for several values in name
        s = helper.decode_search("is:ok is:warning isnot:critical", self.data_model)
        # Search several values with a regex pattern
        assert s == {'_overall_state_id': {'$in': [0, 3], '$nin': [4]}}


class TestBI(unittest2.TestCase):
    def test_print_business_impact(self):
        """ Helper - business impact """

        # Invalid values
        s = helper.get_html_business_impact(-1, icon=True, text=False)
        print("Result:", s)
        assert s == 'n/a - value'
        s = helper.get_html_business_impact(6, icon=False, text=True)
        print("Result:", s)
        assert s == 'n/a - value'
        s = helper.get_html_business_impact(0, icon=False, text=False)
        print("Result:", s)
        assert s == 'n/a - parameters'

        # Default with stars
        s = helper.get_html_business_impact(0, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"></span><span>&nbsp;</span>'  # No star
        s = helper.get_html_business_impact(1, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span></span><span>&nbsp;</span>'  # 1 star
        s = helper.get_html_business_impact(2, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'  # 2 stars
        s = helper.get_html_business_impact(3, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'# 3 stars
        s = helper.get_html_business_impact(4, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'# 4 stars
        s = helper.get_html_business_impact(5, icon=True, text=False)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;</span>'# 5 stars

        # Default with text
        s = helper.get_html_business_impact(0, icon=False, text=True)
        print("Result:", s)
        assert s == 'None'
        s = helper.get_html_business_impact(1, icon=False, text=True)
        print("Result:", s)
        assert s == 'Low'
        s = helper.get_html_business_impact(2, icon=False, text=True)
        print("Result:", s)
        assert s == 'Normal'
        s = helper.get_html_business_impact(3, icon=False, text=True)
        print("Result:", s)
        assert s == 'Important'
        s = helper.get_html_business_impact(4, icon=False, text=True)
        print("Result:", s)
        assert s == 'Very important'
        s = helper.get_html_business_impact(5, icon=False, text=True)
        print("Result:", s)
        assert s == 'Business critical'

        # Default with icon and text
        s = helper.get_html_business_impact(0, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"></span><span>&nbsp;None</span>'
        s = helper.get_html_business_impact(1, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span></span><span>&nbsp;Low</span>'
        s = helper.get_html_business_impact(2, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Normal</span>'
        s = helper.get_html_business_impact(3, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Important</span>'
        s = helper.get_html_business_impact(4, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Very important</span>'
        s = helper.get_html_business_impact(5, icon=True, text=True)
        print("Result:", s)
        assert s == '<span class="text-default"><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span><span class="fa fa-star"></span></span><span>&nbsp;Business critical</span>'


class TestTP(unittest2.TestCase):
    def test_print_timeperiod(self):
        """ Helper - timeperiod """

        # Invalid values
        s = helper.get_html_timeperiod(None)
        print("Result:", s)
        assert s == ''

        tp = TimePeriod(
            {'_updated': 1465548247, '_total': 5, '_type': 'timeperiod', 'definition_order': 100,
             '_default_date': 0, '_comment': '', 'is_active': True,
             '_name': 'All time default 24x7',
             'dateranges': [{'monday': '00:00-24:00'}, {'tuesday': '00:00-24:00'},
                            {'wednesday': '00:00-24:00'}, {'thursday': '00:00-24:00'},
                            {'friday': '00:00-24:00'}, {'saturday': '00:00-24:00'},
                            {'sunday': '00:00-24:00'}],
             '_alias': '',
             '_links': {
                'self': {'href': 'timeperiod/575a7dd74c988c170e857988', 'title': 'Timeperiod'}
             },
             '_created': 1465548247, 'exclude': [],
             '_status': 'unknown',
             '_id': '575a7dd74c988c170e857988',
             '_etag': 'e9f5fb031b79f9abdc42f44d413f8220c321767b', 'imported_from': ''})
        s = helper.get_html_timeperiod(tp)
        print("Result:", s)
        assert s == '<button class="btn btn-default btn-xs btn-block" type="button" data-toggle="collapse" data-target="#html_tp_575a7dd74c988c170e857988" aria-expanded="false" aria-controls="html_tp_575a7dd74c988c170e857988">All time default 24x7</button><div class="collapse" id="html_tp_575a7dd74c988c170e857988"><div class="well"><ul class="list-group"><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;monday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;tuesday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;wednesday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;thursday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;friday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;saturday - 00:00-24:00</li><li class="list-group-item"><span class="fa fa-hourglass">&nbsp;sunday - 00:00-24:00</li></ul></div></div>'


class TestHtmlList(unittest2.TestCase):
    def test_html_list(self):
        """ Helper - HTML list """

        self.maxDiff = None

        # Empty list
        s = helper.get_html_item_list('id', 'type', [])
        print("Result:", s)
        assert s == ''

        # Less than 3 items
        s = helper.get_html_item_list('id', 'type', ['1', '2'])
        print("Short list:", s)
        assert s == '1, 2'

        # Default
        s = helper.get_html_item_list('id', 'type', ['1', '2', '3', '4'])
        print("Result:", s)
        assert s == \
                         '<button class="btn btn-xs btn-raised" ' \
                         'data-toggle="collapse" data-target="#list_type_id" aria-expanded="false">' \
                         'type' \
                         '</button>' \
                         '<div class="collapse" id="list_type_id">' \
                         '<ul class="list-group">' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;1</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;2</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;3</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;4</span></li>' \
                         '</ul>' \
                         '</div>'

        # Default
        s = helper.get_html_item_list('id', 'type', ['1', '2', '3', '4'], 'title')
        print("Result:", s)
        assert s == \
                         '<button class="btn btn-xs btn-raised" ' \
                         'data-toggle="collapse" data-target="#list_type_id" aria-expanded="false">' \
                         'title' \
                         '</button>' \
                         '<div class="collapse" id="list_type_id">' \
                         '<ul class="list-group">' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;1</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;2</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;3</span></li>' \
                         '<li class="list-group-item"><span class="fa fa-check">&nbsp;4</span></li>' \
                         '</ul>' \
                         '</div>'


class TestObjectUrls(unittest2.TestCase):
    def test_notes_url(self):
        """ Helper - get_element_notes_url """

        host = Host({
            '_id': '575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
        })
        assert host

        html_notes = Helper.get_element_notes_url(host, default_title="Note", default_icon="tag")
        # Empty list when no notes exist
        assert html_notes == []

        host = Host({
            '_id': '575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
            'notes': 'note simple|Libellé::note avec un libellé|KB1023,,tag::<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa. Vestibulum id tincidunt lacus. Ut in arcu at ex egestas vestibulum eu non sapien. Nulla facilisi. Aliquam non blandit tellus, non luctus tortor. Mauris tortor libero, egestas quis rhoncus in, sollicitudin et tortor.|note simple|Tag::tagged note ...',
            'notes_url': 'http://www.my-KB.fr?host=$HOSTADDRESS$|http://www.my-KB.fr?host=$HOSTNAME$',
        })
        assert host

        html_notes = Helper.get_element_notes_url(host, default_title="Note", default_icon="tag")
        # 5 declared notes, but only 2 URLs
        # Expecting 5 links
        assert html_notes == [
            '<a href="http://www.my-KB.fr?host=$HOSTADDRESS$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="note simple" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Note</a>',
            '<a href="http://www.my-KB.fr?host=$HOSTNAME$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="note avec un libellé" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Libellé</a>',
            '<a href="#" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa. Vestibulum id tincidunt lacus. Ut in arcu at ex egestas vestibulum eu non sapien. Nulla facilisi. Aliquam non blandit tellus, non luctus tortor. Mauris tortor libero, egestas quis rhoncus in, sollicitudin et tortor." data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;KB1023</span></a>',
            '<a href="#" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="note simple" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Note</span></a>',
            '<a href="#" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="tagged note ..." data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Tag</span></a>'
        ]

    def test_actions_url(self):
        """ Helper - get_element_notes_url """

        host = Host({
            '_id': '575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
        })
        assert host

        html_actions = Helper.get_element_actions_url(host, default_title="Url", default_icon="globe")
        assert html_actions == []

        host = Host({
            '_id': '575a7dd74c988c170e857988',
            '_status': 'OK',
            'name': 'test',
            '_created': 1470995433,
            '_updated': 1470995450,
            'action_url': 'http://www.google.fr|url1::http://www.google.fr|My KB,,tag::http://www.my-KB.fr?host=$HOSTNAME$|Last URL,,tag::<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa.,,http://www.my-KB.fr?host=$HOSTADDRESS$',
        })
        assert host

        html_actions = Helper.get_element_actions_url(host, default_title="Url", default_icon="globe")
        # 3 declared actions, with different parameters
        # Expecting 3 links
        assert html_actions == [
            '<a href="http://www.google.fr" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="No description provided" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-globe"></span>&nbsp;Url</a>', '<a href="http://www.google.fr" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="No description provided" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-globe"></span>&nbsp;url1</a>',
            '<a href="http://www.my-KB.fr?host=$HOSTNAME$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="No description provided" data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;My KB</a>',
            '<a href="http://www.my-KB.fr?host=$HOSTADDRESS$" target="_blank" role="button" data-toggle="popover urls" data-container="body" data-html="true" data-content="<strong>Lorem ipsum dolor sit amet</strong>, consectetur adipiscing elit. Proin et leo gravida, lobortis nunc nec, imperdiet odio. Vivamus quam velit, scelerisque nec egestas et, semper ut massa." data-trigger="hover focus" data-placement="bottom"><span class="fa fa-tag"></span>&nbsp;Last URL</a>'
        ]
