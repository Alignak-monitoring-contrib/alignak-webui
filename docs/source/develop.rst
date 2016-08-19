.. _develop:

Development
===========

Application
-----------

Web application developed with Python Bottle micro-framework. See `app.py` for the main application file and `application.py` as the Bottle application.

User authentication
~~~~~~~~~~~~~~~~~~~~~~~~

The application install a *before_request* hook to detect if a session currently exists and an authenticated user already connected.

If no session exists all the requests are redirected to the */login* page. User is authenticated near Alignak bakcned with username / password. Once authenticated, a Contact representing the current user is stored in the session. This contact has an *authenticated* attribute set.



Session management
~~~~~~~~~~~~~~~~~~~~~~~~

The application uses Beaker middleware for session management. The configuration is made in `__init__.py`.

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

Backend elements can be displayed as a table. For this, the plugin must declare:

    - a table build URL (eg. `/elements/table`)
    - a table update URL (eg. `/elements/table_data`)
    - a table schema in its configuration file

**Note**: the table URLs are formed with element endpoint (eg. host), a plural form (add an s) and `/table` for the build URL or `/table_data` for the update URL.

The plugin class makes this configuration easy and it is enough to define the table configuration.

The *schema* defines the global table configuration and the table columns configuration. The schema is declared in the plugin configuration file.
Each column is declared as a section of the configuration file.  The declaration order in the configuration file will be used for the column ordering in the table.

The name of each column item much match exactly the name of the backend element field.

The main `table` section in the *schema* is used to configure the global table behaviour. This field allows to define the table title and the table main characteristics (ordering, sorting, ...). See the comments in the example below.

As an example::

        [table]
        ; Table global configuration
        page_title=Hosts table (%%d items)
        visible=True
        orderable=True
        editable=True
        selectable=True
        searchable=True
        responsive=False

        [table.name]
        type=string
        title=Host name
        visible=True
        hidden=False
        searchable=True
        regex=True
        orderable=True
        hint=This field is the host name
        editable=True
        required=True
        empty=False
        unique=True

        [table._realm]
        title=Realm
        type=objectid
        searchable=True
        allowed=inner://realms/list
        resource=realm
        visible=False


Table parameters
~~~~~~~~~~~~~~~~~~~~~~~~

Each table may be:

    - visible, (default: True)
    - printable, (default: True)
    - orderable, (default: True)
    - selectable, (default: True)
    - searchable, (default: True)
    - editable, (default: True)
    - responsive, (default: True)
    - recursive, (default: False)
    - commands, (default: False) - only applies to the livestate table
    - css, (default: display)

Initial (default) table sort is defined as (CURRENTLY NOT IMPLEMENTED !):

    - initial_sort which is an array of array: [[1, "desc"]]

All the tables are sorted by default on the first defined column by ascending value.

Table css classes are defined here: https://datatables.net/manual/styling/classes


Table display
~~~~~~~~~~~~~~~~~~~~~~~~

If a status_property is defined for the table (default is to use the `status` field in the elements), then each table row has an extra CSS class named as: table-row-status_property.

As an example, for the livestate table, an element with status UP will have a CSS class **table-row-up**.

The corresponding classes can be defined in the *alignak_webui-items.css* file. Some example classes still exist in this file for the livestate states (eg. UP, OK, ...).

I a table column has a `visible` attribute defined as False, this column will not be displayed in the table.
To hide a column and allow the user to show this column thanks to the table column selector, you can use the `hidden` attribute and set it to True.


Field attributes:

    - `visible` (True): to include a column with this field
    - `hidden` (False): to hide the column in the table display

    - `type`: is the field type (see the known types list hereunder)
    - `content_type`: is the list items content type (eg. same as type) if the field is a *list*
    - `hint`: is a descrption of the field used as an help in the edition form
    - `required`: to indicate if the field must contain a value or may be empty
    - `allowed`: the list of the allowed values in the field (see hereafter for more explanations)

Field types:

    - `string` (default)
    - `integer`
    - `float`
    - `boolean`
    - `objectid`
    - `list`
    - `dict`
    - `point`

Field content types (for a list of items):

    - `string` (default)
    - `integer`
    - `float`
    - `boolean`
    - `objectid`
    - `dict`
    - `point`

Available formats:

    - `date`:
    - `on_off`:
    - `single`: only one value is allowed in the list field
    - `multiple`: several values are allowed in the list field

When the field `type` is a list, the `content_type` field must specify which type is to be used for the list items (eg. string, integer, ...).
If the `allowed` field contains a value, it may be:

    - inner://url
    - a comma separated list of the allowed values

If the edited item is a template, the `allowed_template` (if it is defined) is used instead of the `allowed` value. This to allow defining a different list of allowed values for the templates.

Table filtering
~~~~~~~~~~~~~~~~~~~~~~~~

Table filtering is available on a column basis; each column can have its own search parameter in the table header. The filtering field is an input field, a select field, ... according to the column type/format.


As much as possible, the table column format is determined by the application thanks to the columne *type* parameter.

The column format is used to choose the filtering input method. In some cases, it may be useful to specify the format.

The following rules apply:

    - as a default, *format* is **string** which means that the filtering input method is an input field

    - when *type* is **list**, the format method will automatically be a *select*. The *allowed* parameter defines the content of the allowed values in the select options.
    - *format* can be specified as a *select* (unique value) or *multiselect* (multiple select) input method
    - when *type* is **objectid**, the format method will automatically be a *select* that wil be populated with the related object names list

Available formats:

    - `date`:
    - `on_off`:
    - `select`:
    - `multiselect`:



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
