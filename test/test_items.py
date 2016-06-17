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
import time
import unittest2
import subprocess

from nose import with_setup # optional
from nose.tools import *

import alignak_webui
from alignak_webui.utils.settings import Settings
from alignak_webui import get_app_config, set_app_config
from alignak_webui.objects.item import *


from logging import getLogger, DEBUG, INFO, WARNING, ERROR
loggerDm = getLogger('alignak_webui.objects.item')
loggerDm.setLevel(DEBUG)
loggerDm = getLogger('alignak_webui.objects.backend')
loggerDm.setLevel(DEBUG)

def setup_module(module):
    print ("")

    # Get configuration from only one file ...
    print ("read configuration")
    cfg = Settings(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'settings.cfg'))
    found_cfg_files = cfg.read('Alignak-WebUI')
    assert found_cfg_files
    set_app_config(cfg)


def teardown_module(module):
    print ("")


class test_00_class(unittest2.TestCase):

    def setUp(self):
        print ""

    def tearDown(self):
        print ""

    def test_00_class(self):
        print "--- test class variables"

        # Create basic object
        # Bad parameters
        with assert_raises(ValueError) as cm:
            item = Item(1)
        ex = cm.exception
        print ex
        self.assertEqual(str(ex), "item.__new__: object parameters must be a dictionary!")

        # Declaration without any parameter is allowed
        item = Item()
        print item
        print item.__dict__
        print item.__class__._cache
        assert len(item.__class__._cache) == 1
        assert item.__class__._count == 1
        # _id is created if it does not exist ...
        assert '_id' in item.__dict__
        # ... but it is for the _id==0 object!
        assert isinstance(item.__dict__['_id'], basestring)
        assert item.__dict__['_id'] == 'item_0'

        # Declaration without any parameter is allowed
        item = Item()
        print item
        print item.__dict__
        print item.__class__._cache
        assert len(item.__class__._cache) == 1
        assert item.__class__._count == 1
        # _id is created if it does not exist ...
        assert '_id' in item.__dict__
        # ... but it is for the _id==0 object!
        assert isinstance(item.__dict__['_id'], basestring)
        assert item.__dict__['_id'] == 'item_0'

        # New declaration with _id in args
        item2 = Item({'_id': 0})
        print "---"
        print item2
        print item2.__dict__
        assert isinstance(item2.__dict__['_id'], basestring)    # Even if _id was an int!
        assert item2.__dict__['_id'] == 'item_0'
        print item2.__class__._cache
        assert len(item.__class__._cache) == 1
        assert item == item2
        # Both objects are the same ... because _id and mandatory fields is the same!

        # New declaration with different parameters in kwargs
        item3 = Item(params={'_id': '0', 'new_param': 1})
        print item3.__dict__
        assert item3.__dict__['_id'] == 'item_0'
        print item3.__class__._cache
        print item.__class__._cache
        assert item3.__class__._cache == item.__class__._cache
        print "cache ---"
        for k,v in item.__class__._cache.items():
            print k, v
        print "---"
        assert len(item.__class__._cache) == 1
        assert item == item3

        # New object because not the same id ...
        item3 = Item(params={'_id': 1, 'new_param': 1})
        print item3.__class__._cache
        print "cache ---"
        for k,v in item.__class__._cache.items():
            print k, v
        print "---"
        assert len(item.__class__._cache) == 2
        assert item.__class__._count == 2
        assert item != item3
        # Different objects because different id !

        # Default class variables
        auto_id = item.__class__._next_id
        assert item.__class__._next_id == 1   # First auto object id is 1
        print item.__class__._next_id
        item = Item()
        assert item.__class__._next_id == 1   # Still the same ...
        assert Item().__class__._next_id == 1 # id is not incremented because of empty parameters
        print "cache ---"
        for k,v in item.__class__._cache.items():
            print k, v
        print "---"
        assert len(item.__class__._cache) == 2
        assert item.__class__._count == 2
        item = Item()
        print item.__class__._cache
        assert len(item.__class__._cache) == 2  # No new objects because no parameters
        assert Item().__class__._default_date == 0
        assert Item().__class__._type == 'item'
        print item.__class__._cache
        assert len(item.__class__._cache) == 2
        assert Item().__class__.items_states == [
            "ok", "warning", "critical", "unknown", "not_executed"
        ]

        # New auto id objects
        auto_id = item.__class__._next_id
        assert item.__class__._next_id == 1
        item = Item(params={'param': '0', 'new_param': 1})
        print item.__dict__
        assert item.__dict__['_id'] == 'item_1'     # auto id is prefixed with item type
        assert item.__dict__['param'] == '0'    # parameter set
        assert item.__dict__['new_param'] == 1  # parameter set
        print "cache ---"
        for k,v in item.__class__._cache.items():
            print k, v
        print "---"
        print item.__class__._cache['0']
        print item.__class__._cache['1']
        print item.__class__._cache['item_1']
        print "---"
        print item.__class__._cache
        assert len(item.__class__._cache) == 3
        assert item.__class__._count == 3

        # Same objects because same id ...
        item2 = Item(params={'_id': 'item_1', 'new_param': 2})
        print item2.__dict__
        assert item2.__dict__['_id'] == 'item_1'    # auto id is prefixed with #
        assert item2.__dict__['param'] == '0'   # parameter not changed
        assert item2.__dict__['new_param'] == 2 # parameter changed
        assert len(item.__class__._cache) == 3
        assert item.__class__._count == 3
        assert item == item2

    def test_01_cache(self):
        print "--- test class cache"

        # Clean generic Item cache and reset counter to 0
        Item.cleanCache()

        # Create basic object
        # Declaration without any parameter is allowed
        item = Item()
        print "--- cache:"
        print Item.getCache()
        assert len(Item.getCache()) == 1
        assert Item.getType() == 'item'
        assert Item.getCount() == 1

        # New declaration with _id in args
        item2 = Item({'_id': 0})
        assert item == item2
        # Both objects are the same ... because _id and mandatory fields is the same!
        print "--- cache:"
        print Item.getCache()
        assert len(Item.getCache()) == 1
        assert Item.getCount() == 1

        # New declaration with different parameters in kwargs
        item3 = Item(params={'_id': '0', 'new_param': 1})
        assert item == item3
        print "--- cache:"
        print Item.getCache()
        assert len(Item.getCache()) == 1
        assert Item.getCount() == 1

        # New object because not the same id ...
        item3 = Item(params={'_id': 1, 'new_param': 1})
        assert item != item3
        # Different objects because different id !
        print "--- cache:"
        print Item.getCache()
        assert len(Item.getCache()) == 2
        assert Item.getCount() == 2

        # Delete objects
        item3._delete()
        print "--- cache:"
        print Item.getCache()
        assert len(Item.getCache()) == 1
        assert Item.getCount() == 1


