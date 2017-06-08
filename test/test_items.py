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
import logging
import time
from calendar import timegm
from datetime import datetime
import unittest2
import pytest

# Set test mode ... application is tested in production mode!
os.environ['ALIGNAK_WEBUI_DEBUG'] = '1'
os.environ['ALIGNAK_WEBUI_TEST'] = '1'
os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'] = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg')
print("Configuration file", os.environ['ALIGNAK_WEBUI_CONFIGURATION_FILE'])

import alignak_webui.app

from alignak_webui import get_app_config, set_app_config
from alignak_webui.objects.element import BackendElement
from alignak_webui.objects.item_command import Command
from alignak_webui.objects.item_host import Host
from alignak_webui.objects.item_service import Service
from alignak_webui.objects.element_state import ElementState
from alignak_webui.objects.item_user import User
from alignak_webui.utils.settings import Settings

loggerDm = logging.getLogger('alignak_webui.objects.element')
loggerDm.setLevel(logging.DEBUG)
loggerDm = logging.getLogger('alignak_webui.objects.backend')
loggerDm.setLevel(logging.DEBUG)


class TestClassElements(unittest2.TestCase):
    def test_class(self):
        """ Items - class variables """
        print("--- test class variables")

        # Create basic object
        # Bad parameters
        with pytest.raises(ValueError) as excinfo:
            item = BackendElement(1)
        assert str(excinfo.value) == "item.__new__: object parameters must be a dictionary!"

        # Declaration without any parameter is allowed
        item = BackendElement()
        print(item)
        print(item.__dict__)
        print(item.__class__._cache)
        assert len(item.__class__._cache) == 1
        assert item.__class__._count == 1
        # _id is created if it does not exist ...
        assert '_id' in item.__dict__
        # ... but it is for the _id==0 object!
        assert isinstance(item.__dict__['_id'], basestring)
        assert item.__dict__['_id'] == 'item_0'

        # Declaration without any parameter is allowed
        item = BackendElement()
        print(item)
        print(item.__dict__)
        print(item.__class__._cache)
        assert len(item.__class__._cache) == 1
        assert item.__class__._count == 1
        # _id is created if it does not exist ...
        assert '_id' in item.__dict__
        # ... but it is for the _id==0 object!
        assert isinstance(item.__dict__['_id'], basestring)
        assert item.__dict__['_id'] == 'item_0'

        # New declaration with _id in args
        item2 = BackendElement({'_id': 0})
        print("---")
        print(item2)
        print(item2.__dict__)
        assert isinstance(item2.__dict__['_id'], basestring)  # Even if _id was an int!
        assert item2.__dict__['_id'] == 'item_0'
        print(item2.__class__._cache)
        assert len(item.__class__._cache) == 1
        assert item == item2
        # Both objects are the same ... because _id and mandatory fields is the same!

        # New declaration with different parameters in kwargs
        item3 = BackendElement(params={'_id': '0', 'new_param': 1})
        print(item3.__dict__)
        assert item3.__dict__['_id'] == 'item_0'
        print(item3.__class__._cache)
        print(item.__class__._cache)
        assert item3.__class__._cache == item.__class__._cache
        print("cache ---")
        for k, v in item.__class__._cache.items():
            print(k, v)
        print("---")
        assert len(item.__class__._cache) == 1
        assert item == item3

        # New object because not the same id ...
        item3 = BackendElement(params={'_id': 1, 'new_param': 1})
        print(item3.__class__._cache)
        print("cache ---")
        for k, v in item.__class__._cache.items():
            print(k, v)
        print("---")
        assert len(item.__class__._cache) == 2
        assert item.__class__._count == 2
        assert item != item3
        # Different objects because different id !

        # Default class variables
        auto_id = item.__class__._next_id
        assert item.__class__._next_id == 1  # First auto object id is 1
        print(item.__class__._next_id)
        item = BackendElement()
        assert item.__class__._next_id == 1  # Still the same ...
        assert BackendElement().__class__._next_id == 1
        # id is not incremented because of empty parameters
        print("cache ---")
        for k, v in item.__class__._cache.items():
            print(k, v)
        print("---")
        assert len(item.__class__._cache) == 2
        assert item.__class__._count == 2
        item = BackendElement()
        print(item.__class__._cache)
        assert len(item.__class__._cache) == 2  # No new objects because no parameters
        assert BackendElement().__class__._default_date == 0
        assert BackendElement().__class__._type == 'item'
        print(item.__class__._cache)
        assert len(item.__class__._cache) == 2
        assert BackendElement().__class__.items_states == [
            "ok", "warning", "critical", "unknown", "not_executed"
        ]

        # New auto id objects
        print("----------")
        auto_id = item.__class__._next_id
        assert item.__class__._next_id == 1
        item = BackendElement(params={'param': '0', 'new_param': 1})
        print(item.__dict__)
        assert item.__dict__['_id'] == 'item_1'  # auto id is prefixed with item type
        assert item.__dict__['param'] == '0'  # parameter set
        assert item.__dict__['new_param'] == 1  # parameter set
        print("cache ---")
        for k, v in item.__class__._cache.items():
            print(k, v)
        print("---")
        print(item.__class__._cache['0'])
        print(item.__class__._cache['1'])
        print(item.__class__._cache['item_1'])
        print("---")
        print(item.__class__._cache)
        assert len(item.__class__._cache) == 3
        assert item.__class__._count == 3

        # Same objects because same id ...
        print("----------")
        item2 = BackendElement(params={'_id': 'item_1', 'new_param': 2})
        print(item2.__dict__)
        assert item2.__dict__['_id'] == 'item_1'
        assert item2.__dict__['param'] == '0'       # parameter not changed
        assert item2.__dict__['new_param'] == 2     # parameter changed
        assert len(item.__class__._cache) == 3
        assert item.__class__._count == 3
        assert item == item2

    def test_cache(self):
        """ Items - cache """
        print("--- test class cache")

        # Clean generic Item cache and reset counter to 0
        BackendElement.clean_cache()

        # Create basic object
        # Declaration without any parameter is allowed
        item = BackendElement()
        print("--- cache:")
        print(BackendElement.get_cache())
        assert len(BackendElement.get_cache()) == 1
        assert BackendElement.get_type() == 'item'
        assert BackendElement.get_count() == 1

        # New declaration with _id in args
        item2 = BackendElement({'_id': 0})
        assert item == item2
        # Both objects are the same ... because _id and mandatory fields is the same!
        print("--- cache:")
        print(BackendElement.get_cache())
        assert len(BackendElement.get_cache()) == 1
        assert BackendElement.get_count() == 1

        # New declaration with different parameters in kwargs
        item3 = BackendElement(params={'_id': '0', 'new_param': 1})
        assert item == item3
        print("--- cache:")
        print(BackendElement.get_cache())
        assert len(BackendElement.get_cache()) == 1
        assert BackendElement.get_count() == 1

        # New object because not the same id ...
        item3 = BackendElement(params={'_id': 1, 'new_param': 1})
        assert item != item3
        # Different objects because different id !
        print("--- cache:")
        print(BackendElement.get_cache())
        assert len(BackendElement.get_cache()) == 2
        assert BackendElement.get_count() == 2

        # Delete objects
        item3._delete()
        print("--- cache:")
        print(BackendElement.get_cache())
        assert len(BackendElement.get_cache()) == 1
        assert BackendElement.get_count() == 1


