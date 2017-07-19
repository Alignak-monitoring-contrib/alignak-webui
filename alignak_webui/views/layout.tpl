%from bottle import request
%import json

%#Set default values
%# debug the HTML templates
%setdefault('debug', False)

%# Extra css and jss to be loaded
%setdefault('js', [])
%setdefault('css', [])
%# Callback javascript function to call when extra files are loaded
%setdefault('callback', None)

%# Page title
%setdefault('title', _('Untitled...'))

%# Current page may be refreshed or not (default is True)
%setdefault('refresh', True)
%setdefault('current_user', None)
%setdefault('options_panel', False)
%setdefault('elts_per_page', 25)
%setdefault('pagination', None)
%setdefault('pagination_bottom', False)

%setdefault('edition_mode', False)

%username = current_user.get_username()

<!doctype html>
<html lang="en">
   <head>
      <!--
      <!--
         %# Web UI application about content
         %from bottle import request
         %from alignak_webui import __manifest__
         This file is a part of {{request.app.config.get('name', 'WebUI')}}.

         {{request.app.config.get('about_name', __manifest__['name'])}} {{request.app.config.get('about_version', __manifest__['version'])}}, &copy;&nbsp;{{request.app.config.get('about_copyright', __manifest__['copyright'])}}
      -->

      <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
      <![endif]-->

      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

      <title>{{title}}</title>

      <link href="/static/images/favicon.ico" rel="shortcut icon">

      <!-- Stylesheets -->
      %# WebUI CSS files
      %for f in webui.css_list:
      <link rel="stylesheet" href="{{f}}">
      %end

      <!-- Specific page stylesheets...-->
      %for f in css:
      <link rel="stylesheet" href="/static/plugins/{{f}}">
      %end

      <!-- Opensearch
      ================================================== -->
      <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="Search for hosts and services in Alignak WebUI" />

      <!--
         Application libraries
      -->
      %# WebUI Javascript files
      %for f in webui.js_list:
      <script type="text/javascript" src="{{f}}"></script>
      %end

      <!--
       Application globals ...
      -->
      <script>
      var dashboard_currently = false;
      var sound_activated = false;
      </script>

      <!--
       Application scripts ...
      -->
      %if refresh:
      <script>
      var app_refresh_period = {{int(request.app.config.get('refresh_period', '60'))}};
      </script>
      <script src="/static/js/alignak_webui-refresh.js"></script>
      %end

      <script src="/static/js/alignak_webui-external.js"></script>
      <script src="/static/js/alignak_webui-layout.js"></script>
      <script src="/static/js/alignak_webui-actions.js"></script>
      <script src="/static/js/alignak_webui-bookmarks.js"></script>
   </head>

   <body>
      %include("_header")

      <div id="page-wrapper" class="container-fluid header-page">
         %#debug=True
         %if debug:
         <div class="debug">
            <div class="panel-group">
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#panel1"><i class="fa fa-bug"></i> Global elements</a>
                     </h4>
                  </div>
                  <div id="panel1" class="panel-collapse collapse">
                     <div><small>
                        <strong>User</strong>: {{current_user}}
                     </small></div>
                     <div><small>
                        <strong>Request</strong>:
                        <div class="panel panel-default">
                           <div class="panel-heading">
                              <a data-toggle="collapse" href="#panel4">request['headers']:</a>
                           </div>
                           <div id="panel4" class="panel-collapse collapse">
                              <ul class="list-group">
                                 %for k in request.headers:
                                    <li class="list-group-item"><small>{{k}} - {{request.headers[k]}}</small></li>
                                 %end
                              </ul>
                           </div>
                        </div>
                        <div class="panel panel-default">
                           <div class="panel-heading">
                              <a data-toggle="collapse" href="#panel2">request['environ']:</a>
                           </div>
                           <div id="panel2" class="panel-collapse collapse">
                              <ul class="list-group">
                                 %for k in request.environ:
                                    <li class="list-group-item"><small>{{k}} - {{request.environ[k]}}</small></li>
                                 %end
                              </ul>
                           </div>
                        </div>
                        <div class="panel panel-default">
                           <div class="panel-heading">
                              <a data-toggle="collapse" href="#panel3">request['app'] / request.environ['bottle.app']:</a>
                           </div>
                           <div id="panel3" class="panel-collapse collapse">
                              <ul class="list-group">
                                 %for k in request.environ['bottle.app'].__dict__:
                                    <li class="list-group-item"><small>{{k}} - {{request.app.__dict__[k]}}</small></li>
                                 %end
                              </ul>
                           </div>
                        </div>
                     </small></div>
                     <div><small>
                        <strong>WebUI</strong>:
                        <div class="panel panel-default">
                           <div class="panel-heading">
                              <a data-toggle="collapse" href="#panel4">WebUI application:</a>
                           </div>
                           <div id="panel4" class="panel-collapse collapse">
                              <ul class="list-group">
                                 %for k in webui.__dict__:
                                    <li class="list-group-item"><small>{{k}} - {{webui.__dict__[k]}}</small></li>
                                 %end
                              </ul>
                           </div>
                        </div>
                     </small></div>
                     <div><small>
                        <strong>Beaker session</strong>:
                        <div class="panel panel-default">
                           <div class="panel-heading">
                              <a data-toggle="collapse" href="#panel5">Beaker session:</a>
                           </div>
                           <div id="panel5" class="panel-collapse collapse">
                              <ul class="list-group">
                                 %for k in request.environ['beaker.session'].__dict__:
                                    <li class="list-group-item"><small>{{k}} - {{request.environ['beaker.session'].__dict__[k]}}</small></li>
                                 %end
                              </ul>
                           </div>
                        </div>
                     </small></div>
                  </div>
               </div>
            </div>
         </div>
         %end

         <div class="row">
            % if options_panel:
            <div id="options-panel">
               <div class="card slider-card">
                  <h3>Options</h3>

                 <div class="user">
                     <img src="/static/images/default_user.png" alt="Esempio" class="img-thumbnail"><br>
                     <a href="http://www.lombardoandrea.com" target="_blank" class="navbar-link">Andrea Lombardo</a>
                 </div>

                 <div class="list-group">

                     <a href="#item-1" class="list-group-item" data-toggle="collapse">Item 1</a>

                     <div class="list-group collapse" id="item-1">
                         <a href="#" class="list-group-item">Item 1 di 1</a>
                         <a href="#" class="list-group-item">Item 2 di 1</a>
                         <a href="#item-1-1" class="list-group-item" data-toggle="collapse">Item 3 di 1</a>

                         <div class="list-group collapse" id="item-1-1">
                             <a href="#" class="list-group-item">Item 1 di 1.3</a>
                             <a href="#" class="list-group-item">Item 2 di 1.3</a>
                             <a href="#" class="list-group-item">Item 3 di 1.3</a>
                         </div>

                     </div>

                     <a href="#item-2" class="list-group-item" data-toggle="collapse">Item 2</a>

                     <div class="list-group collapse" id="item-2">
                         <a href="#" class="list-group-item">Item 1 di 2</a>
                         <a href="#" class="list-group-item">Item 2 di 2</a>
                         <a href="#" class="list-group-item">Item 3 di 2</a>
                     </div>

                     <a href="#item-3" class="list-group-item" data-toggle="collapse">Item 3</a>

                     <div class="list-group collapse" id="item-3">
                         <a href="#" class="list-group-item">Item 1 di 3</a>
                         <a href="#" class="list-group-item">Item 2 di 3</a>
                         <a href="#item-3-1" class="list-group-item" data-toggle="collapse">Item 3 di 3</a>

                         <div class="list-group collapse" id="item-3-1">
                             <a href="#" class="list-group-item">Item 1 di 3.3</a>
                             <a href="#" class="list-group-item">Item 2 di 3.3</a>
                             <a href="#" class="list-group-item">Item 3 di 3.3</a>
                         </div>

                     </div>

                     <a href="#item-4" class="list-group-item" data-toggle="collapse">Item 4</a>

                     <div class="list-group collapse" id="item-4">
                         <a href="#" class="list-group-item">Item 1 di 4</a>
                         <a href="#" class="list-group-item">Item 2 di 4</a>
                         <a href="#" class="list-group-item">Item 3 di 4</a>
                     </div>

                 </div>
               </div>
            </div>

            <!-- Options slder
            <aside id="options-panel">
               <a href="#" data-action="options-slider-open"><span class="fa fa-gear"></span>{{_('Options')}}</a>

               <div style="overflow-y:auto; max-height:100%; padding:10px; display:none;">
                  <h3>Options</h3>

                  <form class="hidden-xs" method="get" action="/all">
                    <div class="dropdown form-group text-left">
                      <button class="btn btn-default dropdown-toggle" type="button" id="filters_menu" data-toggle="dropdown" aria-expanded="true"><i class="fa fa-filter"></i><span class="hidden-sm hidden-xs hidden-md"> Filters</span> <span class="caret"></span></button>
                      <ul class="dropdown-menu" role="menu" aria-labelledby="filters_menu">
                        <li role="presentation"><a role="menuitem" href="/all?search=&title=All resources">All resources</a></li>
                        <li role="presentation"><a role="menuitem" href="/all?search=type:host&title=All hosts">All hosts</a></li>
                        <li role="presentation"><a role="menuitem" href="/all?search=type:service&title=All services">All services</a></li>
                        <li role="presentation" class="divider"></li>
                        <li role="presentation"><a role="menuitem" href="/all?search=isnot:0 isnot:ack isnot:downtime&title=New problems">New problems</a></li>
                        <li role="presentation"><a role="menuitem" href="/all?search=is:ack&title=Acknowledged problems">Acknowledged problems</a></li>
                        <li role="presentation"><a role="menuitem" href="/all?search=is:downtime&title=Scheduled downtimes">Scheduled downtimes</a></li>
                        <li role="presentation" class="divider"></li>
                        <li role="presentation"><a role="menuitem" href="?search=bp:>=5">.../...</a></li>
                        <li role="presentation" class="divider"></li>
                        <li role="presentation"><a role="menuitem" onclick="display_modal('/modal/helpsearch')"><strong><i class="fa fa-question-circle"></i> Search syntax</strong></a></li>
                      </ul>
                    </div>
                    <div class="form-group">
                      <label class="sr-only" for="search">Filter</label>
                      <div class="input-group">
                        <span class="input-group-addon hidden-xs hidden-sm"><i class="fa fa-search"></i></span>
                        <input class="form-control" type="search" id="search_worldmap" name="search_worldmap" value="{{ search_string }}">
                      </div>
                    </div>
                  </form>

               </div>
            </aside>
            -->
            %end

            <!-- All the content of #page-content is updated when the page refreshes. -->
            <div id="page-content" class="col-xs-12">
               <!-- Page content header -->
               <section class="content-header">
                  %if pagination:
                  %include("_pagination_element", pagination=pagination, elts_per_page=elts_per_page, display_steps_form=True)
                  %end
               </section>

               <!-- Page content -->
               <section class="content">
                  {{!base}}
               </section>

               %if pagination_bottom:
               <!-- Page content footer -->
               <section class="content-footer">
                  %include("_pagination_element", pagination=pagination, elts_per_page=None)
               </section>
               %end
            </div>
         </div>
      </div>

      %include("_footer", commands=True)

      %include("modal_waiting")

      %include("_main_modal")

      <!-- Specific page scripts ...-->
      <!--<script>
         import L from 'leaflet';
         import { GeoSearchControl, OpenStreetMapProvider } from 'leaflet-geosearch';
      </script>-->
      %for f in js:
      <script type="text/javascript" src="/static/plugins/{{f}}"></script>
      %end

      <script>
      $(document).ready(function() {
         // Initialize alertify library
         alertify.defaults.transition = "slide";
         alertify.defaults.theme.ok = "btn btn-primary";
         alertify.defaults.theme.cancel = "btn btn-danger";
         alertify.defaults.theme.input = "form-control";

         $.material.init();

         %if callback:
         window.setTimeout(function () {
            console.log("Plugin callback function: {{callback}}");
            {{callback}}();
         }, 100);
         %end

         % if options_panel:
         $('#options-panel').BootSideMenu({
            // 'left' or 'right'
            side: "left",
            // animation speed
            duration: 500,
            // restore last menu status on page refresh
            remember: true,
            // auto close
            autoClose: false,
            // push the whole page
            pushBody: true,
            // close on click
            closeOnClick: true,
            // width
            width: "30%",
            onTogglerClick: function () {
               //code to be executed when the toggler arrow was clicked
            },
            onBeforeOpen: function () {
               //code to be executed before menu open
            },
            onBeforeClose: function () {
               //code to be executed before menu close
            },
            onOpen: function () {
               //code to be executed after menu open
            },
            onClose: function () {
               //code to be executed after menu close
            },
            onStartup: function () {
               //code to be executed when the plugin is called
            }
         });
         %end
      });
      </script>
   </body>
</html>
