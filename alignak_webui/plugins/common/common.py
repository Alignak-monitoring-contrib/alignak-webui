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
    The common plugin is not a real plugin ... it simply allows to declare the views used by several
    other plugins.
"""
from logging import getLogger
from bottle import request, response, template

from alignak_webui import _
from alignak_webui.utils.helper import Helper
from alignak_webui.utils.datatable import Datatable

logger = getLogger(__name__)

# Will be populated by the UI with it's own value
webui = None


def get_table(object_type, schema, embedded=False, identifier=None, credentials=None):
    """
    Build the object_type table and get data to populate the table
    """
    datamgr = request.environ['beaker.session']['datamanager']

    # Pagination and search
    where = {'saved_filters': True}
    if request.query.get('search') is not None:
        where = Helper.decode_search(request.query.get('search', ''))

    # Get total elements count
    total = datamgr.get_objects_count(object_type, search=where, refresh=True)

    # Build table structure
    dt = Datatable(object_type, datamgr, schema)

    # Build page title
    title = dt.title
    if '%d' in title:
        title = title % total

    return {
        'object_type': object_type,
        'dt': dt,
        'where': where,
        'title': request.query.get('title', title),
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    }


def get_table_data(object_type, schema):
    """
    Get the table data (requested from the table)
    """
    datamgr = request.environ['beaker.session']['datamanager']
    dt = Datatable(object_type, datamgr, schema)

    response.status = 200
    response.content_type = 'application/json'
    return dt.table_data()


# noinspection PyUnusedLocal
def get_widget(get_method, object_type, embedded=False, identifier=None, credentials=None):
    # Because there are many locals needed :)
    # pylint: disable=too-many-locals
    """
    Get a widget...
    - get_methode is the datamanager method to call to get elements
    - object_type is the elements type

    - widget_id: widget identifier

    - start and count for pagination
    - search for specific elements search

    """
    user = request.environ['beaker.session']['current_user']
    datamgr = request.environ['beaker.session']['datamanager']
    target_user = request.environ['beaker.session']['target_user']

    username = user.get_username()
    if not target_user.is_anonymous():
        username = target_user.get_username()

    # Fetch elements per page preference for user, default is 25
    elts_per_page = datamgr.get_user_preferences(username, 'elts_per_page', 25)
    elts_per_page = elts_per_page['value']

    # Pagination and search
    start = int(request.params.get('start', '0'))
    count = int(request.params.get('count', elts_per_page))
    where = webui.helper.decode_search(request.params.get('search', ''))
    search = {
        'page': start // count + 1,
        'max_results': count,
        'where': where
    }
    name_filter = request.params.get('filter', '')
    if name_filter:
        search['where'].update({
            '$or': [
                {'name': {'$regex': ".*%s.*" % name_filter}},
                {'alias': {'$regex': ".*%s.*" % name_filter}}
            ]
        })
    logger.info("Search parameters: %s", search)

    # Get elements from the data manager
    elements = get_method(search)
    # Get last total elements count
    total = datamgr.get_objects_count(object_type, search=where, refresh=True)
    count = min(count, total)

    # Widget options
    widget_id = request.params.get('widget_id', '')
    if widget_id == '':
        return webui.response_invalid_parameters(_('Missing widget identifier'))

    widget_place = request.params.get('widget_place', 'dashboard')
    widget_template = request.params.get('widget_template', 'elements_table_widget')
    widget_icon = request.params.get('widget_icon', 'plug')
    # Search in the application widgets (all plugins widgets)
    options = {}
    for widget in webui.widgets[widget_place]:
        if widget_id.startswith(widget['id']):
            options = widget['options']
            widget_template = widget['template']
            widget_icon = widget['icon']
            logger.info("Widget found, template: %s, options: %s", widget_template, options)
            break
    else:
        logger.warning("Widget identifier not found: %s", widget_id)
        return webui.response_invalid_parameters(_('Unknown widget identifier'))

    if options:
        options['search']['value'] = request.params.get('search', '')
        options['count']['value'] = count
        options['filter']['value'] = name_filter
    logger.info("Widget options: %s", options)

    title = request.params.get('title', _('Hosts'))
    if name_filter:
        title = _('%s (%s)') % (title, name_filter)

    # Use required template to render the widget
    return template('_widget', {
        'widget_id': widget_id,
        'widget_name': widget_template,
        'widget_place': widget_place,
        'widget_template': widget_template,
        'widget_icon': widget_icon,
        'widget_uri': request.urlparts.path,
        'elements': elements,
        'options': options,
        'title': title,
        'embedded': embedded,
        'identifier': identifier,
        'credentials': credentials
    })
