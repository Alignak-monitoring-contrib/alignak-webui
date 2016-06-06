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
    Datatable module
    ------------------

    This module implements an interface for the server side scripting of the jQuery Datatables
    plugin (https://datatables.net/manual/server-side).

    Each element used in the Web UI and presented with a table form references a Datatable object
    to implement this interface. The ElementsView class used by (almost ...) all the elements
    contains a property which is a Datatable object.
"""
import json
from logging import getLogger
from bottle import request, response, view

# Import all objects we will need
# pylint: disable=wildcard-import,unused-wildcard-import
# We need all the classes defined whatever their number to use the globals() object.
from alignak_webui.objects.item import *

from alignak_webui.utils.helper import Helper

logger = getLogger(__name__)


class Datatable(object):
    """ jQuery  Datatable plugin interface for backend elements """

    def __init__(self, object_type, backend, schema):
        """
        Create a new datatable:
        - object_type: object type in the backend
        - backend: backend endpoint (http://127.0.0.1:5002)
        - schema: model dictionary (see hosts.py as an example)
        """
        self.object_type = object_type
        self.backend = backend

        self.recordsTotal = 0

        self.visible = True
        self.orderable = True
        self.searchable = True
        self.responsive = True

        self.paginable = True
        self.exportable = True
        self.printable = True

        self.id_property = None
        self.name_property = None
        self.status_property = None

        self.get_data_model(schema)

    ##
    # Total records
    ##
    def get_total_records(self):
        """
        Request objects from the backend to pick-up total records count
        """
        # Request objects from the backend ...
        resp = self.backend.get(self.object_type, params={'page': 0, 'max_results': 1})
        logger.debug("get_total_records _meta: %s", resp['_meta'])

        # Total number of records
        self.recordsTotal = 0
        if '_meta' in resp:
            self.recordsTotal = int(resp['_meta']['total'])

        return self.recordsTotal

    ##
    # Data model
    ##
    def get_data_model(self, schema):
        """ Get the data model for an element type

            If the data model specifies that the element is managed in the UI,
            all the fields for this element are provided

            Returns a dictionary containing:

            - element_type: element type
            - uid: unique identifier for the element type. Contains the field that is to be used as
                a unique identifier field
            - page_title: title format string to be used for an element page
            - fields: list of dictionaries. One dictionary per each field mentioned as visible in
                the ui in its schema. The dictionary contains all the fields defined in the 'ui'
                property of the schema of the element.

            :param element_type: element type
            :type element_type: str
            :return: list of fields name/title
            :rtype: list
            :return: dictionary
            :rtype: list
        """
        self.table_columns = []

        if not schema:
            logger.error(
                "get_data_model, missing schema"
            )
            return None

        ui_dm = {
            'element_type': self.object_type,
            'model': {
                'uid': None,
                'page_title': '',
                'fields': {}
            }
        }

        for field, model in schema.iteritems():
            logger.debug("get_data_model, field: %s = %s", field, model)
            ui_dm['model']['fields'].update({field: model})

            if field == 'ui':
                if 'uid' not in model['ui']:  # pragma: no cover - should never happen
                    logger.error(
                        'get_data_model, UI schema is not well formed: missing uid property'
                    )
                    continue
                ui_dm['model']['uid'] = model['ui']['uid']
                ui_dm['model']['page_title'] = model['ui']['page_title']
                # Useful? Table is visible ?
                ui_dm['model']['visible'] = model['ui']['visible']
                # Useful? Table is orderable ?
                ui_dm['model']['orderable'] = model['ui']['orderable']
                # Useful? Table is searchable ?
                ui_dm['model']['searchable'] = model['ui']['searchable']
                # Useful? Table is searchable ?
                ui_dm['model']['responsive'] = model['ui']['responsive']
                continue

            if 'ui' in model and ('visible' not in model['ui'] or not model['ui']['visible']):
                continue

            # If element is considered for the UI
            if 'ui' not in model:
                continue

            # Copy all model 'ui' dictionary fields and mange specific values for the field format
            ui_dm['model']['fields'][field].update(model['ui'])
            ui_dm['model']['fields'][field].update({'format': model.get('type', '')})
            if 'allowed' in model:
                ui_dm['model']['fields'][field].update(
                    {'format': 'select'}
                )
            if 'data_relation' in model and model['data_relation']['embeddable']:
                ui_dm['model']['fields'][field].update(
                    {'format': model['data_relation']['resource']}
                )

            # Convert data model format to datatables' one ...
            self.table_columns.append({
                # 'name': field,
                'data': field,
                'regex': model.get('regex', False),
                'title': model.get('title', field),
                'type': model.get('type', 'string'),
                'format': model.get('format', 'string'),
                'allowed': ','.join(model.get('allowed', [])),
                'defaultContent': model.get('default', ''),
                'width': model.get('width', '500px'),
                'size': model.get('size', 10),
                'visible': not model.get('hidden', False),
                'orderable': model.get('orderable', True),
                'searchable': model.get('searchable', True),
                # 'responsivePriority': model.get('priority', 10000),
            })

        if not ui_dm['model']['fields']:  # pragma: no cover, should never happen
            logger.error(
                "get_data_model, missing UI information in the backend data model"
            )
            return None

        self.title = ui_dm['model']['page_title']
        self.visible = ui_dm['model']['visible']
        self.orderable = ui_dm['model']['orderable']
        self.searchable = ui_dm['model']['searchable']
        self.responsive = ui_dm['model']['responsive']

    ##
    # Localization
    ##
    def get_language_strings(self):
        """
        Get DataTable language strings
        """
        return {
            'decimal': _('.'),
            'thousands': _(','),
            'emptyTable': _('No data available in table'),
            'info': _('Showing _START_ to _END_ of _TOTAL_ entries'),
            'infoEmpty': _('Showing 0 to 0 of 0 entries'),
            'infoFiltered': _(' out of _MAX_ entries.'),
            'infoPostFix': _(' '),
            'lengthMenu': _('Show _MENU_ entries'),
            'loadingRecords': _('Loading...'),
            'processing': _('Processing...'),
            'search': _('<i class="fa fa-search"></i>'),
            'searchPlaceholder': _('search...'),
            'zeroRecords': _('No matching records found'),
            'paginate': {
                'first': _('<i class="fa fa-fast-backward"></i>'),
                'last': _('<i class="fa fa-fast-forward"></i>'),
                'next': _('<i class="fa fa-forward"></i>'),
                'previous': _('<i class="fa fa-backward"></i>')
            },
            'aria': {
                'sortAscending': _(': activate to sort column ascending'),
                'sortDescending': _(': activate to sort column descending'),
                'paginate': {
                    'first': _('First page'),
                    'last': _('Last page'),
                    'next': _('Next page'),
                    'previous': _('Previous page')
                },
            },
            'buttons': {
                'pageLength': {
                    '-1': _('Show all rows'),
                    '_': _('Show %d rows')
                },

                'collection': _('<i class="fa fa-external-link"></i>'),
                'csv': _('CSV'),
                'excel': _('Excel'),
                'pdf': _('PDF'),

                'print': _('<i class="fa fa-print"></i>'),

                'copy': _('<i class="fa fa-clipboard"></i>'),
                'copyTitle': _('Copy to clipboard'),
                'copyKeys': _(
                    r'Press <i>ctrl</i> or <i>\u2318</i> + <i>C</i> to copy the table data to<br>'
                    r'your system clipboard.<br><br>To cancel, click this message or press escape.'
                ),
                'copySuccess': {
                    '1': _('Copied one row to clipboard'),
                    '_': _('Copied %d rows to clipboard')
                },

                'colvis': _('<i class="fa fa-eye-slash"></i>'),
                'colvisRestore': _('Restore')
            }
        }

    #
    # Data source
    #
    def table_data(self):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """
        Return elements data in json format as of Datatables SSP protocol
        More info: https://datatables.net/manual/server-side

        Example URL::

            POST /?
            draw=1&
            columns[0][data]=alias&
            columns[0][name]=&
            columns[0][searchable]=true&
            columns[0][orderable]=true&
            columns[0][search][value]=&
            columns[0][search][regex]=false&
             ...
            order[0][column]=0&
            order[0][dir]=asc&
            start=0&
            length=10&
            search[value]=&
            search[regex]=false&

        Request parameters are Json formatted

        Request Parameters:
        - draw, index parameter to be returned in the response

            Pagination:
            - start / length, for pagination

            Searching:
            - search (value or regexp)
            search[value]: Global search value. To be applied to all columns which are searchable
            search[regex]: true if searh[value] is a regex

            Sorting:
            - order[i][column] / order[i][dir]
            index of the columns to order and sort direction (asc/desc)

            Columns:
            - columns[i][data]: Column's data source, as defined by columns.data.
            - columns[i][name]: Column's name, as defined by columns.name.
            - columns[i][searchable]: Flag to indicate if this column is searchable (true).
            - columns[i][orderable]: Flag to indicate if this column is orderable (true).
            - columns[i][search][value]: Search value to apply to this specific column.
            - columns[i][search][regex]: Flag to indicate if the search term for this column is a
            regex.

        Response data:
        - draw

        - recordsTotal: total records, before filtering
            (i.e. total number of records in the database)

        - recordsFiltered: Total records, after filtering
            (i.e. total number of records after filtering has been applied -
            not just the number of records being returned for this page of data).

        - data: The data to be displayed in the table.
            an array of data source objects, one for each row, which will be used by DataTables.

        - error (optional): Error message if an error occurs
            Not included if there is no error.
        """
        # Manage request parameters ...
        logger.info("request data for table: %s", request.forms.get('object_type'))

        # Because of specific datatables parameters name (eg. columns[0] ...)
        # ... some parameters have been json.stringify on client side !
        params = {}
        for key in request.forms.keys():
            if key == 'columns' or key == 'order' or key == 'search':
                params[key] = json.loads(request.forms.get(key))
            else:
                params[key] = request.forms.get(key)
        # params now contains 'valid' query parameters as we should have found them ...
        logger.debug("table request parameters: %s", params)

        parameters = {}

        # Manage page number ...
        # start is the first requested row and we must transform to a page count ...
        first_row = int(params.get('start', '0'))
        # length is the number of requested rows
        rows_count = int(params.get('length', '25'))

        parameters['page'] = (first_row // rows_count) + 1
        parameters['max_results'] = rows_count
        logger.info(
            "get %d rows from row #%d -> page: %d",
            rows_count, first_row, parameters['page']
        )

        # Columns ordering
        # order:[{"column":2,"dir":"desc"}]
        if 'order' in params and 'columns' in params and params['order']:
            sorted_columns = []
            for order in params['order']:
                idx = int(order['column'])
                if params['columns'][idx] and params['columns'][idx]['data']:
                    logger.debug(
                        "sort by column %d (%s), order: %s ",
                        idx, params['columns'][idx]['data'], order['dir']
                    )
                    if order['dir'] == 'desc':
                        sorted_columns.append('-' + params['columns'][idx]['data'])
                    else:
                        sorted_columns.append(params['columns'][idx]['data'])
            if sorted_columns:
                parameters['sort'] = ','.join(sorted_columns)

            logger.info("backend order request parameters: %s", parameters)

        # Individual column search parameter
        searched_columns = []
        if 'columns' in params and params['columns']:
            for column in params['columns']:
                if 'searchable' not in column or 'search' not in column:  # pragma: no cover
                    continue
                if 'value' not in column['search'] or not column['search']['value']:
                    continue
                logger.debug(
                    "search column '%s' for '%s'",
                    column['data'], column['search']['value']
                )
                column_type = 'string'
                for field in self.table_columns:
                    if field['data'] == column['data']:
                        column_type = field['type']
                        break

                # Do not care about 'smart' and 'caseInsensitive' boolean parameters ...
                # Only take care of 'regex'
                if 'regex' in column['search']:
                    if column['search']['regex']:
                        if column_type == 'integer':
                            searched_columns.append(
                                '{ "%s": { "$regex": .*%s.* } }' % (
                                    column['data'], column['search']['value']
                                )
                            )
                        else:
                            searched_columns.append(
                                '{ "%s": { "$regex": ".*%s.*" } }' % (
                                    column['data'], column['search']['value']
                                )
                            )
                    else:
                        if column_type == 'integer':
                            searched_columns.append(
                                '{ "%s": %s }' % (
                                    column['data'], column['search']['value']
                                )
                            )
                        else:
                            searched_columns.append(
                                '{ "%s": "%s" }' % (
                                    column['data'], column['search']['value']
                                )
                            )

            logger.info("backend search columns parameters: %s", searched_columns)

        # Global search parameter
        # search:{"value":"test","regex":false}
        searched_global = []
        # pylint: disable=too-many-nested-blocks
        # Will be too complex else ...
        if 'search' in params and 'columns' in params and params['search']:
            if 'value' in params['search'] and params['search']['value']:
                logger.debug(
                    "search requested, value: %s ",
                    params['search']['value']
                )
                for column in params['columns']:
                    if 'searchable' in column and column['searchable']:
                        logger.debug(
                            "search global '%s' for '%s'",
                            column['data'], params['search']['value']
                        )
                        if 'regex' in params['search']:
                            if params['search']['regex']:
                                searched_global.append(
                                    '{ "%s": { "$regex": ".*%s.*" } }' % (
                                        column['data'], params['search']['value']
                                    )
                                )
                            else:
                                searched_global.append(
                                    '{ "%s": "%s" }' % (
                                        column['data'], params['search']['value']
                                    )
                                )

            logger.info("backend search global parameters: %s", searched_global)

        if searched_columns and searched_global:
            parameters['where'] = '{"$and": [ %s, %s ] }' % (
                '{"$and": [' + ','.join(searched_columns) + '] }',
                '{"$or": [' + ','.join(searched_global) + '] }'
            )
        if searched_columns:
            parameters['where'] = '{"$and": [' + ','.join(searched_columns) + '] }'
        if searched_global:
            parameters['where'] = '{"$or": [' + ','.join(searched_global) + '] }'

        # Embed linked resources
        embedded = {}
        for field in self.table_columns:
            if field['type'] == 'objectid' and field['format'] != 'objectid':
                embedded.update({field['data']: 1})
        if embedded:
            parameters['embedded'] = json.dumps(embedded)
            logger.info("backend embedded parameters: %s", parameters['embedded'])

        # Request ALL objects from the backend
        recordsTotal = self.get_total_records()

        # Request objects from the backend ...
        logger.debug("table data get parameters: %s", parameters)
        resp = self.backend.get(self.object_type, params=parameters)
        logger.debug("response _meta: %s", resp['_meta'])
        logger.debug("response _links: %s", resp['_links'])
        # logger.debug("response _items: %s", resp['_items'])

        # Total number of filtered records
        recordsFiltered = len(resp['_items'])
        if '_meta' in resp and (searched_columns or searched_global):
            recordsFiltered = int(resp['_meta']['total'])
        # recordsFiltered = int(resp['_meta']['total'])

        # Create an object ...
        if resp['_items']:
            bo_object = None
            for k in globals().keys():
                if isinstance(globals()[k], type) and \
                   '_type' in globals()[k].__dict__ and \
                   globals()[k].getType() == self.object_type:
                    bo_object = globals()[k]()
                    logger.debug("created: %s", bo_object)
                    break

            self.id_property = '_id'
            if hasattr(bo_object.__class__, 'id_property'):
                self.id_property = bo_object.__class__.id_property
            self.name_property = 'name'
            if hasattr(bo_object.__class__, 'name_property'):
                self.name_property = bo_object.__class__.name_property
            self.status_property = 'status'
            if hasattr(bo_object.__class__, 'status_property'):
                self.status_property = bo_object.__class__.status_property

            # Change item content ...
            for item in resp['_items']:
                # _update is the method name... yes, it sounds like a protected member :/
                # pylint: disable=protected-access
                bo_object._update(item)
                logger.debug("Object: %s", bo_object)
                for key in item.keys():
                    for field in self.table_columns:
                        if field['data'] != key:
                            continue

                        # Specific fields name
                        if field['data'] == self.name_property:
                            item[key] = '''<a href="%s/%s">%s</a>''' % (
                                bo_object.getType(),
                                bo_object.get_id(),
                                bo_object.get_name()
                            )

                        if field['data'] == self.status_property:
                            item[key] = bo_object.get_html_state()

                        if field['data'] == "business_impact":
                            item[key] = Helper.get_html_business_impact(bo_object.business_impact)

                        # Specific fields type
                        if field['type'] == 'datetime':
                            item[key] = bo_object.get_date(item[key])

                        if field['type'] == 'boolean':
                            item[key] = Helper.get_on_off(item[key])

                        if field['type'] == 'objectid' and key in embedded and item[key]:
                            for k in globals().keys():
                                if isinstance(globals()[k], type) and \
                                   '_type' in globals()[k].__dict__ and \
                                   globals()[k]._type == field['format']:
                                    linked_object = globals()[k](item[key])
                                    logger.debug("created: %s", linked_object)
                                    item[key] = '''<a href="%s/%s">%s</a>''' % (
                                        field['format'],
                                        item[key]['_id'] if '_id' in item[key] else '',
                                        linked_object.get_html_state(
                                            label=linked_object.get_name()
                                        )
                                    )
                                    break

        # Prepare response
        rsp = {
            # draw is the request number ...
            "draw": int(params.get('draw', '0')),
            "recordsTotal": recordsTotal,
            "recordsFiltered": recordsFiltered,
            "data": resp['_items']
        }
        return json.dumps(rsp)
