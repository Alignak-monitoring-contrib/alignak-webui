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
from bottle import request, response

logger = getLogger(__name__)

# Will be valued by the plugin loader
webui = None


def show_acknowledge_add():
    """
        Show form to add an acknowledge
    """
    return {
        'title': request.query.get('title', _('Send an acknowledgement')),
        'action': request.query.get('action', 'add'),
        'element_name': request.query.get('element_name', 'Unknown'),
        'livestate_id': request.query.get('livestate_id', '-1'),
        'sticky': request.query.get('is_admin', '1') == '1',
        'notify': request.query.get('is_read_only', '0') == '1',
        'persistent': request.query.get('persistent', '1') == '1',
        'comment': request.query.get('comment', _('Acknowledge comment...')),
    }


def add_acknowledge():
    """
    Add an acknowledgement
    """
    user = request.environ['beaker.session']['current_user']
    target_user = request.environ['beaker.session']['target_user']
    datamgr = request.environ['beaker.session']['datamanager']

    user_id = user.id
    if not target_user.is_anonymous():
        user_id = target_user.id

    livestate_id = request.forms.get('livestate_id', '')
    if not livestate_id:
        logger.error("request to send an acknowledge: missing livestate_id parameter!")
        return webui.response_invalid_parameters(_('Missing livestate identifier: livestate_id'))

    livestate = datamgr.get_livestate({'where': {'_id': livestate_id}})
    if not livestate:
        return webui.response_invalid_parameters(_('Livestate element does not exist'))
    livestate = livestate[0]

    logger.critical("livestate: %s", livestate)
    # Prepare post request ...
    data = {
        'action': 'add',
        'host': livestate.host.id,
        'service': livestate.service.id,
        'user': user_id,
        'sticky': request.forms.get('sticky', '0') == '1',
        'notify': request.forms.get('notify', '0') == '1',
        'persistent': request.forms.get('persistent', '0') == '1',
        'comment': request.forms.get('comment', "{{_('No comment')}}")
    }
    if not datamgr.add_acknowledge(data=data):
        return webui.response_ko(_("Failed adding an acknowledge"))

    status = _('Acknowledge sent for %s.' % request.forms.get('element_name', 'Unknown'))

    logger.critical("request to send an acknowledge, result: %s", status)

    return webui.response_ok(message=status)


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
    }
}
