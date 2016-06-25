#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2016:
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

"""
    Plugin actions
"""

import json
from logging import getLogger
import datetime
from time import gmtime, strftime

from bottle import request, response

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None


def show_acknowledge_add():
    """
        Show form to add an acknowledge
    """
    return {
        'title': request.query.get('title', _('Request an acknowledge')),
        'action': request.query.get('action', 'add'),
        'livestate_id': request.query.getall('livestate_id'),
        'element_name': request.query.getall('element_name'),
        'sticky': request.query.get('sticky', '1') == '1',
        'notify': request.query.get('notify', '0') == '1',
        'persistent': request.query.get('persistent', '1') == '1',
        'comment': request.query.get('comment', _('Acknowledge requested from WebUI')),
        'read_only': request.query.get('read_only', '0') == '1',
        'auto_post': request.query.get('auto_post', '0') == '1'
    }


def add_acknowledge():
    """
    Add an acknowledgement

    Parameters:
    - livestate_id[]: all the livestate elements identifiers to be acknowledged

    - sticky
    - notify
    - persistent
    - comment

    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    user_id = user.id
    if not target_user.is_anonymous():
        user_id = target_user.id

    livestate_ids = request.forms.getall('livestate_id')
    if not livestate_ids:
        logger.error("request to send an acknowledge: missing livestate_id parameter!")
        return webui.response_invalid_parameters(_('Missing livestate identifier: livestate_id'))

    problem = False
    status = ""
    index = 0
    for livestate_id in livestate_ids:
        livestate = datamgr.get_livestate({'where': {'_id': livestate_id}})
        if not livestate:
            status += _('Livestate element %s does not exist') % livestate_id
            continue

        livestate = livestate[0]
        # Prepare post request ...
        data = {
            'action': 'add',
            'host': livestate.host.id,
            'service': None,
            'user': user_id,
            'sticky': request.forms.get('sticky', 'false') == 'true',
            'notify': request.forms.get('notify', 'false') == 'true',
            'persistent': request.forms.get('persistent', 'false') == 'true',
            'comment': request.forms.get('comment', _('No comment'))
        }
        if livestate.service != 'service':
            data.update({'service': livestate.service.id})

        if not datamgr.add_acknowledge(data=data):
            status += _("Failed adding an acknowledge for %s") % livestate.name
            problem = True
        else:
            status += _('Acknowledge sent for %s.') % livestate.name

    logger.info("Request an acknowledge, result: %s", status)

    if not problem:
        return webui.response_ok(message=status)
    else:
        return webui.response_ko(message=status)


def show_recheck_add():
    """
        Show form to request a forced check
    """
    return {
        'title': request.query.get('title', _('Send a check request')),
        'livestate_id': request.query.getall('livestate_id'),
        'element_name': request.query.getall('element_name'),
        'comment': request.query.get('comment', _('Re-check requested from WebUI')),
        'read_only': request.query.get('read_only', '0') == '1',
        'auto_post': request.query.get('auto_post', '0') == '1'
    }


def add_recheck():
    """
    Request a forced check
    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    user_id = user.id
    if not target_user.is_anonymous():
        user_id = target_user.id

    livestate_ids = request.forms.getall('livestate_id')
    if not livestate_ids:
        logger.error("request to send an recheck: missing livestate_id parameter!")
        return webui.response_invalid_parameters(_('Missing livestate identifier: livestate_id'))

    problem = False
    status = ""
    index = 0
    for livestate_id in livestate_ids:
        livestate = datamgr.get_livestate({'where': {'_id': livestate_id}})
        if not livestate:
            status += _('Livestate element %s does not exist') % livestate_id
            continue

        livestate = livestate[0]
        # Prepare post request ...
        data = {
            'host': livestate.host.id,
            'service': None,
            'user': user_id,
            'comment': request.forms.get('comment', _('No comment'))
        }
        if livestate.service != 'service':
            data.update({'service': livestate.service.id})

        if not datamgr.add_recheck(data=data):
            status += _("Failed adding a check request for %s") % livestate.name
            problem = True
        else:
            status += _('Check request sent for %s.') % livestate.name

    logger.info("Request a re-check, result: %s", status)

    if not problem:
        return webui.response_ok(message=status)
    else:
        return webui.response_ko(message=status)


def show_downtime_add():
    """
        Show form to add a downtime
    """
    return {
        'title': request.query.get('title', _('Request a downtime')),
        'action': request.query.get('action', 'add'),
        'livestate_id': request.query.getall('livestate_id'),
        'element_name': request.query.getall('element_name'),
        'start_time': request.query.get('start_time'),
        'end_time': request.query.get('end_time'),
        'fixed': request.query.get('fixed', '1') == '1',
        'duration': request.query.get('duration', 86400),
        'comment': request.query.get('comment', _('Downtime requested from WebUI')),
        'read_only': request.query.get('read_only', '0') == '1',
        'auto_post': request.query.get('auto_post', '0') == '1'
    }


def add_downtime():
    """
    Add a downtime
    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    user_id = user.id
    if not target_user.is_anonymous():
        user_id = target_user.id

    livestate_ids = request.forms.getall('livestate_id')
    if not livestate_ids:
        logger.error("request to send an downtime: missing livestate_id parameter!")
        return webui.response_invalid_parameters(_('Missing livestate identifier: livestate_id'))

    problem = False
    status = ""
    index = 0
    for livestate_id in livestate_ids:
        livestate = datamgr.get_livestate({'where': {'_id': livestate_id}})
        if not livestate:
            status += _('Livestate element %s does not exist') % livestate_id
            continue

        livestate = livestate[0]

        # Prepare post request ...
        data = {
            'action': 'add',
            'host': livestate.host.id,
            'service': None,
            'user': user_id,
            'start_time': request.forms.get('start_time'),
            'end_time': request.forms.get('end_time'),
            'fixed': request.forms.get('fixed', 'false') == 'true',
            'duration': int(request.forms.get('duration', '86400')),
            'comment': request.forms.get('comment', _('No comment'))
        }
        if livestate.service != 'service':
            data.update({'service': livestate.service.id})

        logger.critical("Request a downtime, data: %s", data)
        if not datamgr.add_downtime(data=data):
            status += _("Failed adding a downtime for %s") % livestate.name
            problem = True
        else:
            status += _('downtime sent for %s.') % livestate.name

    logger.info("Request a downtime, result: %s", status)

    if not problem:
        return webui.response_ok(message=status)
    else:
        return webui.response_ko(message=status)


pages = {
    show_acknowledge_add: {
        'name': 'Acknowledge add form',
        'route': '/acknowledge/form/add',
        'view': 'acknowledge_form_add'
    },
    add_acknowledge: {
        'name': 'Acknowledge',
        'route': '/acknowledge/add',
        'method': 'POST'
    },
    show_recheck_add: {
        'name': 'Recheck add form',
        'route': '/recheck/form/add',
        'view': 'recheck_form_add'
    },
    add_recheck: {
        'name': 'Recheck',
        'route': '/recheck/add',
        'method': 'POST'
    },
    show_downtime_add: {
        'name': 'Downtime add form',
        'route': '/downtime/form/add',
        'view': 'downtime_form_add'
    },
    add_downtime: {
        'name': 'Downtime',
        'route': '/downtime/add',
        'method': 'POST'
    }
}
