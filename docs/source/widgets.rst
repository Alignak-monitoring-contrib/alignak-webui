.. _develop:

Widgets and tables
===================

The Alignal WebUI proposes several widgets and tables.

Widgets
---------------

Hosts table
~~~~~~~~~~~~~~~~~~~~~~~~
Displays a simple list of the monitored hosts with their current status, business impact and check command.

Options:

    - number of elements
    - filter on host name and alias
    - filter on host parameters

Hosts chart
~~~~~~~~~~~~~~~~~~~~~~~~
Displays a pie chart for the monitored hosts with their current status.

Livestate table
~~~~~~~~~~~~~~~~~~~~~~~~
Displays a simple list of the monitored hosts with their current status and business impact. Some command buttons allow to send an acknowledge, schedule a downtime or request a re-check.

Options:

    - number of elements
    - filter on host name and alias
    - filter on host parameters

Livestate chart
~~~~~~~~~~~~~~~~~~~~~~~~
Displays a pie chart for the monitored hosts with their current status (same as Hosts chart).


Tables
---------------
All the elements have a table to display them. The table name is build with this simple rule: name_table. As examples:

    * hosts_table
    * livestate_table
    * logcheckresults_table
    * ...

Depending upon the element table configuration in its plugin, the table is searchable, orderable, ...

Host widgets
---------------

The host information page is built with *host widgets* declared in the hosts plugin. Each host widget is included in a tab of the host page navigation tab control.

Available host widgets are:

    * information
    * configuration
    * services
    * timeline
    * history
    * metrics

