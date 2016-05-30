#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier pour IPM France

'''
    Plugin Users
'''

import json

from logging import getLogger
from bottle import request

PLUGIN_TYPE = "prefs"
PLUGIN_NAME = "prefs"

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None


def show_user_add():
    '''
        Show form to add a user
    '''
    return {
        'user_name': request.query.get('user_name', ''),
        'password': request.query.get('password', 'no_password'),
        'friendly_name': request.query.get('friendly_name', 'Friendly name'),
        'is_admin': request.query.get('is_admin', '0') == '1',
        'is_read_only': request.query.get('is_read_only', '1') == '1',
        'widgets_allowed': request.query.get('widgets_allowed', '1') == '1',
        'comment': request.query.get('comment', _('User description ...')),
        'title': request.query.get('title', _('Create a new user')),
    }


def add_user():
    '''
        Add a user
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    user_name = request.forms.get('user_name', '')
    if not user_name:
        logger.error("request to add a user: missing user_name parameter!")
        return webui.response_invalid_parameters(_('Missing user name'))

    # Prepare post request ...
    data = {
        'name': user_name,
        'password': request.forms.get('password', ''),
        'friendly_name': request.forms.get('friendly_name', ''),
        'is_admin': request.forms.get('is_admin') == '1',
        'read_only': request.forms.get('is_read_only') == '1',
        'widgets_allowed': request.forms.get('widgets_allowed') == '1',
        'description': request.forms.get('comment')
    }
    user_id = datamgr.add_user(data=data)
    if not user_id:
        return webui.response_ko(_('User creation failed'))

    # Refresh data ...
    # datamgr.require_refresh()

    return webui.response_ok(message=_('User created'))


def show_user_delete():
    '''
    User deletion form
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    user_id = request.query.get('user_id', -1)
    if user_id == -1:
        logger.error("request to show a user deletion form: missing user_id parameter!")
        return webui.response_invalid_parameters(_('Missing user identifier'))

    user = datamgr.get_user(user_id)
    if not user:  # pragma: no cover - should never happen
        return webui.response_invalid_parameters(_('User does not exist'))

    return {
        'user_id': user_id,
        'user_name': user.get_username(),
        'comment': request.query.get('comment', _('Optional comment ...')),
        'title': request.query.get('title', _('Delete a user')),
    }


def delete_user():
    '''
        Delete a user
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    user_id = request.forms.get('user_id', -1)
    if user_id == -1:  # pragma: no cover - should never happen
        logger.error("request to close a user: missing user_id parameter!")
        return webui.response_invalid_parameters(_('Missing user identifier'))

    # User deletion request ...
    if not datamgr.delete_user(user_id):  # pragma: no cover - should never happen
        return webui.response_ko(_('User deletion failed'))

    # Refresh data ...
    # datamgr.require_refresh()

    return webui.response_ok(message=_('User deleted'))


def get_users():
    '''
        Show list of users
    '''
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = webui.prefs_module.get_ui_user_preference(username, 'elts_per_page', 25)

    # Fetch sound preference for user, default is 'no'
    sound_pref = webui.prefs_module.get_ui_user_preference(
        username, 'sound', request.app.config.get('play_sound', 'no')
    )
    sound = request.query.get('sound', '')
    if sound != sound_pref and sound in ['yes', 'no']:  # pragma: no cover - RFU sound
        webui.prefs_module.set_ui_user_preference(user, 'sound', sound)
        sound_pref = sound

    # Pagination and search
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = webui.helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'where': where
    }

    # Get users
    users = datamgr.get_users(search)
    # Get last total elements count
    total = datamgr.get_objects_count('user', search=where, refresh=True)
    count = min(count, total)

    return {
        'users': users,
        'start': start, 'count': count, 'total': total,
        'pagination': webui.helper.get_pagination_control(total, start, count),
        'title': request.query.get('title', _('All users')),
        'bookmarks': webui.prefs_module.get_user_bookmarks(user.get_username()),
        'bookmarksro': webui.prefs_module.get_common_bookmarks(),
        'sound': sound_pref,
        'elts_per_page': elts_per_page
    }


def get_user_preferences(application):
    '''
        tbc
    '''
    from alignak_webui.plugins.users.mongo_prefs import MongoDBPreferences

    return MongoDBPreferences(application.config)


def load_config(application):
    '''
        tbc
    '''
    from pymongo import version
    from alignak_webui.plugins.users.mongo_prefs import MongoDBPreferences

    replica_set = application.config.get('replica_set', None)
    if replica_set and int(version[0]) < 3:  # pragma: no cover - not tested on replica set DB :/
        logger.error('Can not initialize module with '
                     'replica_set because your pymongo lib is too old. '
                     'Please install it with a 3.x+ version from '
                     'https://pypi.python.org/pypi/pymongo')
        return False

    return True


# User preferences page ...
def show_user_preferences():
    '''
        Show the user preferences view
    '''
    return {}


def get_user_preference():
    '''
        tbc
    '''
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    key = request.query.get('key', None)
    if not key:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    return webui.prefs_module.get_ui_user_preference(username, key)


def set_user_preference():
    '''
        tbc
    '''
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    key = request.forms.get('key', None)
    value = request.forms.get('value', None)
    if key is None or value is None:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    # Store value as a JSON object
    webui.prefs_module.set_ui_user_preference(username, key, json.loads(value))

    return webui.response_ok(message=_('User\'s preferences saved'))


def set_common_preference():
    '''
        tbc
    '''
    user = request.environ['beaker.session']['current_user']

    if not webui.prefs_module:
        return webui.response_ko(message=_('No preferences module installed'))

    key = request.forms.get('key', None)
    value = request.forms.get('value', None)
    if key is None or value is None:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    if user.is_administrator():
        # Store value as a JSON object
        webui.prefs_module.set_ui_common_preference(key, json.loads(value))

    return webui.response_ok(message=_('Common preferences saved'))


def get_common_preference():
    '''
        tbc
    '''
    key = request.query.get('key', None)
    if not key:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    value = webui.prefs_module.get_ui_common_preference(key)
    return webui.response_data(value)


pages = {
    show_user_add: {
        'name': 'User add form',
        'route': '/user/form/add',
        'view': 'user_form_add'
    },
    add_user: {
        'name': 'User add',
        'route': '/user/add',
        'method': 'POST'
    },

    show_user_delete: {
        'name': 'User delete form',
        'route': '/user/form/delete',
        'view': 'user_form_delete'
    },
    delete_user: {
        'name': 'User delete',
        'route': '/user/delete',
        'method': 'POST'
    },

    get_users: {
        'name': 'Users',
        'route': '/users',
        'view': 'users',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Administrator'): 'role:administrator',
            _('Power'): 'role:power',
            _('User'): 'role:user',
            _('Guest'): 'name:anonymous'
        }
    },
    show_user_preferences: {
        'name': 'ShowPref',
        'route': '/user/preferences',
        'view': 'user_pref'
    },
    get_user_preference: {
        'name': 'GetPref',
        'route': '/user/preference',
        'method': 'GET'
    },
    set_user_preference: {
        'name': 'SetPref',
        'route': '/user/preference',
        'method': 'POST'
    },
    get_common_preference: {
        'name': 'GetCommonPref',
        'route': '/common/preference',
        'method': 'GET'
    },
    set_common_preference: {
        'name': 'SetCommonPref',
        'route': '/common/preference',
        'method': 'POST'
    }
}
