%from bottle import request
%from alignak_webui import _

%#Set default values
%setdefault('debug', False)
%setdefault('js', [])
%setdefault('css', [])
%setdefault('title', _('Untitled...'))
%# Current page may be refreshed or not (default is True)
%setdefault('refresh', True)
%setdefault('current_user', None)
%setdefault('sidebar', False)
%setdefault('elts_per_page', 25)
%setdefault('pagination', None)
%setdefault('pagination_bottom', False)

%setdefault('edition_mode', False)

%username = current_user.get_username()

<!DOCTYPE html>
<html lang="en">
   <head>
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

      <!-- Alignak Web UI (included in the previous files list)
      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >
      -->

      %# Specific CSS files
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
            % if sidebar:
            <div class="{{'col-sidebar' if sidebar else ''}}">
               <!-- Sidebar menu ... -->
               %include("_sidebar.tpl")
            </div>
            %end

            <!-- All the content of #page-content is updated when the page refreshes. -->
            <div id="page-content" class="{{'col-offset-sidebar' if sidebar else 'col-xs-12'}}">
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

      %include("_modalWaiting")

      <!-- A modal div that will be filled and shown when we want forms ... -->
      <div id="mainModal" class="modal fade" role="dialog" aria-labelledby="{{_('Generic modal box')}}" aria-hidden="true">
         <div class="modal-dialog">
            <div class="modal-content">
               <div class="modal-header">
                  <h4 class="modal-title">{{_('Generic modal box')}}</h4>
               </div>
               <div class="modal-body">
                  <!-- Filled by application ... -->
               </div>
               <div class="modal-footer">
                  <a href="#" class="btn btn-default" data-dismiss="modal">{{_('Close')}}</a>
               </div>
            </div>
         </div>
      </div>

      <!-- Specific scripts ... -->
      %# Specific Js files ...
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
      });
      </script>
   </body>
</html>