class test_01_items_states(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."
        # Application configuration is loaded
        self.config = get_app_config()
        assert self.config

    def tearDown(self):
        print ""
        print "tearing down ..."

    def test_01_items_states(self):
        print "---"

        items_states = ItemState()
        assert items_states.object_types_states
        assert items_states.default_states
        assert items_states.states
        print "Objects types and states", items_states.object_types_states
        print "Default states", items_states.default_states
        print "Items states", items_states.states

        for s in self.config:
            s = s.split('.')
            if s[0] not in ['items'] and len(s) > 1:
                assert s[1] not in items_states.object_types_states
                assert s[1] not in items_states.default_states
                assert s[1] not in items_states.states
            else:
                if s[0] not in ['items']:
                    continue
                print s
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
                        print s[1], items_states.states[s[1]]

    def test_02_items_states(self):
        print "---"

        items_states = ItemState()
        assert items_states.object_types_states
        assert items_states.default_states
        assert items_states.states
        print "Objects types and states", items_states.object_types_states
        print "Default states", items_states.default_states
        print "Items states", items_states.states

        assert items_states.get_objects_types()
        print "All objects types : ", items_states.get_objects_types()

        assert items_states.get_icon_states()
        print "All objects : ", items_states.get_icon_states()

        assert items_states.get_default_states()
        print "Default states : ", items_states.get_default_states()

        # Objects known states
        for object_type in items_states.object_types_states:
            assert items_states.get_icon_states(object_type)
            print object_type, ", all states: ", items_states.get_icon_states(object_type)
            for state in items_states.get_icon_states(object_type):
                assert items_states.get_icon_state(object_type, state)
                print object_type, ", state: ", state, ": ", items_states.get_icon_state(object_type, state)

        assert not items_states.get_icon_state(None, None)

        # Default states are in all objects types
        for state in items_states.get_default_states():
            print "Default state: ", state
            for object_type in items_states.object_types_states:
                assert items_states.get_icon_states(object_type)

    def test_03_html_states(self):
        print "---"

        items_states = ItemState()
        assert items_states.object_types_states
        assert items_states.default_states
        assert items_states.states

        # Objects known states
        save_object_type = 'user'
        for object_type in items_states.object_types_states:
            print "Html for: ", object_type
            for state in items_states.get_icon_states(object_type):
                if state == 'state_view':
                    continue

                object = Item({
                    '_id': '0', 'status': state
                })
                print "Html for:", object_type, ", object:", object
                assert items_states.get_html_state(object_type, object)
                print "Html : ", items_states.get_html_state(object_type, object)

        # Unknown states
        print "States for: fake"
        print items_states.get_icon_states('fake')
        assert not items_states.get_icon_states('fake')

        print "Html for:", save_object_type, ", state: fake"
        print "Unknown state"
        object = Item({
            '_id': '0', 'status': 'fake'
        })
        print items_states.get_html_state(save_object_type, object)
        assert items_states.get_html_state(save_object_type, object) == 'n/a - status: fake'

        print "Html for: fake, state: unknown"
        print "Unknown object type"
        object = Item({
            '_id': '0', 'status': 'unknown'
        })
        # Unknown object_type provides a default user html state ...
        item_state = items_states.get_html_state('fake', object)
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="fake"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % object.id)

        # Bad parameters
        print "No icon/text"
        item_state = items_states.get_html_state(save_object_type, object, icon=False, text='')
        print item_state
        self.assertEqual(item_state, 'n/a - icon/text')

        print "Default icon/text"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, text='')
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % object.id)

        # Other parameters
        print "Default icon/text - disabled"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, text='', disabled=True)
        print item_state
        self.assertEqual(item_state, '''<div class="item-state font-greyed " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x font-greyed"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % object.id)

        print "Default icon/text - title and default text"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, title='Test title')
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="Test title"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % object.id)

        print "Default icon/text - title without text"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, text=None, title='Test title')
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="Test title"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span></span></div>''' % object.id)

        print "Default icon/text - not title and default text"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, text='Test')
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>Test</span></div>''' % object.id)

        print "Default icon/text - not title and text"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, text='Test text')
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>Test text</span></div>''' % object.id)

        print "Default icon/text - extra"
        item_state = items_states.get_html_state(save_object_type, object, icon=True, text='', extra='test')
        print item_state
        self.assertEqual(item_state, '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack" style="opacity: 0.5" title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x test"></i></span><span>User default text</span></div>''' % object.id)


