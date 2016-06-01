#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier pour IPM France

'''
    Plugin Contacts
'''

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
        'title': _('Contact name'),
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
        'title': _('Contact alias'),
        'visible': True
    },
}

# This to define if the object in this model are to be used in the UI
schema['ui'] = {
    'type': 'boolean',
    'default': True,

    # UI parameters for the objects
    'ui': {
        'page_title': _('Contacts table (%d items)'),
        'uid': '_id',
        'visible': True,
        'orderable': True,
        'searchable': True
    }
}


def show_contact_add():
    '''
        Show form to add a contact
    '''
    return {
        'contact_name': request.query.get('contact_name', ''),
        'password': request.query.get('password', 'no_password'),
        'friendly_name': request.query.get('friendly_name', 'Friendly name'),
        'is_admin': request.query.get('is_admin', '0') == '1',
        'is_read_only': request.query.get('is_read_only', '1') == '1',
        'widgets_allowed': request.query.get('widgets_allowed', '1') == '1',
        'comment': request.query.get('comment', _('Contact description ...')),
        'title': request.query.get('title', _('Create a new contact')),
    }


def add_contact():
    '''
        Add a contact
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    contact_name = request.forms.get('contact_name', '')
    if not contact_name:
        logger.error("request to add a contact: missing contact_name parameter!")
        return webui.response_invalid_parameters(_('Missing contact name'))

    # Prepare post request ...
    data = {
        'name': contact_name,
        'password': request.forms.get('password', ''),
        'friendly_name': request.forms.get('friendly_name', ''),
        'is_admin': request.forms.get('is_admin') == '1',
        'read_only': request.forms.get('is_read_only') == '1',
        'widgets_allowed': request.forms.get('widgets_allowed') == '1',
        'description': request.forms.get('comment')
    }
    contact_id = datamgr.add_contact(data=data)
    if not contact_id:
        return webui.response_ko(_('Contact creation failed'))

    # Refresh data ...
    # datamgr.require_refresh()

    return webui.response_ok(message=_('Contact created'))


def show_contact_delete():
    '''
    Contact deletion form
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    contact_id = request.query.get('contact_id', -1)
    if contact_id == -1:
        logger.error("request to show a contact deletion form: missing contact_id parameter!")
        return webui.response_invalid_parameters(_('Missing contact identifier'))

    contact = datamgr.get_contact(contact_id)
    if not contact:  # pragma: no cover - should never happen
        return webui.response_invalid_parameters(_('Contact does not exist'))

    return {
        'contact_id': contact_id,
        'contact_name': contact.get_username(),
        'comment': request.query.get('comment', _('Optional comment ...')),
        'title': request.query.get('title', _('Delete a contact')),
    }


def delete_contact():
    '''
        Delete a contact
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    contact_id = request.forms.get('contact_id', -1)
    if contact_id == -1:  # pragma: no cover - should never happen
        logger.error("request to close a contact: missing contact_id parameter!")
        return webui.response_invalid_parameters(_('Missing contact identifier'))

    # Contact deletion request ...
    if not datamgr.delete_contact(contact_id):  # pragma: no cover - should never happen
        return webui.response_ko(_('Contact deletion failed'))

    # Refresh data ...
    # datamgr.require_refresh()

    return webui.response_ok(message=_('Contact deleted'))


def get_contacts():
    '''
        Show list of contacts
    '''
    contact = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    contactname = contact.get_username()
    if not target_user.is_anonymous():
        contactname = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(contactname, 'elts_per_page', 25)

    # Pagination and search
    start = int(request.query.get('start', '0'))
    count = int(request.query.get('count', elts_per_page))
    where = webui.helper.decode_search(request.query.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'where': where
    }

    # Get contacts
    contacts = datamgr.get_contacts(search)
    # Get last total elements count
    total = datamgr.get_objects_count('contact', search=where, refresh=True)
    count = min(count, total)

    return {
        'contacts': contacts,
        'pagination': Helper.get_pagination_control('contact', total, start, count),
        'title': request.query.get('title', _('All contacts'))
    }


def get_contacts_table():
    '''
    Get the contacts list and transform it as a table
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = webui.helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count('contact', search=where)

    # Build table structure
    dt = Datatable('contact', datamgr.backend, schema)

    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': 'contact',
        'dt': dt,
        'title': request.query.get('title', title)
    }


