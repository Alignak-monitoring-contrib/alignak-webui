#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2015-2017:
#   Frederic Mohier, frederic.mohier@alignak.net
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

from bottle import request

from alignak_webui.objects.element_state import ElementState
from alignak_webui.utils.helper import Helper
from alignak_webui.objects.element import BackendElement

# pylint: disable=invalid-name
logger = getLogger(__name__)


class Datatable(object):

    """jQuery  Datatable plugin interface for backend elements """

    def __init__(self, object_type, datamgr, plugin_table, templates=False):
        """ Create a new datatable:

        - object_type: object type in the backend
        - backend: backend endpoint (http://127.0.0.1:5002)
        - plugin_table: table configuration as defined in a plugin
        - templates: templates table or objects table (False)
        """
        self.object_type = object_type
        self.datamgr = datamgr
        self.backend = self.datamgr.backend

        # Update global table records count, require total count from backend
        self.records_total = 0
        self.records_filtered = 0

        self.id_property = '_id'
        self.name_property = 'name'
        self.status_property = 'status'

        self.title = ""

        # data_model is the complete data model of the plugin
        self.data_model = []
        # table_columns only contains the columns displayed in the table view
        self.table_columns = []
        self.initial_sort = []
        self.embedded = []

        self.visible = True
        self.printable = True
        self.orderable = True
        self.selectable = True
        self.searchable = True
        self.editable = True
        self.responsive = True
        self.recursive = False
        self.commands = (object_type == 'host') or (object_type == 'service')

        self.css = "compact nowrap"

        self.paginable = True
        self.exportable = True
        self.printable = True

        # Table concers a templated backend endpoint (host, service, user)
        self.is_templated = False

        self.id_property = None
        self.name_property = None
        self.status_property = None

        # Get table structure and description
        self.templates = templates
        self.is_templated = False
        self.get_data_model(plugin_table)

        # Templates management
        if self.is_templated:
            self.records_total = self.backend.count(self.object_type,
                                                    params={
                                                        'where': {'_is_template': self.templates}
                                                    })
        else:
            self.records_total = self.backend.count(self.object_type)

    def get_data_model(self, plugin_table):
        """Get the data model for an element type

            If the data model specifies that the element is managed in the UI,
            all the fields for this element are provided

            type and format:
            - type is the type of the field (default: string)
            - format is the representation and filtering format (default: string)
                - if the field is an object relation, type is 'objectid' and format is the name
                of the linked object
                - if the field contains 'allowed' values, format is set to 'select'

            Returns a dictionary containing:
            - element_type: element type
            - uid: unique identifier for the element type. Contains the field that is to be used as
                a unique identifier field
            - page_title: title format string to be used for an element page
            - fields: list of dictionaries. One dictionary per each field mentioned as visible in
                the ui in its plugin_table.

            :return: list of fields name/title"""
        # Current logged user skill level
        user_level = self.datamgr.logged_in_user.skill_level

        self.data_model = []
        self.table_columns = []
        for field, model in plugin_table.iteritems():
            logger.debug('get_data_model, field: %s, plugin_table: %s', field, model)

            if 'skill_level' in model and model['skill_level'] > user_level:
                logger.warning("UI field has a skill level: %s.%s vs %s",
                               field, model['skill_level'], user_level)
                continue

            # Global table configuration?
            if field == '_table':
                self.id_property = model.get('id_property', '_id')
                self.name_property = model.get('name_property', 'name')
                self.status_property = model.get('status_property', 'status')

                self.items_title = model.get('page_title', _('Items table (%d items)'))
                self.templates_title = model.get('template_page_title', self.items_title)

                self.visible = model.get('visible', self.visible)
                self.printable = model.get('printable', self.printable)
                self.orderable = model.get('orderable', self.orderable)
                self.selectable = model.get('selectable', self.selectable)
                self.editable = model.get('editable', self.editable)
                self.searchable = model.get('searchable', self.searchable)
                self.responsive = model.get('responsive', self.responsive)
                self.recursive = model.get('recursive', self.recursive)
                self.commands = model.get('commands', self.commands)
                self.paginable = model.get('paginable', self.paginable)
                self.css = model.get('css', "display nowrap")

                self.initial_sort = model.get('initial_sort', [[0, 'desc']])
                continue

            if field == '_is_template':
                self.is_templated = True

            if self.templates:
                self.title = self.templates_title
            else:
                self.title = self.items_title

            # ignore this field if we display the templates and it is configured as ignored...
            templates_included = model.get('templates_table', False)
            if self.templates and not templates_included:
                logger.debug('get_data_model, templates table filtered: %s', field)
                continue

            # Get all the definitions made in the plugin configuration...
            ui_field = model
            # Update them with some specific information...
            ui_field.update({
                'data': field,
                'type': model.get('type', 'string'),
                'content_type': model.get('content_type', model.get('type', 'string')),
                'allowed': model.get('allowed', ''),
                'default': model.get('default', ''),
                'required': model.get('required', False),
                'empty': model.get('empty', False),
                'unique': model.get('unique', False),

                'regex_search': model.get('regex_search', True),
                'title': model.get('title', field),
                'comment': model.get('comment', ''),
                'format': model.get('format', ''),
                'format_parameters': model.get('format_parameters', ''),
                'visible': model.get('visible', True),
                'hidden': model.get('hidden', False),
                'orderable': model.get('orderable', True),
                'editable': model.get('editable', True),
                'searchable': model.get('searchable', True),
            })

            # If one says a field is hidden, it means that it must be visible ...
            # but it will be hidden!
            if model.get('hidden', False):
                ui_field.update({'visible': True})

            if self.templates and templates_included:
                ui_field.update({'visible': True})
                ui_field.update({'hidden': False})

            if model.get('type') in ['objectid', 'list'] and model.get('data_relation', None):
                relation = model.get('data_relation')
                logger.debug('get_data_model, object/list field: %s / %s',
                             field, relation.get('resource', None))
                ui_field.update(
                    {'content_type': 'objectid:' + relation.get('resource', 'unknown')})

            # logger.debug("get_data_model, field: %s = %s", field, ui_field)

            # If not hidden, return field
            # self.data_model.append(ui_field)
            if not model.get('hidden', False):
                self.table_columns.append(ui_field)

                if ui_field['type'] == 'objectid' or \
                        ui_field['content_type'].startswith('objectid'):
                    self.embedded.append(ui_field['data'])

        return self.data_model

    @staticmethod
    def get_language_strings():
        """Get DataTable language strings"""
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
            'search': _('<span class="fa fa-search"></span>'),
            'searchPlaceholder': _('search...'),
            'zeroRecords': _('No matching records found'),
            'paginate': {
                'first': _('<span class="fa fa-fast-backward"></span>'),
                'last': _('<span class="fa fa-fast-forward"></span>'),
                'next': _('<span class="fa fa-forward"></span>'),
                'previous': _('<span class="fa fa-backward"></span>')
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

                'collection': _('<span class="fa fa-download"></span>'),
                'csv': _('CSV'),
                'excel': _('Excel'),
                'pdf': _('PDF'),

                'print': _('<span class="fa fa-print"></span>'),

                'copy': _('<span class="fa fa-clipboard"></span>'),
                'copyTitle': _('Copy to clipboard'),
                'copyKeys': _(
                    r'Press <span>ctrl</span> or <span>\u2318</span> + <span>C</span> '
                    'to copy the table data to<br>'
                    r'your system clipboard.<br><br>To cancel, click this message or press escape.'
                ),
                'copySuccess': {
                    '1': _('Copied one row to clipboard'),
                    '_': _('Copied %d rows to clipboard')
                },

                'colvis': _('<span class="fa fa-eye-slash"></span>'),
                'colvisRestore': _('Restore'),

                'selectAll': _('<span class="fa fa-plus-square"></span>'),
                'selectNone': _('<span class="fa fa-square-o"></span>'),
                'selectCells': _('Select cells'),
                'selectColumns': _('Select columns'),
                'selectRows': _('Select rows'),
                'selectedSingle': _('Selected single'),
                'selected': _('Selected')
            }
        }

    def table_data(self, plugin_table):
        # Because there are many locals needed :)
        # pylint: disable=too-many-locals
        """Return elements data in json format as of Datatables SSP protocol

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
        - object_type: object type managed by the datatable
        - links: url prefix to be used by the links in the table
        - embedded: true / false whether the table is embedded by an external application
            **Note**: those three first parameters are not datatable specific parameters :)

        - draw, index parameter to be returned in the response

            Pagination:
            - start / length, for pagination

            Searching:
            - search (value or regexp)
            search[value]: Global search value. To be applied to all columns which are searchable
            search[regex]: true if search[value] is a regex

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
        logger.info("request data for table: %s, templates: %s",
                    request.forms.get('object_type'), self.templates)

        # Because of specific datatables parameters name (eg. columns[0] ...)
        # ... some parameters have been json.stringify on client side !
        params = {}
        for key in request.params.keys():
            if key == 'columns' or key == 'order' or key == 'search':
                params[key] = json.loads(request.params.get(key))
            else:
                params[key] = request.params.get(key)
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
        logger.debug("get %d rows from row #%d -> page: %d",
                     rows_count, first_row, parameters['page'])

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
        s_columns = []
        if 'columns' in params and params['columns']:
            for column in params['columns']:
                if 'searchable' not in column or 'search' not in column:  # pragma: no cover
                    continue
                if 'value' not in column['search'] or not column['search']['value']:
                    continue
                logger.debug("search column '%s' for '%s'",
                             column['data'], column['search']['value'])

                for field in self.table_columns:
                    if field['data'] != column['data']:
                        continue

                    # Some specific types...
                    if field['type'] == 'boolean':
                        s_columns.append(
                            {column['data']: column['search']['value'] == 'true'}
                        )
                    elif field['type'] == 'integer':
                        s_columns.append(
                            {column['data']: int(column['search']['value'])}
                        )
                    elif field['format'] == 'select':
                        values = column['search']['value'].split(',')
                        if len(values) > 1:
                            s_columns.append(
                                {
                                    column['data']: {
                                        "$in": values
                                    }
                                }
                            )
                        else:
                            s_columns.append(
                                {column['data']: values[0]}
                            )
                    # ... the other fields :)
                    else:
                        # Do not care about 'smart' and 'caseInsensitive' boolean parameters ...
                        if column['search']['regex']:
                            s_columns.append(
                                {
                                    column['data']: {
                                        "$regex": ".*" + column['search']['value'] + ".*"
                                    }
                                }
                            )
                        else:
                            s_columns.append(
                                {column['data']: column['search']['value']}
                            )
                    break

            logger.info("backend search individual columns parameters: %s", s_columns)

        # Global search parameter
        # search:{"value":"test","regex":false}
        s_global = {}
        # pylint: disable=too-many-nested-blocks
        # Will be too complex else ...
        if 'search' in params and 'columns' in params and params['search']:
            # params['search'] contains something like: {u'regex': False, u'value': u'name:pi1'}
            # global regex is always ignored ... in favor of the column declared regex
            logger.info("global search requested: %s ", params['search'])
            if 'value' in params['search'] and params['search']['value']:
                # There is something to search for...
                logger.debug("search requested, value: %s ", params['search']['value'])

                # New strategy: decode search patterns...
                search = Helper.decode_search(params['search']['value'], plugin_table)
                logger.info("decoded search pattern: %s", search)

                # Old strategy: search for the value in all the searchable columns...
                # if not search:
                #     logger.info("applying datatable search pattern...")
                #     for column in params['columns']:
                #         if not column['searchable']:
                #             continue
                #         logger.debug("search global '%s' for '%s'",
                #                      column['data'], params['search']['value'])
                #         if 'regex' in params['search']:
                #             if params['search']['regex']:
                #                 s_global.update(
                #                     {column['data']: {
                #                         "$regex": ".*" + params['search']['value'] + ".*"}})
                #             else:
                #                 s_global.update({column['data']: params['search']['value']})
                s_global = search

            logger.info("backend search global parameters: %s", s_global)

        # Specific hack to filter the log check results that are not dated!
        if self.object_type == 'logcheckresult':
            s_columns.append({"last_check": {"$ne": 0}})

        if s_columns and s_global:
            parameters['where'] = {"$and": [{"$and": s_columns}, s_global]}
        elif s_columns:
            parameters['where'] = {"$and": s_columns}
        elif s_global:
            parameters['where'] = s_global

        # Embed linked resources / manage templated resources
        parameters['embedded'] = {}
        for field in self.embedded:
            parameters['embedded'].update({field: 1})

        logger.debug("backend embedded parameters: %s", parameters['embedded'])

        # Count total elements excluding templates if necessary
        if self.is_templated:
            self.records_total = self.backend.count(
                self.object_type, params={'where': {'_is_template': self.templates}}
            )
            if 'where' in parameters:
                parameters['where'].update({'_is_template': self.templates})
            else:
                parameters['where'] = {'_is_template': self.templates}
        else:
            self.records_total = self.backend.count(self.object_type)

        # Request objects from the backend ...
        logger.info("table data get parameters: %s", parameters)
        items = self.backend.get(self.object_type, params=parameters)
        logger.info("table data got %d items", len(items))
        if not items:
            logger.info("No backend elements match search criteria: %s", parameters)
            # Empty response
            return json.dumps({
                # draw is the request number ...
                "draw": int(params.get('draw', '0')),
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": []
            })

        # Create an object ...
        object_class = [kc for kc in self.datamgr.known_classes
                        if kc.get_type() == self.object_type]
        if not object_class:  # pragma: no cover, should never happen!
            logger.warning("datatable, unknown object type: %s", self.object_type)
            # Empty response
            return json.dumps({
                # draw is the request number ...
                "draw": int(params.get('draw', '0')),
                "recordsTotal": 0,
                "recordsFiltered": 0,
                "data": []
            })

        # Update table inner properties with the object class defined properties
        object_class = object_class[0]

        self.id_property = '_id'
        if hasattr(object_class, 'id_property'):
            self.id_property = object_class.id_property
        self.name_property = 'name'
        if hasattr(object_class, 'name_property'):
            self.name_property = object_class.name_property
        self.status_property = 'status'
        if hasattr(object_class, 'status_property'):
            self.status_property = object_class.status_property
        logger.debug("datatable, object type: '%s' and properties: %s / %s / %s",
                     object_class, self.id_property, self.name_property, self.status_property)

        # Change item content...
        rows = []
        # Total number of filtered records
        self.records_filtered = self.records_total
        for item in items:
            bo_object = object_class(item)
            logger.debug("table data object: %s", bo_object)
            # Each item contains the total number of records matching the search filter
            self.records_filtered = item['_total']

            row = {}
            row['DT_RowData'] = {}
            row['_id'] = bo_object.id
            for field in self.table_columns:
                # Specific fields
                if field['data'] == self.name_property:
                    # Create a link to navigate to the item page
                    row[self.name_property] = bo_object.html_link
                    # Store the item name in a specific field of the row.
                    # The value will be retrieved by the table actions (ack, recheck, ...)
                    row['DT_RowData'].update({"object_%s" % self.object_type: bo_object.name})
                    continue

                if field['data'] == self.status_property:
                    # Replace the text status with the specific item HTML state
                    row[self.status_property] = bo_object.get_html_state(text=None,
                                                                         title=bo_object.status)
                    # Use the item status to specify the table row class
                    # row['DT_RowClass'] = "table-row-%s" % (bo_object.status.lower())
                    continue

                if field['data'] in ['_overall_state_id', 'overall_state', 'overall_status']:
                    # Get the item overall state from the data manager
                    f_get_overall_state = getattr(self.datamgr,
                                                  'get_%s_overall_state' % self.object_type)
                    if f_get_overall_state:
                        (dummy, overall_status) = f_get_overall_state(bo_object)

                        # Get element state configuration
                        row[field['data']] = ElementState().get_html_state(
                            self.object_type, bo_object,
                            text=None,
                            title=bo_object.overall_state_to_title[bo_object.overall_state],
                            use_status=overall_status
                        )
                        # Use the item overall state to specify the table row class
                        row['DT_RowClass'] = "table-row-%s" % (overall_status)
                    else:  # pragma: no cover, should never happen!
                        logger.warning("Missing get_overall_state method for: %s", self.object_type)
                        row[field['data']] = 'XxX'
                    continue

                if "business_impact" in field['data']:
                    # Replace the BI count with the specific item HTML formatting
                    row[field['data']] = Helper.get_html_business_impact(bo_object.business_impact)
                    continue

                # Specific fields type
                if field['type'] == 'datetime' or field['format'] == 'datetime':
                    # Replace the timestamp with the formatted date
                    row[field['data']] = bo_object.get_date(bo_object[field['data']])
                    continue

                if field['type'] == 'boolean':
                    # Replace the boolean vaue with the specific item HTML formatting
                    row[field['data']] = Helper.get_on_off(bo_object[field['data']])
                    continue

                if field['type'] == 'list':
                    # Replace the list with the specific list HTML formatting
                    if hasattr(bo_object, field['data']):
                        row[field['data']] = Helper.get_html_item_list(
                            bo_object.id, field['data'],
                            getattr(bo_object, field['data']), title=field['title']
                        )
                    else:
                        row[field['data']] = 'Unknown'
                    continue

                if field['type'] == 'dict':
                    # Replace the dictionary with the specific dict HTML formatting
                    row[field['data']] = Helper.get_html_item_list(
                        bo_object.id, field['data'],
                        getattr(bo_object, field['data']), title=field['title']
                    )
                    continue

                if field['type'] == 'objectid':
                    if isinstance(bo_object[field['data']], BackendElement):
                        row[field['data']] = bo_object[field['data']].get_html_link(
                            prefix=request.params.get('links')
                        )
                        # row['DT_RowData'].update({
                        #     "object_%s" % field['data']: bo_object[field['data']].name
                        # })
                    else:
                        logger.warning("Table field is supposed to be an object: %s, %s = %s",
                                       bo_object.name, field['data'],
                                       getattr(bo_object, field['data']))
                        row[field['data']] = getattr(bo_object, field['data'])
                        if row[field['data']] == field['resource']:
                            row[field['data']] = '...'
                    continue

                # For ny non-specific fields, send the firled value to the table
                row[field['data']] = getattr(bo_object, field['data'])
            logger.debug("table data row: %s", row)

            # logger.debug("Table row: %s", row)
            rows.append(row)

        logger.debug("filtered records: %d out of total: %d",
                     self.records_filtered, self.records_total)

        # Send response
        return json.dumps({
            "draw": int(params.get('draw', '0')),
            "recordsTotal": self.records_total,
            "recordsFiltered": self.records_filtered,
            "data": rows
        })
