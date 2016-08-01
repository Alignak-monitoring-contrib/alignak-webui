.. _plugins:


Plugins
=============

The application loads **plugins**...
    TO BE COMPLETED!

Plugin structure
---------------------------------
A plugin is a sub-directory in the application *plugins* directory (eg *plugin*) which  must
contain a Python file named *plugin.py* that is imported by the application as a Python module.

All directories that do not match this requirement are ignored by the application.

The *plugin.py* file must declare a global variable to be aware of the application object::

    # Will be populated by the UI with it's own value
    webui = None

If the plugin is dedicated to a specific Alignak backend type of elements, it must declare which element is managed in a global variable *backend_endpoint*.::

    # Declare backend element endpoint
    backend_endpoint = 'host'

and it must declare which fields it manages in a global OrderedDict *schema*.::

    # Use an OrderedDict to create an ordered list of fields
    schema = OrderedDict()
    # Specific field to include the responsive + button used to display hidden columns on small devices
    schema['#'] = {
        'type': 'string',
        'ui': {
            'title': '',
            # This field is visible (default: False)
            'visible': True,
            # This field is initially hidden (default: False)
            'hidden': False,
            # This field is searchable (default: True)
            'searchable': False,
            # This field is orderable (default: True)
            'orderable': False,
            # search as a regex (else strict value comparing when searching is performed)
            'regex': False,
            # defines the priority for the responsive column hidding (0 is the most important)
            # Default is 10000
            # 'priority': 0,
        }
    }

This will allow the application to route all the request for this type of element to this specific plugin. When an external application requests an hosts list, this plugin will be requested for the list.

If the plugin is to log some information, it must use this pattern::

    from logging import getLogger
    logger = getLogger(__name__)

As of it, the plugin logs will be included in the application main log stream.


Plugin configuration file
---------------------------
A plugin can have its own configuration file.

The application searches in several location for a configuration file:

    - /usr/local/etc/alignak-webui/plugin_NAME.cfg
    - /etc/alignak-webui/plugin_NAME.cfg
    - ~/alignak-webui/plugin_NAME.cfg
    - ./DIR/settings.cfg

Where NAME is the plugin name and DIR is the plugin directory.


Plugin routes
---------------------------------------
A plugin may declare routes for the application Web server. The routes declaration is made through a global dictionary names *pages*.

Main routes:

    - elements view: /elements
    - elements table: /elements_table
    - elements list: /elements_list
    - elements templates: /elements_templates
    - element: /element/element_id
    - elements widgets: /elements/widget
    - element widget: /element/element_id/widget_id

For a recursive element (eg. hostgroups, ...):

    - elements tree view: /elements_tree

A complete example of what is possible can be found in the **hosts** plugin. This example is copied and commented hereunder ...

Example::

    pages = {
        # To allow plugin configuration reload thanks to a browser navigation...
        load_config: {
            'name': 'Hosts plugin config',
            'route': '/hosts/config'
        },
        # Get a widget for an host...
        get_host_widget: {
            'name': 'Host widget',
            'route': '/host_widget/<host_id>/<widget_id>',
            'view': 'host',
            'widgets': [
                {
                    'id': 'information',
                    'for': ['host'],
                    'name': _('Information'),
                    'template': 'host_information_widget',
                    'icon': 'info',
                    'description': _(
                        'Host information: displays host general information.'
                    ),
                    'options': {}
                },

                ...

            ]
        },
        # View an host
        get_host: {
            'name': 'Host',
            'route': '/host/<host_id>',
            'view': 'host'
        },
        # View all hosts
        get_hosts: {
            'name': 'Hosts',
            'route': '/hosts',
            'view': 'hosts'
        },
        # Get all hosts list
        # Note how routes can be defined in an array... if you need several routes to the same function!
        get_hosts_list: {
            'routes': [
                ('/hosts_list', 'Hosts list'),
            ]
        },
        get_hosts_templates: {
            'routes': [
                ('/hosts_templates', 'Hosts templates'),
            ]
        },

        get_hosts_table: {
            'name': 'Hosts table',
            'route': '/hosts_table',
            'view': '_table',
            'search_engine': True,
            'search_prefix': '',
            # Must use this complex structure because we want ordering ... and OrderedDict are not supported.
            'search_filters': {
                # 01 for sorting as first
                # Title
                # Filter: field name : value
                '01': (_('Hosts'), '_is_template:false'),
                # Create a line divider
                '02': ('', ''),
                '03': (_('Hosts templates'), '_is_template:true'),
            },
            'tables': [
                {
                    'id': 'hosts_table',
                    'for': ['external'],
                    'name': _('Hosts table'),
                    'template': '_table',
                    'icon': 'table',
                    'description': _(
                        '<h4>Hosts table</h4>Displays a datatable for the monitored system hosts.<br>'
                    ),
                    'actions': {
                        'hosts_table_data': get_hosts_table_data
                    }
                }
            ]
        },

        get_hosts_table_data: {
            'name': 'Hosts table data',
            'route': '/hosts_table_data',
            'method': 'POST'
        },

        get_hosts_widget: {
            'name': 'Hosts widget',
            'route': '/hosts/widget',
            'method': 'POST',
            'view': 'hosts_widget',
            'widgets': [
                {
                    'id': 'hosts_table',
                    'for': ['external', 'dashboard'],
                    'name': _('Hosts table widget'),
                    'template': 'hosts_table_widget',
                    'icon': 'table',
                    'description': _(
                        '<h4>Hosts table widget</h4>Displays a list of the monitored system hosts.<br>'
                        'The number of hosts in this list can be defined in the widget options.'
                        'The list of hosts can be filtered thanks to regex on the host name'
                    ),
                    'picture': 'htdocs/img/hosts_table_widget.png',
                    'options': {
                        'search': {
                            'value': '',
                            'type': 'text',
                            'label': _('Filter (ex. status:up)')
                        },
                        'count': {
                            'value': -1,
                            'type': 'int',
                            'label': _('Number of elements')
                        },
                        'filter': {
                            'value': '',
                            'type': 'hst_srv',
                            'label': _('Host name search')
                        }
                    }
                },
                {
                    'id': 'hosts_chart',
                    'for': ['external', 'dashboard'],
                    'name': _('Hosts chart widget'),
                    'template': 'hosts_chart_widget',
                    'icon': 'pie-chart',
                    'description': _(
                        '<h4>Hosts chart widget</h4>Displays a pie chart with the system hosts states.'
                    ),
                    'picture': 'htdocs/img/hosts_chart_widget.png',
                    'options': {}
                }
            ]
        },
    }