def get_contacts_table_data():
    '''
    Get the contacts list and provide table data
    '''
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable('contact', datamgr.backend, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


# Contact preferences page ...
def show_contact_preferences():
    '''
        Show the contact preferences view
    '''
    return {}


def get_contact_preference():
    '''
        tbc
    '''
    datamgr = request.environ['beaker.session']['datamanager']
    contact = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']

    contactname = contact.get_username()
    if not target_user.is_anonymous():
        contactname = target_user.get_username()

    key = request.query.get('key', None)
    if not key:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    return datamgr.get_user_preferences(contactname, key, request.query.get('default', None))


def get_common_preference():
    '''
        tbc
    '''
    datamgr = request.environ['beaker.session']['datamanager']

    key = request.query.get('key', None)
    if not key:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    return datamgr.get_user_preferences('common', key, request.query.get('default', None))


def set_contact_preference():
    '''
        tbc
    '''
    datamgr = request.environ['beaker.session']['datamanager']
    contact = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']

    contactname = contact.get_username()
    if not target_user.is_anonymous():
        contactname = target_user.get_username()

    key = request.forms.get('key', None)
    value = request.forms.get('value', None)
    if key is None or value is None:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    if datamgr.set_user_preferences(contactname, key, json.loads(value)):
        return webui.response_ok(message=_('Contact preferences saved'))

    return webui.response_invalid_parameters(_('Error when saving contact preferences'))


def set_common_preference():
    '''
        tbc
    '''
    datamgr = request.environ['beaker.session']['datamanager']
    contact = request.environ['beaker.session']['current_user']

    if not webui.prefs_module:
        return webui.response_ko(message=_('No preferences module installed'))

    key = request.forms.get('key', None)
    value = request.forms.get('value', None)
    if key is None or value is None:
        return webui.response_invalid_parameters(_('Missing mandatory parameters'))

    if contact.is_administrator():
        if datamgr.set_user_preferences('common', key, value):
            return webui.response_ok(message=_('Common preferences saved'))
    else:
        return webui.response_ko(message=_('Only adaministrator user can save common preferences'))

    return webui.response_ok(message=_('Error when saving common preferences'))


pages = {
    show_contact_add: {
        'name': 'Contact add form',
        'route': '/contact/form/add',
        'view': 'contact_form_add'
    },
    add_contact: {
        'name': 'Contact add',
        'route': '/contact/add',
        'method': 'POST'
    },

    show_contact_delete: {
        'name': 'Contact delete form',
        'route': '/contact/form/delete',
        'view': 'contact_form_delete'
    },
    delete_contact: {
        'name': 'Contact delete',
        'route': '/contact/delete',
        'method': 'POST'
    },

    get_contacts: {
        'name': 'Contacts',
        'route': '/contacts',
        'view': 'contacts',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            _('Administrator'): 'role:administrator',
            _('Power'): 'role:power',
            _('Contact'): 'role:contact',
            _('Guest'): 'name:anonymous'
        }
    },

    get_contacts_table: {
        'name': 'Contacts table',
        'route': '/contacts_table',
        'view': '_table'
    },
    get_contacts_table_data: {
        'name': 'Contacts table data',
        'route': '/contact_table_data',
        'method': 'POST'
    },

    show_contact_preferences: {
        'name': 'ShowPref',
        'route': '/contact/preferences',
        'view': 'contact_pref'
    },
    get_contact_preference: {
        'name': 'GetPref',
        'route': '/contact/preference',
        'method': 'GET'
    },
    set_contact_preference: {
        'name': 'SetPref',
        'route': '/contact/preference',
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
