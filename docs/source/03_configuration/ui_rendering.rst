.. raw:: LaTeX

    \newpage

.. _configuration_ui_rendering:

UI rendering
============


Alignak WebUI is highly configurable and even some UI rendering can be configured to best suit the user's needs. This is what is introduced in the next chapters; each one made for a specific section of the Alignak WebUI configuration file.

[Alignak-WebUI] section
-----------------------

    * **livestate_layout**, configure the layout to be used in the livestate view: single table, multiple panels or tabbed view, for each business impact level

Some examples:

.. figure:: ../images/livestate-1.png
   :scale: 50 %
   :alt: Livestate rendering example - table

   Default configuration

.. figure:: ../images/livestate-2.png
   :scale: 50 %
   :alt: Livestate rendering example - panels

   Panels layout

.. figure:: ../images/livestate-3.png
   :scale: 50 %
   :alt: Livestate rendering example - tabs

   Tabs


[on_off]
--------
This section allows to configure how the on/off (eg. enabled/disabled) is represented in the Web UI.
::

    [on_off]
    ; Global element to be included in the HTML and including the items and the text
    on=<span title="##title##" class="fa fa-fw fa-check text-success">##message##</span>

    ; Element to be included for each BI count
    off=<span title="##title##" class="fa fa-fw fa-close text-danger">##message##</span>


[business_impact]
-----------------
This section allows to configure how the business impact of an element is represented in the Web UI.
::

    [business_impact]
    ; Global element to be included in the HTML and including the items and the text
    ;global=<span class="text-default">##items##</span><span>&nbsp;##text##</span>

    ; Element to be included for each BI count
    ;item=<span class="fa fa-trophy"></span>
    ; If item is empty, then the following unique is used in place
    ;item=

    ; Unique element
    ; ##bi## will be replaced with the business impact level value
    ;unique=<div style="display: inline; font-size:0.9em;" title="##text##"><span class="fa-stack"><span class="fa fa-circle fa-stack-2x"></span><span class="fa fa-stack-1x fa-inverse">##bi##</span></span></div>

    ; Number of elements to remove from the real business impact
    ; 0 is meaning that the defined item will be repeated twice for BI=2, third for BI=3
    ; 2 is meaning that the defined item will not be repeated for BI=2, and once for BI=3
    ;less=0

Some examples:

.. figure:: ../images/bi-0.png
   :scale: 50 %
   :alt: BI rendering example

   Default configuration

.. figure:: ../images/bi-1.png
   :scale: 50 %
   :alt: BI rendering example

   Changed color

.. figure:: ../images/bi-2.png
   :scale: 50 %
   :alt: BI rendering example

   Icon and text

.. figure:: ../images/bi-3.png
   :scale: 50 %
   :alt: BI rendering example

   Text only

[buttons]
---------

This section defines patterns used by the application to build the buttons commands toolbar.
::

    [buttons]
    ; First solution: a buttons group
    ; Global element to be included in the HTML
    ;livestate_commands=<div class="btn-group btn-group-xs btn-group-raised" role="group" data-type="actions" title="##title##">##commands##</div>
    ; Each command element to be included in the HTML
    ;livestate_command=<button class="btn btn-default" data-type="action" data-action="##action##" data-toggle="tooltip" data-placement="top" title="##title##" data-element_type="##type##" data-name="##name##" data-element="##id##" ##disabled##><i class="fa fa-##icon##"></i></button>

    ; Second solution (preferred one): a buttons dropdown list
    ; Global element to be included in the HTML
    livestate_commands=<div class="btn-group btn-group-xs" role="group" data-type="actions" title="##title##"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">##title## <span class="caret"></span></button><ul class="dropdown-menu">##commands##</ul></div>
    ; Each command element to be included in the HTML
    livestate_command=<li><button class="btn btn-default" data-type="action" data-action="##action##" data-toggle="tooltip" data-placement="top" title="##title##" data-element_type="##type##" data-name="##name##" data-element="##id##" ##disabled##><i class="fa fa-##icon##"></i>&nbsp;&nbsp;##title##</button></li>

[tables.lists]
--------------

This section defines patterns used by the application to build the elemnts lists in the tables.
::

    [tables.lists]
    ; Button to display the list
    button=<button class="btn btn-xs btn-raised" data-toggle="collapse" data-target="#list_##type##_##id##" aria-expanded="false">##title##</button><div class="collapse" id="list_##type##_##id##">##content##</div>

    ; Global element to be included in the HTML for the list
    list=<ul class="list-group">##content##</ul>

    ; Each command element to be included in the HTML list
    item=<li class="list-group-item"><span class="fa fa-check">&nbsp;##content##</span></li>

    ; Unique element to be included in the HTML list if the list contains only one element
    unique=##content##

[items] section
---------------

This section defines patterns used by the application to build the elements icons.
**TO BE COMPLETED**
