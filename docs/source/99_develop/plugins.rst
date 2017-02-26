.. raw:: LaTeX

    \newpage

.. _plugins:


Plugins
=============

The application loads **plugins**...
    TO BE COMPLETED!

Plugin structure
----------------
A plugin is a sub-directory in the application *plugins* directory (eg. *plugin*) which must contain a Python file named *plugin.py* that is imported by the application as a Python module.

All directories in the application *plugins* directory that do not match this requirement are ignored by the application.

The *plugin.py* file must declare a global class inherited from the application Plugin class::

    class PluginHosts(Plugin):
        """ Hosts plugin """
    
        def __init__(self, app, cfg_filenames=None):
            """
            Hosts plugin
    
            Overload the default get route to declare filters.
            """
            self.name = 'Hosts'
            self.backend_endpoint = 'host'
    
            self.pages = {
            ...
            }

            super(PluginHosts, self).__init__(app, cfg_filenames)


If the plugin is dedicated to a specific Alignak backend type of elements, it must declare which element is managed in a property *backend_endpoint*.::

    # Declare backend element endpoint
    self.backend_endpoint = 'host'

This will allow the application to route all the request for this type of element to this specific plugin. When an external application requests an hosts list, this plugin will be requested for the list.

If the plugin is to log some information, it must use this pattern::

    from logging import getLogger
    logger = getLogger(__name__)

As of it, the plugin logs will be included in the application main log stream.


Plugin configuration file
-------------------------
A plugin can have its own configuration file.

The application searches in several location for a configuration file:

    - /usr/local/etc/alignak-webui/plugin_NAME.cfg
    - /etc/alignak-webui/plugin_NAME.cfg
    - ~/alignak-webui/plugin_NAME.cfg
    - ./DIR/settings.cfg

Where NAME is the plugin name and DIR is the plugin directory.

The configuration file is built like an Ini file parsed thank to Python ConfigPaser::

        ; ------------------------------------------------------------------------------------------
        ; Plugin configuration file formatted as RFC822 standard
        ; ------------------------------------------------------------------------------------------

        [timeperiods]
        ; Plugin global configuration
        ;enabled=False

        ; A parameter in a section named like the plugin is seen as a direct parameter:
        ; timeperiods.variable is available as: self.plugin_parameters['variable']

        [test]
        variable2=2
        ; A parameter in another section is seen as a dict parameter:
        ; test.variable2 is available as: self.plugin_parameters['test']['variable2']

        ; The table and table. sections are specific:
        ; test.variable2 is available as: self.plugin_parameters['test']['variable2']
        [table]
        ; Table global configuration
        page_title=Timeperiods table (%d items)
        visible=True
        orderable=True
        editable=True
        selectable=True
        searchable=True
        responsive=False
        recursive=True

        [table.name]
        title=Timeperiod name
        type=string
        searchable=True
        regex=True
        orderable=True
        editable=True
        hint=This field is the time period name


Once parsed, the configuration file will make available an ordered dictionary in the plugin class: ``self.plugin_parameters``. The ``self.plugin_parameters['table']``, also aliased as ``self.table``, contains the table structure. Using the *element/config* route with a Web browser will output Json formatted data with the parameters.


Plugin table configuration
--------------------------
A plugin can have its own configuration file.

Whole table configuration
~~~~~~~~~~~~~~~~~~~~~~~~~
::

        ; Table global configuration
        [table]

        ; Items page title - used when displaying items table
        page_title=Hosts table (%d items)

        ; Templates page title - used when displaying templates table
        template_page_title=Hosts templates table (%d items)

        ; Obviously ;)
        visible=True

        ; The table may be printed
        printable=True

        ; The table may be ordered - then orderable fields are active
        orderable=True

        ; The table is editable - items can be selected for edition
        editable=True

        ; The table is selectable - rows can be selected
        selectable=True

        ; The table is searchable - searchable fields are active
        searchable=True

        ; The table is responsive or not - responsivenes adds an horizontal bar
        responsive=False

        ; The table is recursive (sic)- can navigate to a tree view
        recursive=True

Table field configuration
~~~~~~~~~~~~~~~~~~~~~~~~~
::

        ; Declare the field 'name' of the table
        [table.name]
        ; Title of the table column
        title=Timeperiod name
        type=string

        ; When displaying the templates table, only the fields having templates_table=true are displayed
        templates_table=true

        ; This field is searchable
        searchable=True
        ; If regex is true, search in the table with a regex, else search for strictly identical content
        regex=True

        ; The table may be ordered
        orderable=True

        ; Edition part
        ; ------------
        ; This field is editable
        editable=True
        ; The hint information is displayed in the edition form to explain the field content
        hint=This field is the time period name
        ; Required field
        required=true
        ; Field can be left empty or not
        empty=false
        ; Must contain a unique value
        unique=true

Plugin routes
-------------
A plugin may declare routes for the application Web server. The routes declaration is made through a global dictionary named *pages*.

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

A complete example of what is possible can be found in the **hosts** plugin. The source code is commented to explain what is done...