class TestElementStates(unittest2.TestCase):
    def setUp(self):
        print("setting up ...")
        # Application configuration is loaded
        self.config = get_app_config()
        assert self.config

    def test_items_states(self):
        """ Items - states """

        items_states = ElementState()
        assert items_states.object_types_states
        assert items_states.default_states
        assert items_states.states
        print("Objects types and states", items_states.object_types_states)
        print("Default states", items_states.default_states)
        print("Items states", items_states.states)

        for s in self.config:
            print(s)
            s = s.split('.')
            if s[0] not in ['items', 'bottle'] and len(s) > 1:
                assert s[1] not in items_states.object_types_states
                assert s[1] not in items_states.default_states
                assert s[1] not in items_states.states
            else:
                if s[0] not in ['items']:
                    continue
                print(s)
                if s[1] == 'item':
                    assert s[1] not in items_states.object_types_states
                    assert s[1] not in items_states.states
                    if len(s) > 2:
                        assert s[2] in items_states.default_states
                else:
                    assert s[1] not in items_states.default_states

                    if s[1] in ['content', 'back', 'front', 'badge']:
                        assert s[1] not in items_states.object_types_states
                        assert s[1] not in items_states.states
                        continue

                    assert s[1] in items_states.object_types_states
                    assert s[1] in items_states.states

                    if len(s) > 2:
                        assert s[2] in items_states.object_types_states[s[1]]
                        assert s[2] in items_states.states[s[1]]
                        print(s[1], items_states.states[s[1]])

    def test_items_states_2(self):
        """ Items - states (2) """

        items_states = ElementState()
        assert items_states.object_types_states
        assert items_states.default_states
        assert items_states.states
        print("Objects types and states", items_states.object_types_states)
        print("Default states", items_states.default_states)
        print("Items states", items_states.states)

        assert items_states.get_objects_types()
        print("All objects types : ", items_states.get_objects_types())

        assert items_states.get_icon_states()
        print("All objects : ", items_states.get_icon_states())

        assert items_states.get_default_states()
        print("Default states : ", items_states.get_default_states())

        # Objects known states
        for object_type in items_states.object_types_states:
            assert items_states.get_icon_states(object_type)
            print(object_type, ", all states: ", items_states.get_icon_states(object_type))
            for state in items_states.get_icon_states(object_type):
                assert items_states.get_icon_state(object_type, state)
                print(object_type, ", state: ", state, ": ", items_states.get_icon_state(
                    object_type, state))

        assert not items_states.get_icon_state(None, None)

        # Default states are in all objects types
        for state in items_states.get_default_states():
            print("Default state: ", state)
            for object_type in items_states.object_types_states:
                assert items_states.get_icon_states(object_type)

    def test_html_states(self):
        """ Items - HTML states """

        self.maxDiff = None

        items_states = ElementState()
        assert items_states.object_types_states
        assert items_states.default_states
        assert items_states.states

        # Objects known states
        save_object_type = 'user'
        for object_type in items_states.object_types_states:
            print("Html for: ", object_type)
            for state in items_states.get_icon_states(object_type):
                if state == 'state_view':
                    continue

                elt = BackendElement({
                    '_id': '0', 'status': state
                })
                print("Html for:", object_type, ", object:", elt)
                assert items_states.get_html_state(object_type, elt)
                print("Html : ", items_states.get_html_state(object_type, elt))

        # Unknown states
        print("States for: fake")
        print(items_states.get_icon_states('fake'))
        assert not items_states.get_icon_states('fake')

        print("Html for:", save_object_type, ", state: fake")
        print("Unknown state")
        elt = BackendElement({
            '_id': '0', 'status': 'fake'
        })
        print(items_states.get_html_state(save_object_type, elt))
        assert items_states.get_html_state(save_object_type, elt) == 'n/a - status: fake'

        print("Html for: fake, state: unknown")
        print("Unknown object type")
        elt = BackendElement({
            '_id': '0', 'status': 'unknown'
        })
        # Unknown object_type provides a default user html state ...
        item_state = items_states.get_html_state('fake', elt)
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="fake" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % elt.id

        # Bad parameters
        print("No icon/text")
        item_state = items_states.get_html_state(save_object_type, elt, icon=False, text='')
        print(item_state)
        assert item_state == 'n/a - icon/text'

        print("Default icon/text")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True, text='')
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % elt.id

        # Other parameters
        print("Default icon/text - disabled")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True, text='',
                                                 disabled=True)
        print(item_state)
        assert item_state == \
                         '''<div class="item-state text-muted " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x text-muted"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % elt.id

        print("Default icon/text - title and default text")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True,
                                                 title='Test title')
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title="Test title"><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % elt.id

        print("Default icon/text - title without text")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True, text=None,
                                                 title='Test title')
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title="Test title"><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % elt.id

        print("Default icon/text - not title and default text")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True, text='Test')
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>Test</span></div>''' % elt.id

        print("Default icon/text - not title and text")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True,
                                                 text='Test text')
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>Test text</span></div>''' % elt.id

        print("Default icon/text - extra")
        item_state = items_states.get_html_state(save_object_type, elt, icon=True, text='',
                                                 extra='test')
        print(item_state)
        assert item_state == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title="testtest"><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % elt.id


class TestItems(unittest2.TestCase):
    def setUp(self):
        print("setting up ...")
        # Application configuration is loaded
        self.config = get_app_config()
        assert self.config
        self.maxDiff = None

    def test_items(self):
        """ Items - items """
        print("--- test Item")

        # Clean generic Item cache and reset counter to 0
        BackendElement.clean_cache()

        # Base item with parameters, including identifier
        parameters = {'_id': 'test_id', 'foo': 'bar', 'foo_int': 1}
        item = BackendElement(parameters)
        print(item.__dict__)
        assert item._id == 'test_id'
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.name == 'anonymous'

        # Same object
        parameters = {'_id': 'test_id', 'foo': 'bar', 'foo_int': 1}
        item2 = BackendElement(parameters)
        print("item2", item2.__dict__)
        assert item2._id == 'test_id'
        assert item2.foo == 'bar'
        assert item2.foo_int == 1
        assert item.name == 'anonymous'
        assert item.alias == 'anonymous'
        assert item.json_alias == 'anonymous'
        assert item.notes == ''

        # Same objects!
        assert item == item2

        # New object
        parameters = {'_id': 'test_id2', 'foo': 'baz', 'foo_int': 9}
        item3 = BackendElement(parameters)
        print(item3.__dict__)
        assert item3._id == 'test_id2'
        assert item3.foo == 'baz'
        assert item3.foo_int == 9

        # Different objects!
        assert item != item3
        assert item2 != item3

        # Update object from a dict
        # item._update({'foo': 'bar', 'foo_int': 1})
        # assert item.foo == 'bar'
        # assert item.foo_int == 1
        # Still true ... so different
        # assert item != item3
        # assert item2 != item3

        # Update object from an object
        # item._update(item3)
        # assert item._id == 'test_id2'
        # assert item.foo == 'baz'
        # assert item.foo_int == 9
        # Still true ... so different
        # assert item != item3
        # assert item2 != item3

        # Base item with dates
        # Accept dates as:
        # - float (time.now()) as timestamp
        # - formatted string as '%a, %d %b %Y %H:%M:%S %Z' (Tue, 01 Mar 2016 14:15:38 GMT)
        # Parameters which name ends with date are considered as dates.
        # _created and _updated parameters also.
        # Default date used is 0 (epoch)
        now = datetime.now()
        now_time = time.time()
        parameters = {
            'foo': 'bar', 'foo_int': 1,
            'foo_date': '2016-04-01',  # Invalid string formet
            'epoch_date': 0,  # Valid timestamp date (integer)
            'now_date': now,  # Valid timestamp date (time tuple)
            'now_time_date': now_time,  # Valid timestamp date time (integer)
            '_created': 'Tue, 01 Mar 2016 14:15:38 GMT',  # Valid string format
            '_updated': 'Tue, 01 Mar 2016 14:15:38 XX'  # Invalid string format => default date
        }
        item = BackendElement(parameters)
        print(item.__dict__)
        assert item._id == 'item_1'
        assert item.id == 'item_1'
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.foo_date == item._default_date
        assert item.foo_date == item.__class__._default_date
        assert item.epoch_date == 0
        assert item.now_time_date == now_time
        assert item.now_date == timegm(now.timetuple())
        assert item._created == 1456841738
        assert item._updated == 0
        assert item._updated == item._default_date
        assert item._updated == item.__class__._default_date

        # Base item with dates, specific format and error cases
        now = datetime.now()
        parameters = {
            'foo': 'bar', 'foo_int': 1,
            'foo_date': '2016-04-01 10:58:12',  # Valid string formet
            'now_date': now,  # Valid timestamp date
            '_created': None,  # Invalid string format => default date
            '_updated': 'Tue, 01 Mar 2016 14:15:38 GMT'  # Invalid string format
        }
        item = BackendElement(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print(item.__dict__)
        assert item._id == 'item_2'
        assert item.id == 'item_2'
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.foo_date == 1459508292
        assert item.now_date == timegm(now.timetuple())
        assert item._created == 0
        assert item._updated == 0

        # Base item update
        now = datetime.now()
        parameters = {
            'foo': 'bar2', 'foo_int': 2,
            'foo_date': '2016-04-01 10:58:13',
            'ts_date': 1459508293,
            'now_date': now,
            'fake_date': None,
            '_updated': 'Tue, 01 Mar 2016 14:15:38 XX'  # Invalid string format => default date
        }
        # item._update(parameters, date_format='%Y-%m-%d %H:%M:%S')
        # print(item.__dict__)
        # self.assertEqual(item._id, 'item_2')  # Still the same object
        # self.assertEqual(item.id, 'item_2')
        # self.assertEqual(item.foo, 'bar2')
        # self.assertEqual(item.foo_int, 2)
        # self.assertEqual(item.ts_date, 1459508293)
        # self.assertEqual(item.foo_date, 1459508293)
        # self.assertEqual(item.now_date, timegm(now.timetuple()))
        # self.assertEqual(item.fake_date, 0)
        # self.assertEqual(item.alias, item.name)
        # self.assertEqual(item.notes, '')

        # Base item methods
        now = datetime.now()
        parameters = {
            'alias': 'Item alias',
            'notes': 'Item notes',
            'foo': 'bar', 'foo_int': 1,
            'foo_date': '2016-04-01 10:58:13',
            'now_date': now,
            'dict_param': {
                'param1': 1,
                'param2': '2'
            }
        }
        item = BackendElement(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print(item.__dict__)
        assert item._id == 'item_3'  # New object
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.foo_date == 1459508293
        assert item.now_date == timegm(now.timetuple())
        assert item.dict_param
        print(item.dict_param)
        assert item.dict_param['param1'] == 1
        assert item.dict_param['param2'] == '2'

        assert item.name == 'anonymous'
        assert item.alias == 'Item alias'
        assert item.notes == 'Item notes'
        assert item.status == 'unknown'

        # Alias containing specific character
        now = datetime.now()
        parameters = {
            'alias': 'Item "alias"',
            'notes': 'Item notes',
            'foo': 'bar', 'foo_int': 1,
            'foo_date': '2016-04-01 10:58:13',
            'now_date': now,
            'dict_param': {
                'param1': 1,
                'param2': '2'
            }
        }
        item = BackendElement(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print(item.__dict__)
        assert item._id == 'item_4'  # New object
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.foo_date == 1459508293
        assert item.now_date == timegm(now.timetuple())
        assert item.dict_param
        print(item.dict_param)
        assert item.dict_param['param1'] == 1
        assert item.dict_param['param2'] == '2'

        assert item.name == 'anonymous'
        assert item.alias == 'Item "alias"'
        assert item.json_alias == 'Item \\"alias\\"'
        assert item.notes == 'Item notes'
        assert item.status == 'unknown'

        # Alias containing specific character (bis)
        now = datetime.now()
        parameters = {
            'alias': "Item 'alias'",
            'notes': 'Item notes',
            'foo': 'bar', 'foo_int': 1,
            'foo_date': '2016-04-01 10:58:13',
            'now_date': now,
            'dict_param': {
                'param1': 1,
                'param2': '2'
            }
        }
        item = BackendElement(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print(item.__dict__)
        assert item._id == 'item_5'  # New object
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.foo_date == 1459508293
        assert item.now_date == timegm(now.timetuple())
        assert item.dict_param
        print(item.dict_param)
        assert item.dict_param['param1'] == 1
        assert item.dict_param['param2'] == '2'

        assert item.name == 'anonymous'
        assert item.alias == "Item 'alias'"
        assert item.json_alias == "Item \\'alias\\'"
        assert item.notes == 'Item notes'
        assert item.status == 'unknown'

    def test_users(self):
        """ Items - users"""
        print("--- test User")

        # Global (Item) objects count
        global_objects_count = BackendElement().get_count()
        print(global_objects_count, "objects")
        print("--- cache:")
        print(User.get_cache())

        # Base item
        User.clean_cache()
        item = User()
        assert item
        print("--- cache:")
        print(User.get_cache())
        assert len(User.get_cache()) == 1

        # Specific (User) objects count and cache
        user_objects_count = item._count
        print(user_objects_count, " User objects")
        print(item._cache)

        # Global objects count and cache did not changed
        assert global_objects_count == BackendElement().get_count()
        assert len(BackendElement().get_cache()) == global_objects_count
        # Only 1 User object
        assert item._count == 1
        assert len(User.get_cache()) == 1

        print(item)
        assert "%s" % item == "<user, id: user_0, name: anonymous, role: user>"
        assert item._id == 'user_0'  # Because no _id in the parameters ...
        assert item._type == 'user'
        assert item.name == 'anonymous'
        assert item.status == 'unknown'

        assert item.role == 'user'
        assert item.can_submit_commands == False
        assert item.picture == '/static/images/user_guest.png'
        assert item.authenticated == False
        assert item.widgets_allowed == False
        assert item.is_admin == False

        assert item.get_role() == 'user'
        assert item.get_role(display=True) == 'User'
        assert item.is_administrator() == False
        assert item.is_anonymous() == True
        assert item.can_submit_commands == False
        assert item.can_change_dashboard() == False
        assert item.picture == '/static/images/user_guest.png'

        print(item.get_html_state())
        assert item.get_html_state() == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % item._id

        item = User({
            'name': 'test',
            'password': 'test',
            'is_admin': False,
            'widgets_allowed': True,
            'can_submit_commands': True,
            'email': 'test@gmail.com',
            'lync': 'test@lync.com',
            'token': 'token'
        })
        assert item._id == 'user_1'  # Not 0 because parameters are provided but auto generated because no _id in the parameters!

        assert item.get_role() == 'power'
        assert item.get_role(display=True) == 'Power user'
        assert item.is_administrator() == False
        assert item.is_anonymous() == False
        assert item.is_power() == True
        assert item.can_change_dashboard() == False # Because default skill_level is 0
        item.skill_level = 1
        assert item.can_change_dashboard() == True
        assert item.picture == '/static/images/user_default.png'
        assert item.token == 'token'

        print(item.get_html_state())
        assert item.get_html_state() == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="test" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % item._id

        item = User({
            'name': 'test',
            'user_name': 'test',
            'friendly_name': 'Friendly name',
            'password': 'test',
            'is_admin': True,
            'skill_level': 2
        })
        assert item._id == 'user_2'  # Not 0 because parameters are provided but auto generated because no _id in the parameters!

        assert item.name == 'test'
        assert item.friendly_name == 'Friendly name'
        assert item.get_role() == 'administrator'
        assert item.get_role(display=True) == 'Administrator'
        assert item.is_administrator() == True
        assert item.is_anonymous() == False
        assert item.is_power() == True
        assert item.can_change_dashboard() == True
        assert item.picture == '/static/images/user_admin.png'

        print(item.get_html_state())
        assert item.get_html_state() == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="test" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % item._id

        item = User({
            'username': 'test_priority',
            'name': 'test',
            'alias': 'Real name',
            'password': 'test',
            'is_admin': False,
            'widgets_allowed': '0',
            'can_submit_commands': False
        })
        print(item.__dict__)

        assert item.name == 'test'
        assert item.alias == 'Real name'
        assert item.get_username() == 'test_priority'
        assert item.get_role() == 'user'
        assert item.get_role(display=True) == 'User'
        assert item.is_administrator() == False
        assert item.is_anonymous() == False
        assert item.is_power() == False
        assert item.can_change_dashboard() == False
        assert item.picture == '/static/images/user_default.png'

        print("State: ", item.get_html_state())
        assert item.get_html_state() == \
                         '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="Real name" data-item-type="user" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % item._id

        item = User({
            'username': 'test_priority',
            'name': 'test',
            'alias': 'Aliased name',
            'password': 'test',
            'is_admin': False,
            'can_submit_commands': '0'
        })
        assert item.name == 'test'
        assert item.alias == 'Aliased name'
        assert item.get_username() == 'test_priority'
        assert item.is_power() == False
        assert item.can_change_dashboard() == False
        # Update with a new obect declaration
        item = User({
            '_id': item._id,
            'alias': 'Aliased name (bis)',
            'is_admin': True,
            'skill_level': 2
        })
        assert item.alias == 'Aliased name (bis)'
        assert item.get_username() == 'test_priority'
        assert item.is_power() == True
        assert item.can_change_dashboard() == True
        # Update calling _update
        # item._update({
            # 'alias': 'Aliased name (bis)',
            # 'is_admin': True
        # })
        # assert item.alias == 'Aliased name (bis)'
        # assert item.get_username() == 'test_priority'
        # assert item.is_power() == True
        # assert item.can_change_dashboard() == True

    def test_commands(self):
        """ Items - commands"""
        print("--- test Command")

        # Global (Item) objects count
        global_objects_count = BackendElement().get_count()
        print(global_objects_count, "objects")
        print(BackendElement().get_cache())

        # Base item
        Command.clean_cache()
        item = Command()
        print(item.__dict__)
        print(item)
        assert item
        assert len(Command.get_cache()) == 1

        # Specific (Command) objects count and cache
        user_objects_count = Command.get_count()
        print(user_objects_count, " Command objects")
        print(item._cache)
        assert user_objects_count == 1

        # Global objects count and cache did not changed
        assert global_objects_count == BackendElement().get_count()
        assert len(BackendElement().get_cache()) == global_objects_count
        # Only 1 User object
        assert item._count == 1
        assert len(item._cache) == 1
        assert len(Command.get_cache()) == 1

        print(item)
        assert "%s" % item == "<command, id: command_0, name: Undefined command, status: unknown>"
        assert item._id == 'command_0'  # Because no _id in the parameters ...
        assert item._type == 'command'
        assert item.name == 'Undefined command'
        assert item.status == 'unknown'

        assert item.status == 'unknown'

        print(item.get_html_state())
        assert item.get_html_state() == '''<div class="item-state item_command " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="Undefined command" data-item-type="command" data-item-state="" title=""><span class="fa-stack " ><i class="fa fa-circle fa-stack-2x item_command"></i><i class="fa fa-bolt fa-stack-1x fa-inverse"></i></span><span></span></div>''' % item.id

    def test_hosts(self):
        """ Items - hosts """
        print("--- test Host")

        # Global (Item) objects count
        global_objects_count = BackendElement().get_count()
        print(global_objects_count, "objects")
        print("Global cache: ", BackendElement().get_cache())

        # Base item
        Host.clean_cache()
        item = Host()
        print(item.__dict__)
        print(item)
        assert item

        # Specific (Session) objects count and cache
        user_objects_count = item._count
        print(user_objects_count, " Host objects")
        print("Host cache: ", item._cache)

        # Global objects count and cache did not changed
        assert global_objects_count == BackendElement().get_count()
        print("Global cache: ", BackendElement().get_cache())
        assert len(BackendElement().get_cache()) == global_objects_count
        # Only 1 Session object
        assert item._count == 1
        assert len(item._cache) == 1

        print(item)
        print(item.__dict__)
        # status is None because there is no status_property defined
        assert "%s" % item == "<host, id: host_0, name: anonymous, status: None>"
        assert item._id == 'host_0'
        assert item._type == 'host'
        assert item.name == 'anonymous'
        assert item.status is None

        item = Host()
        print(item.__dict__)
        assert item._id == 'host_0'

        # Host item with dates
        now = datetime.now()
        item = Host({
            'name': 'test',
            'ls_last_check': now
        })
        print(item.__dict__)
        print(now)
        print(item.get_last_check(timestamp=True))
        assert item._id == 'host_1'
        assert item.get_last_check(timestamp=True) == timegm(now.timetuple())

        # Host item update
        time.sleep(1)
        now2 = datetime.now()
        item = Host({
            'name': 'test',
            'last_check': now,
            '_created': 1470995433,
            '_updated': 1470995450,
            'notes': 'Host notes'
        })
        print(item.created)
        print(item.updated)
        print(item.get_date(item.created))
        assert item.get_date(item.created) == '2016-08-12 11:50:33'

    def test_services(self):
        """ Items - services """
        print("--- test Service")

        # Global (Item) objects count
        global_objects_count = BackendElement().get_count()
        print(global_objects_count, "objects")
        print("Global cache: ", BackendElement().get_cache())

        # Base item
        Service.clean_cache()
        item = Service()
        print(item.__dict__)
        print(item)
        assert item

        # Specific (Session) objects count and cache
        user_objects_count = item._count
        print(user_objects_count, " Service objects")
        print("Service cache: ", item._cache)

        # Global objects count and cache did not changed
        assert global_objects_count == BackendElement().get_count()
        print("Global cache: ", BackendElement().get_cache())
        assert len(BackendElement().get_cache()) == global_objects_count
        # Only 1 Session object
        assert item._count == 1
        assert len(item._cache) == 1

        print(item)
        print(item.__dict__)
        # status is None because there is no status_property defined
        assert "%s" % item == "<service, id: service_0, name: anonymous, status: None>"
        assert item._id == 'service_0'
        assert item._type == 'service'
        assert item.name == 'anonymous'
        assert item.status is None

        item = Service()
        print(item.__dict__)
        assert item._id == 'service_0'

        # Host item with dates
        now = datetime.now()
        item = Service({
            'name': 'test',
            'ls_last_check': now
        })
        print(item.__dict__)
        print(now)
        print(item.get_last_check(timestamp=True))
        assert item._id == 'service_1'
        assert item.get_last_check(timestamp=True) == timegm(now.timetuple())

        # Host item update
        time.sleep(1)
        now2 = datetime.now()
        item = Service({
            'name': 'test',
            'last_check': now,
            '_created': 1470995433,
            '_updated': 1470995450,
            'notes': 'Host notes'
        })
        print(item.created)
        print(item.updated)
        print(item.get_date(item.created))
        assert item.get_date(item.created) == '2016-08-12 11:50:33'
