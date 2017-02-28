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

This section defines patterns used by the application to build the elements lists in the tables.
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

[currently]
-----------

This section defines patterns used by the application to build the currently view.
::


   ; Hosts states to include in the history graph
   ; States can be: up,down,unreachable,acknowledged,in_downtime
   ; Defaults to: up,down,unreachable,acknowledged,in_downtime
   ;hh_states=up,down,unreachable,acknowledged,in_downtime

   ; Hosts states history graph height
   ; Defaults to: 300
   ;hh_height=300

   ; Services states to include in the history graph
   ; States can be: ok,warning,critical,unknown,unreachable,acknowledged,in_downtime
   ; Defaults to: ok,warning,critical,unknown,acknowledged,in_downtime
   ;sh_states=ok,warning,critical,unknown,acknowledged,in_downtime

   ; Services states history graph height
   ; Defaults to: 300
   ;sh_height=300

   ; Hosts panel definition
   hosts_panel=<div id="panel_hosts" class="panel panel-default">
               <div class="panel-heading clearfix">
                 <strong>
                   <span class="fa fa-server"></span>
                   <span class="hosts-all text-white" data-count="##nb_elts##" data-problems="##nb_problems##">
                       &nbsp; ##nb_elts## hosts ##problems##
                   </span>
                 </strong>

                 <div class="pull-right">
                    <a href="#p_ph" class="btn btn-xs btn-raised" data-toggle="collapse">
                       <i class="fa fa-fw %%s"></i>
                    </a>
                 </div>
               </div>
               <div id="p_ph" class="panel-collapse collapse %%s">
                 <div class="panel-body">
                 ##hosts_counters##
                 <hr>
                 ##hosts_percentage##
                 </div>
               </div>
           </div>

   hosts_counters=
       <div class="row">
           <div class="col-xs-12 col-sm-9 text-center">
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##?search=ls_state:UP"
                 class="item_host_up" title="Up">
                 <span class="hosts-count">##nb_up##</span>
               </a>
             </div>
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##?search=ls_state:DOWN"
                 class="item_host_down" title="Down">
                 <span class="hosts-count">##nb_down##</span>
               </a>
             </div>
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##?search=ls_state:UNREACHABLE"
                 class="item_host_unreachable" title="Unreachable">
                 <span class="hosts-count">##nb_unreachable##</span>
               </a>
             </div>
           </div>

           <div class="col-xs-12 col-sm-3 text-center">
             <a href="##hosts_table_url##?search=ls_state:acknowledged"
               class="item_host_acknowledged" title="Acknowledged">
               <span class="hosts-count">##nb_acknowledged##</span>
             </a>
             <span>/</span>
             <a href="##hosts_table_url##?search=ls_state:IN_DOWNTIME"
               class="item_host_in_downtime" title="In downtime">
               <span class="hosts-count">##nb_in_downtime##</span>
             </a>
           </div>
       </div>

   hosts_percentage=
       <div class="row">
         <div class="col-xs-3 col-sm-3 text-center">
           <div class="col-xs-12 text-center">
             <a href="##hosts_table_url##" class="sla_hosts_##font##">
               <div>##pct_sla##%%</div>
               <i class="fa fa-4x fa-server"></i>
             </a>
           </div>
         </div>

         <div class="col-xs-9 col-sm-9 text-center">
           <div class="row">
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##?search=ls_state:UP"
                 class="item_host_up" title="Up">
                 <span class="hosts-count">##pct_up##%%</span>
               </a>
             </div>
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##?search=ls_state:DOWN"
                 class="item_host_down" title="Down">
                 <span class="hosts-count">##pct_down##%%</span>
               </a>
             </div>
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##?search=ls_state:UNREACHABLE"
                 class="item_host_unreachable" title="Unreachable">
                 <span class="hosts-count">##pct_unreachable##%%</span>
               </a>
             </div>
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url##" title="Fake">
                 <span class="hosts-count">&nbsp;</span>
               </a>
             </div>
             <div class="col-xs-4 text-center">
               <a href="##hosts_table_url## title="Fake">
                 <span class="hosts-count">&nbsp;</span>
               </a>
             </div>
           </div>

           <div class="row">
             <div class="col-xs-12 text-center">
               <a href="##hosts_table_url##?search=ls_state:acknowledged"
                 class="item_host_acknowledged" title="Acknowledged">
                 <span class="hosts-count">##pct_acknowledged##%%</span>
               </a>
               <span>/</span>
               <a href="##hosts_table_url##?search=ls_state:IN_DOWNTIME"
                 class="item_host_in_downtime" title="In downtime">
                 <span class="hosts-count">##pct_in_downtime##%%</span>
               </a>
             </div>
           </div>
         </div>
       </div>

   ; Services panel definition
   services_panel=
       <div id="panel_services" class="panel panel-default">
           <div class="panel-heading clearfix">
             <strong>
               <span class="fa fa-cube"></span>
               <span class="services-all text-default"
                       data-count="##nb_elts##"
                       data-problems="##nb_problems##">
                   &nbsp; ##nb_elts## services ##problems##
               </span>
             </strong>

             <div class="pull-right">
                 <a href="#p_ps" class="btn btn-xs btn-raised" data-toggle="collapse">
                     <i class="fa fa-fw %%s"></i>
                 </a>
             </div>
           </div>
           <div id="p_ps" class="panel-collapse collapse %%s">
             <div class="panel-body">
               ##services_counters##
               <hr>
               ##services_percentage##
             </div>
           </div>
       </div>

   services_counters=
       <div class="row">
           <div class="col-xs-12 col-sm-9 text-center">
             <div class="col-xs-2 text-center">
               <a href="##services_table_url##?search=ls_state:OK"
                 class="item_service_ok" title="Ok">
                 <span class="services-count">##nb_ok##</span>
               </a>
             </div>
             <div class="col-xs-2 text-center">
               <a href="##services_table_url##?search=ls_state:WARNING"
                 class="item_service_critical" title="Warning">
                 <span class="services-count">##nb_warning##</span>
               </a>
             </div>
             <div class="col-xs-2 text-center">
               <a href="##services_table_url##?search=ls_state:CRITICAL"
                 class="item_service_critical" title="Critical">
                 <span class="services-count">##nb_critical##</span>
               </a>
             </div>
             <div class="col-xs-2 text-center">
               <a href="##services_table_url##?search=ls_state:UNKNOWN"
                 class="item_service_unknown" title="Unknown">
                 <span class="services-count">##nb_unknown##</span>
               </a>
             </div>
             <div class="col-xs-2 text-center">
               <a href="##services_table_url##?search=ls_state:UNREACHABLE"
                 class="item_service_unreachable" title="Unreachable">
                 <span class="services-count">##nb_unreachable##</span>
               </a>
             </div>
           </div>

           <div class="col-xs-12 col-sm-3 text-center">
             <a href="##services_table_url##?search=ls_state:acknowledged"
               class="item_service_acknowledged" title="Acknowledged">
               <span class="services-count">##nb_acknowledged##</span>
             </a>
             <span>/</span>
             <a href="##services_table_url##?search=ls_state:IN_DOWNTIME"
               class="item_service_in_downtime" title="In downtime">
               <span class="services-count">##nb_in_downtime##</span>
             </a>
           </div>
       </div>


   services_percentage=
       <div class="row">
           <div class="col-xs-3 col-sm-3 text-center">
               <div class="col-xs-12 text-center">
                 <a href="##services_table_url##" class="sla_services_##font##">
                   <div>##pct_ok##%%</div>
                   <i class="fa fa-4x fa-cube"></i>
                 </a>
               </div>
               </div>

               <div class="col-xs-9 col-sm-9 text-center">
               <div class="row">
                 <div class="col-xs-4 text-center">
                   <a href="##services_table_url##?search=ls_state:OK"
                     class="item_service_ok" title="ok">
                     <span class="services-count">##pct_ok##%%</span>
                   </a>
                 </div>
                 <div class="col-xs-4 text-center">
                   <a href="##services_table_url##?search=ls_state:WARNING"
                     class="item_service_warning" title="warning">
                     <span class="services-count">##pct_warning##%%</span>
                   </a>
                 </div>
                 <div class="col-xs-4 text-center">
                   <a href="##services_table_url##?search=ls_state:CRITICAL"
                     class="item_service_critical" title="critical">
                     <span class="services-count">##pct_critical##%%</span>
                   </a>
                 </div>
                 <div class="col-xs-4 text-center">
                   <a href="##services_table_url##?search=ls_state:UNKNONW"
                     class="item_service_unknown" title="unknown">
                     <span class="services-count">##pct_unknown##%%</span>
                   </a>
                 </div>
                 <div class="col-xs-4 text-center">
                   <a href="##services_table_url##?search=ls_state:UNREACHABLE"
                     class="item_service_unreachable" title="unreachable">
                     <span class="services-count">##pct_unreachable##%%</span>
                   </a>
                 </div>
               </div>

               <div class="row">
                 <div class="col-xs-12 text-center">
                   <a href="##services_table_url##?search=ls_state:ACKNOWLEDGED"
                     class="item_service_acknowledged" title="acknowledged">
                     <span class="services-count">##pct_acknowledged##%%</span>
                   </a>
                   <span>/</span>
                   <a href="##services_table_url##?search=ls_state:IN_DOWNTIME"
                     class="item_service_in_downtime" title="in_downtime">
                     <span class="services-count">##pct_in_downtime##%%</span>
                   </a>
                 </div>
               </div>
           </div>
       </div>

[items] section
---------------

This section defines patterns used by the application to build the elements icons.
**TO BE COMPLETED**
