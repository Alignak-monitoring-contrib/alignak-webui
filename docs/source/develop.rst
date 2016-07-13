.. _develop:

Development
===========

Application
-----------

Web application developed with Python Bottle micro-framework. See application.py

User authentication
~~~~~~~~~~~~~~~~~~~~~~~~

If no session exists all the requests are redirected to the /login page. User is authenticated near Alignak bakcned with username / password. Once authenticated, a Contact representing the current user is stored in the session. This contact has an *authenticated* attribute set.

Cookie name is the application name(Alignak-WebUI). Expiry delay is 6 hours.

Session stores the current user, the target user, the connection message and the data manager.


Session management
~~~~~~~~~~~~~~~~~~~~~~~~

Use Beaker middleware for session management. The configuration is made in `__init__.py`.

The session is stored in memory, mainly for performance and also because some stored objects can not be pickled (BackendConnection) to file storage.

A cookie named as the application (Alignak-WebUI) is existing as soon as a session is created. Its expiry delay is 6 hours.

The session stores the current user, the target user, the connection message and the data manager containing all the UI data.


Data manager
------------------
 The application uses a DataManager object to store all the information about the data got from the Alignak backend.

 TO BE DETAILED !


Datatables
------------------
Table configuration
~~~~~~~~~~~~~~~~~~~~~~~~

A backend object used in a plugin can be displayed as a table. For this, the plugin must declare:

    - a table build URL (eg. element_table)
    - a table update URL (eg. element_table_data)
    - a table schema as a global OrderedDict variable named *schema*

The *schema* defines the global table configuration and the table columns configuration. Each column is declared as an item of the *schema* ordered dictionary. The declaration order will be used for the column order in the table.

The name of each column item much match eaxctly the name of the backend element field. The same constraint applies  for the column type.

The `ui` item in each column configuration is used to configure the table specific behaviour for a particular column. See the comments in the example below.

The main `ui` item in the *schema* is used to configure the global table behaviour. This field allows to define the table title and the table main characteristics (ordering, sorting, ...). See the comments in the example below.

As an example::

        schema = OrderedDict()
        # Specific field to include the responsive + button used to display hidden columns on small devices (needed if the table type is responsive, else optional...)
        schema['#'] = {
            'type': 'string',
            'ui': {
                'title': '#',
                'visible': True,
                'hidden': False,
                'searchable': False,
                'orderable': False,
                'regex': False,
            }
        }

        schema['type'] = {
            'type': 'string',
            'ui': {
                # Column title
                'title': _('Type'),
                # This field is visible (default: False)
                'visible': True,
                # This field is initially hidden (default: False)
                'hidden': False,
                # This field is searchable (default: True)
                'searchable': True,
                # search as a regex (default: True), else use an exact value match
                'regex': True,
                # This field is orderable (default: True)
                'orderable': True,
            },
            'allowed': ["host", "service"]
        }
        schema['name'] = {
            'type': 'string',
            'ui': {
                'title': _('Element name'),
                'visible': True,
            }
        }


        # This to define the global information for the table
        schema['ui'] = {
            'type': 'boolean',
            'default': True,

            # UI parameters for the objects
            'ui': {
                'page_title': _('Livestate table (%d items)'),
                # id, name and status property for the table elements
                # Default values are:
                # 'id_property': '_id',
                # 'name_property': 'name',
                # 'status_property': 'status',
                # Must be True for the table to to displayed (obvious...)!
                'visible': True,
                # Table is orderable by columns
                'orderable': True,
                # Table is editable
                'editable': False,
                # Table rows can be selected
                'selectable': True,
                # Table columns search is activated
                'searchable': True,
                # Table is responsive (no horizontal scroll)
                'responsive': True,

                # Table initial sort
                # Sort by descending business impact (column index 9)
                'initial_sort': [[9, "desc"]]
            }
        }

Table display
~~~~~~~~~~~~~~~~~~~~~~~~

If a status_property is defined for the table (default is to use the `status` field in the elemnts), then each table row has an extra CSS class named as: table-row-status_property.

As an example, for the livestate table, an element with status UP will have a CSS class **table-row-up**.

The corresponding classes can be defined in the *alignak_webui-items.css* file. Some example classes still exist in this file for the livestate states (eg. UP, OK, ...).

Table filtering
~~~~~~~~~~~~~~~~~~~~~~~~

Table filtering is available on a column basis; each column can have its own search parameter in the table header. The filtering field is an input field, a select field, ... according to the column type/format.

 TO BE DETAILED (fields type/format)!

The data backend search is made with an AND operator on all the provided values. Furthermore, each column has a *regex* parameter. This parameter indicates wether the search is an exact (False) or loose (True) match on the data value.

The table filtering is stored in the user's preferences to be restored the next time the page is refreshed or browsed.

A table button indicates if some filters are activated and also allows to clear the currently applied filters.

Web UI pages displaying a datatable can receive an URL parameter to influence the data filtering. If the *search* query parameter is present in the URL it takes precedence over the existing column filtering. As of it, the user can request a specific table filter that will be used instead of the saved filtering.

On table loading, the filtering logic is as follows:
    - restore previously saved state
    - if no URL filtering is present, restore filters from saved state
    - if URL filtering is present, clear table filtering and apply URL filtering

The URL filtering parameter *search* has a very simple syntax:
    - `?search=` to clear all the table filters
    - `?search=name:value` to search for `value` in the column `name`
    - `?search=name:value name2:value2` to search for `value` in the column `name` and `value2` in `name2`

Some examples:
    - livestate hosts UP: `search=type:host state:UP`
    - livestate hosts DOWN: `search=type:host state:DOWN`
    - livestate services WARNING: `search=type:service state:WARNING` or `search=type:service state_id:1`
    - livestate hosts/services OK/UP: `search=state_id:0`
    - livestate elements business impact high: `search=business_impact:5`

User's preferences
------------------

 TO BE EXPLAINED !

HTML templates
---------------

 TO BE EXPLAINED !

Debug mode
~~~~~~~~~~~~~~
Many templates declare a local `debug` variable that will display extra information. Simply declare this variable as True (eg. `%setdefault('debug', True)`). Debug information panels have a *bug* icon ;)

Some specific templates for debug mode:

    - layout.tpl, will display all the HTTP request information
    - _actionbar.tpl will display all the widgets available for dashboard and external access

Good practices
~~~~~~~~~~~~~~

From Python to javascript, main javascript variables are declared in layout.tpl to be available for every HTML and Javascript files.
