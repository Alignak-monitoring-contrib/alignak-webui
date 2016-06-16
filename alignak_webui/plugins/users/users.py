#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier pour IPM France

"""
    Plugin Users
"""

import json

from collections import OrderedDict

from logging import getLogger
from bottle import request, response

from alignak_webui.utils.datatable import Datatable
from alignak_webui.utils.helper import Helper

# PLUGIN_TYPE = "prefs"
# PLUGIN_NAME = "prefs"

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None

# Get the same schema as the applications backend and append information for the datatable view
# Use an OrderedDict to create an ordered list of fields
schema = OrderedDict()
schema['name'] = {
    'type': 'string',
    'ui': {
        'title': _('User name'),
        # This field is visible (default: False)
        'visible': True,
        # This field is initially hidden (default: False)
        'hidden': False,
        # This field is searchable (default: True)
        'searchable': True,
        # search as a regex (else strict value comparing when searching is performed)
        'regex': True,
        # This field is orderable (default: True)
        'orderable': True,
    },
}
schema['definition_order'] = {
    'type': 'integer',
    'ui': {
        'title': _('Definition order'),
        'visible': True,
        'hidden': True,
        'orderable': False,
    },
}
schema['alias'] = {
    'type': 'string',
    'ui': {
        'title': _('User alias'),
        'visible': True
    },
}

# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Users table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True,
        'responsive': True
    }
}


def show_user_add():  # pragma: no cover - not yet implemented
    """
        Show form to add a user
    """
    return {
        'user_name': request.query.get('user_name', ''),
        'password': request.query.get('password', 'no_password'),
        'friendly_name': request.query.get('friendly_name', 'Friendly name'),
        'is_admin': request.query.get('is_admin', '0') == '1',
        'is_read_only': request.query.get('is_read_only', '1') == '1',
        'widgets_allowed': request.query.get('widgets_allowed', '1') == '1',
        'notes': request.query.get('notes', _('User description ...')),
        'title': request.query.get('title', _('Create a new user')),
    }


def add_user():  # pragma: no cover - not yet implemented
    """
        Add a user
    """
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
        'description': request.forms.get('notes')
    }
    user_id = datamgr.add_user(data=data)
    if not user_id:
        return webui.response_ko(_('User creation failed'))

    # Refresh data ...
    # datamgr.require_refresh()

    return webui.response_ok(message=_('User created'))


def show_user_delete():  # pragma: no cover - not yet implemented
    """
    User deletion form
    """
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
        'notes': request.query.get('notes', _('Optional notes ...')),
        'title': request.query.get('title', _('Delete a user')),
    }


def delete_user():  # pragma: no cover - not yet implemented
    """
        Delete a user
    """
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
    """
        Show list of users
    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

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
        'pagination': Helper.get_pagination_control('user', total, start, count),
        'title': request.query.get('title', _('All users'))
    }


def get_users_table():
    """
    Get the users list and transform it as a table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('user', search=where)

    # Build table structure
    dt = Datatable('user', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'user',
        'dt': dt,
        'title': request.query.get('title', title)
    }


def get_users_table_data():
    """
    Get the users list and provide table data
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('user', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


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

    get_users_table: {
        'name': 'Users table',
        'route': '/users_table',
        'view': '_table'
    },
    get_users_table_data: {
        'name': 'Users table data',
        'route': '/user_table_data',
        'method': 'POST'
    }
}