class test_02_items(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."
        # Application configuration is loaded
        self.config = get_app_config()
        assert self.config

    def tearDown(self):
        print ""
        print "tearing down ..."

    def test_01_items(self):
        print "--- test Item"

        # Clean generic Item cache and reset counter to 0
        Item.cleanCache()

        # Base item with parameters, including identifier
        parameters = { '_id': 'test_id', 'foo': 'bar', 'foo_int': 1 }
        item = Item(parameters)
        print item.__dict__
        assert item._id == 'test_id'
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.name == 'anonymous'

        # Same object
        parameters = { '_id': 'test_id', 'foo': 'bar', 'foo_int': 1 }
        item2 = Item(parameters)
        print "item2", item2.__dict__
        assert item2._id == 'test_id'
        assert item2.foo == 'bar'
        assert item2.foo_int == 1
        assert item.name == 'anonymous'
        assert item.alias == 'anonymous'
        assert item.notes == ''

        # Same objects!
        assert item == item2

        # New object
        parameters = { '_id': 'test_id2', 'foo': 'baz', 'foo_int': 9 }
        item3 = Item(parameters)
        print item3.__dict__
        assert item3._id == 'test_id2'
        assert item3.foo == 'baz'
        assert item3.foo_int == 9

        # Different objects!
        assert item != item3
        assert item2 != item3

        # Update object from a dict
        item._update({ 'foo': 'bar', 'foo_int': 1 })
        assert item.foo == 'bar'
        assert item.foo_int == 1
        # Still true ... so different
        assert item != item3
        assert item2 != item3

        # Update object from an object
        item._update(item3)
        assert item._id == 'test_id2'
        assert item.foo == 'baz'
        assert item.foo_int == 9
        # Still true ... so different
        assert item != item3
        assert item2 != item3

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
            'foo_date': '2016-04-01',                       # Invalid string formet
            'epoch_date': 0,                                # Valid timestamp date (integer)
            'now_date': now,                                # Valid timestamp date (time tuple)
            'now_time_date': now_time,                      # Valid timestamp date time (integer)
            '_created': 'Tue, 01 Mar 2016 14:15:38 GMT',    # Valid string format
            '_updated':'Tue, 01 Mar 2016 14:15:38 XX'       # Invalid string format => default date
        }
        item = Item(parameters)
        print item.__dict__
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
            'foo_date': '2016-04-01 10:58:12',              # Valid string formet
            'now_date': now,                                # Valid timestamp date
            '_created': None,                               # Invalid string format => default date
            '_updated':'Tue, 01 Mar 2016 14:15:38 GMT'      # Invalid string format
        }
        item = Item(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print item.__dict__
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
            '_updated':'Tue, 01 Mar 2016 14:15:38 XX'       # Invalid string format => default date
        }
        item._update(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print item.__dict__
        self.assertEqual(item._id, 'item_2')     # Still the same object
        self.assertEqual(item.id, 'item_2')
        self.assertEqual(item.foo, 'bar2')
        self.assertEqual(item.foo_int, 2)
        self.assertEqual(item.ts_date, 1459508293)
        self.assertEqual(item.foo_date, 1459508293)
        self.assertEqual(item.now_date, timegm(now.timetuple()))
        self.assertEqual(item.fake_date, 0)
        self.assertEqual(item.alias, item.name)
        self.assertEqual(item.notes, '')

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
        item = Item(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print item.__dict__
        assert item._id == 'item_3'     # New object
        assert item.foo == 'bar'
        assert item.foo_int == 1
        assert item.foo_date == 1459508293
        assert item.now_date == timegm(now.timetuple())
        assert item.dict_param
        print item.dict_param
        assert item.dict_param['param1'] == 1
        assert item.dict_param['param2'] == '2'

        assert item.name == 'anonymous'
        assert item.alias == 'Item alias'
        assert item.notes == 'Item notes'
        assert item.status == 'unknown'
        print item.get_icon_states()
        assert item.get_icon_states()

    def test_02_users(self):
        print "--- test User"

        # Global (Item) objects count
        global_objects_count = Item().getCount()
        print global_objects_count, "objects"
        print "--- cache:"
        print User.getCache()
        assert len(User.getCache()) == 0

        # Base item
        item = User()
        assert item
        print "--- cache:"
        print User.getCache()
        assert len(User.getCache()) == 1


        # Specific (User) objects count and cache
        user_objects_count = item._count
        print user_objects_count, " User objects"
        print item._cache

        # Global objects count and cache did not changed
        assert global_objects_count == Item().getCount()
        assert len(Item().getCache()) == global_objects_count
        # Only 1 User object
        assert item._count == 1
        assert len(User.getCache()) == 1

        print item
        assert "%s" % item == "<user, id: user_0, name: anonymous, role: user>"
        assert item._id == 'user_0'  # Because no _id in the parameters ...
        assert item._type == 'user'
        assert item.name == 'anonymous'
        assert item.status == 'unknown'

        assert item.role == 'user'
        assert item.read_only == True
        assert item.picture == '/static/images/user_guest.png'
        assert item.authenticated == False
        assert item.widgets_allowed == False
        assert item.is_admin == False

        assert item.get_role() == 'user'
        assert item.get_role(display=True) == 'User'
        assert item.is_administrator() == False
        assert item.is_anonymous() == True
        assert item.can_submit_commands() == False
        assert item.can_change_dashboard() == False
        assert item.picture == '/static/images/user_guest.png'

        print item.get_html_state()
        self.assertEqual(item.get_html_state(), '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % item._id)


        item = User({
            'name': 'test',
            'password': 'test',
            'is_admin': False,
            'widgets_allowed': True,
            'read_only': False,
            'email': 'test@gmail.com',
            'lync': 'test@lync.com',
            'token': 'token'
        })
        assert item._id == 'user_1' # Not 0 because parameters are provided but auto generated because no _id in the parameters!

        assert item.get_role() == 'power'
        assert item.get_role(display=True) == 'Power user'
        assert item.is_administrator() == False
        assert item.is_anonymous() == False
        assert item.can_submit_commands() == True
        assert item.can_change_dashboard() == True
        assert item.picture == '/static/images/user_default.png'
        assert item.token == 'token'

        print item.get_html_state()
        assert item.get_html_state() == '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="test" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % item._id


        item = User({
            'name': 'test',
            'user_name': 'test',
            'friendly_name': 'Friendly name',
            'password': 'test',
            'is_admin': True
        })
        assert item._id == 'user_2' # Not 0 because parameters are provided but auto generated because no _id in the parameters!

        assert item.name == 'test'
        assert item.friendly_name == 'Friendly name'
        assert item.get_role() == 'administrator'
        assert item.get_role(display=True) == 'Administrator'
        assert item.is_administrator() == True
        assert item.is_anonymous() == False
        assert item.can_submit_commands() == True
        assert item.can_change_dashboard() == True
        assert item.picture == '/static/images/user_admin.png'

        print item.get_html_state()
        assert item.get_html_state() == '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="test" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % item.id


        item = User({
            'username': 'test_priority',
            'name': 'test',
            'alias': 'Real name',
            'password': 'test',
            'is_admin': False,
            'widgets_allowed': '0',
            'read_only': True
        })
        print item.__dict__

        assert item.name == 'test'
        assert item.alias == 'Real name'
        assert item.get_username() == 'test_priority'
        assert item.get_role() == 'user'
        assert item.get_role(display=True) == 'User'
        assert item.is_administrator() == False
        assert item.is_anonymous() == False
        assert item.can_submit_commands() == False
        assert item.can_change_dashboard() == False
        assert item.picture == '/static/images/user_default.png'

        print "State: ", item.get_html_state()
        self.assertEqual(item.get_html_state(), '''<div class="item-state item_user " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="test" data-item-type="user"><span class="fa-stack"  title="User default text"><i class="fa fa-circle fa-stack-2x item_user"></i><i class="fa fa-user fa-stack-1x fa-inverse"></i></span><span>User default text</span></div>''' % item.id)

        item = User({
            'username': 'test_priority',
            'name': 'test',
            'alias': 'Aliased name',
            'password': 'test',
            'is_admin': False,
            'read_only': '1'
        })
        assert item.name == 'test'
        assert item.alias == 'Aliased name'
        assert item.get_username() == 'test_priority'
        assert item.can_submit_commands() == False
        assert item.can_change_dashboard() == False
        # Update with a new obect declaration
        item = User({
            '_id': item._id,
            'alias': 'Aliased name (bis)',
            'is_admin': True
        })
        assert item.alias == 'Aliased name (bis)'
        assert item.get_username() == 'test_priority'
        assert item.can_submit_commands() == True
        assert item.can_change_dashboard() == True
        # Update calling _update
        item._update({
            'alias': 'Aliased name (bis)',
            'is_admin': True
        })
        assert item.alias == 'Aliased name (bis)'
        assert item.get_username() == 'test_priority'
        assert item.can_submit_commands() == True
        assert item.can_change_dashboard() == True

    def test_03_commands(self):
        print "--- test Command"

        # Global (Item) objects count
        global_objects_count = Item().getCount()
        print global_objects_count, "objects"
        print Item().getCache()

        # Base item
        item = Command()
        print item.__dict__
        print item
        assert item
        assert len(Command.getCache()) == 1


        # Specific (Command) objects count and cache
        user_objects_count = Command.getCount()
        print user_objects_count, " Command objects"
        print item._cache
        assert user_objects_count == 1

        # Global objects count and cache did not changed
        assert global_objects_count == Item().getCount()
        assert len(Item().getCache()) == global_objects_count
        # Only 1 User object
        assert item._count == 1
        assert len(item._cache) == 1
        assert len(Command.getCache()) == 1

        print item
        assert "%s" % item == "<command, id: command_0, name: anonymous, status: unknown>"
        assert item._id == 'command_0'  # Because no _id in the parameters ...
        assert item._type == 'command'
        assert item.name == 'anonymous'
        assert item.status == 'unknown'

        assert item.status == 'unknown'

        print item.get_html_state()
        assert item.get_html_state() == '''<div class="item-state item_command " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="anonymous" data-item-type="command"><span class="fa-stack"  title=""><i class="fa fa-circle fa-stack-2x item_command"></i><i class="fa fa-bolt fa-stack-1x fa-inverse"></i></span><span></span></div>''' % item.id

    def test_04_hosts(self):
        print "--- test Host"

        # Global (Item) objects count
        global_objects_count = Item().getCount()
        print global_objects_count, "objects"
        print "Global cache: ", Item().getCache()

        # Base item
        item = Host()
        print item.__dict__
        print item
        assert item


        # Specific (Session) objects count and cache
        user_objects_count = item._count
        print user_objects_count, " Host objects"
        print "Host cache: ", item._cache

        # Global objects count and cache did not changed
        assert global_objects_count == Item().getCount()
        print "Global cache: ", Item().getCache()
        assert len(Item().getCache()) == global_objects_count
        # Only 1 Session object
        assert item._count == 1
        assert len(item._cache) == 1

        print item
        assert "%s" % item == "<host, id: host_0, name: anonymous, status: unknown>"
        assert item._id == 'host_0'
        assert item._type == 'host'
        assert item.name == 'anonymous'
        assert item.status == 'unknown'

        item = Host()
        print item.__dict__
        assert item._id == 'host_0'

        # Host item with dates
        now = datetime.now()
        item = Host({
            'name': 'test',
            'last_check': now
        })
        print item.__dict__
        assert item._id == 'host_1'
        assert item.get_last_check(timestamp=True) == timegm(now.timetuple())

        # Host item update
        time.sleep(1)
        now2 = datetime.now()
        parameters = {
            'last_check': now2,
            'notes': 'Host notes'
        }
        item._update(parameters, date_format='%Y-%m-%d %H:%M:%S')
        print item.__dict__
        assert item._id == 'host_1'
        assert item.get_last_check(timestamp=True) == timegm(now2.timetuple())

        # Base item methods
        # No backend id (_id)
        assert item.id == 'host_1'
        assert item.name == 'test'
        assert item.notes == 'Host notes'
        assert item.status == 'unknown'
        print item.get_html_state()
        assert item.get_html_state() == '''<div class="item-state item_hostUnknown " style="display: inline; font-size:0.9em;" data-item-id="%s" data-item-name="test" data-item-type="host"><span class="fa-stack"  title="Host is unknown"><i class="fa fa-circle fa-stack-2x item_hostUnknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span><span>Host is unknown</span></div>''' % item.id


class test_03_relations(unittest2.TestCase):

    def setUp(self):
        print ""
        print "setting up ..."

    def tearDown(self):
        print ""
        print "tearing down ..."

    def test_01_host_command(self):
        print "--- test Item"

        # Base item
        cmd = Command({
            '_id': 'cmd1',
            'name': 'command 1'
        })

        host = Host({
            '_id': 'host1',
            'name': 'host 1',
            'check_command': 'cmd1' # Command id
        })

        print host.__dict__
        print host.check_command
        assert host.check_command == 'command'  # Remained the init string because no link could be done with the command ... the backend is not available to find the command !

