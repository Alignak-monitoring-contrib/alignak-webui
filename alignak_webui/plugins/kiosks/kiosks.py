#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (C) 2015-2016 F. Mohier pour IPM France

'''
    Plugin Kiosks
'''

import os
import time
import re

from urlparse import urljoin

import shutil

from base64 import b64decode

from datetime import datetime
from logging import getLogger

import requests

from bottle import request, response

from alignak_webui.objects.item import Kiosk

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None


def get_kiosks():
    '''
    Get the kiosks list
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
        webui.prefs_module.set_ui_user_preference(username, 'sound', sound)
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

    # Get elements from the data manager
    kiosks = datamgr.get_kiosks(search)
    # Get last total elements count
    total = datamgr.get_objects_count('kiosk', search=where, refresh=True)
    count = min(count, total)

    return {
        'kiosks': kiosks,
        'start': start, 'count': count, 'total': total,
        'pagination': webui.helper.get_pagination_control(total, start, count),
        'title': request.query.get('title', _('All kiosks')),
        'bookmarks': webui.prefs_module.get_user_bookmarks(username),
        'bookmarksro': webui.prefs_module.get_common_bookmarks(),
        'sound': sound_pref,
        'elts_per_page': elts_per_page
    }


def get_kiosks_widget():
    '''
    Get the kiosks list widget
    '''
    # user = request.environ['beaker.session']['current_user']
    # target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    # We want to limit the number of elements, The user will be able to increase it
    nb_elements = max(0, int(request.query.get('nb_elements', '10')))

    # Search string ...
    search = request.query.get('search', '')
    items = datamgr.get_kiosks(webui.helper.decode_search(search))

    # Ok, if needed, apply the widget refine search filter
    if search:
        # We compile the pattern
        pat = re.compile(search, re.IGNORECASE)
        new_kiosks = []
        for p in items:
            if pat.search(p.get_name()):
                new_kiosks.append(p)
                continue

        items = new_kiosks[:nb_elements]

    kiosks = items[:nb_elements]

    wid = request.query.get('wid', 'widget_kiosks_' + str(int(time.time())))
    collapsed = (request.query.get('collapsed', 'false') == 'true')
    header = (request.query.get('header', 'false') == 'true')
    commands = (request.query.get('commands', 'false') == 'true')

    options = {
        'search': {
            'value': search,
            'type': 'text',
            'label': _('Filter (kiosk name)')
        },
        'nb_elements': {
            'value': nb_elements,
            'type': 'int',
            'label': _('Maximum number of elements')
        },
        'commands': {
            'value': commands,
            'type': 'bool',
            'label': _('Commands')
        },
        'header': {
            'value': header,
            'type': 'bool',
            'label': _('Kiosks header')
        }
    }

    title = _('User kiosks')
    if search:
        title = _('User kiosks (%s)') % search

    return {
        'kiosks': kiosks,
        'all_kiosks': items,
        'search': search,
        'page': 'kiosks',
        'wid': wid, 'collapsed': collapsed, 'options': options,
        'base_url': '/widget/kiosks', 'title': title,
        'header': header, 'commands': commands
    }


widget_desc = _('<h4>Kiosks</h4>List the kiosks')


pages = {
    get_kiosks: {
        'name': 'Kiosks',
        'route': '/kiosks',
        'view': 'kiosks',
        'search_engine': True,
        'search_prefix': '',
        'search_filters': {
            'With attachment': 'status:attached',
            'Without attachment': 'status:empty',
        }
    },
    get_kiosks_widget: {
        'name': 'wid_kiosks',
        'route': '/widget/kiosks',
        'view': 'widget_kiosks',
        'widget': ['dashboard'],
        'widget_desc': widget_desc,
        'widget_id': 'kiosks',
        'widget_name': _('Kiosks'),
        'widget_picture': 'htdocs/img/widget_kiosks.png'
    }
}
