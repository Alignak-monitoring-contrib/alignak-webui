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
%setdefault('target_user', None)
%setdefault('sidebar', True)
%setdefault('elts_per_page', 25)
%setdefault('pagination', None)
%setdefault('pagination_bottom', False)

%setdefault('edition_mode', False)

%username = current_user.get_username()
%if not target_user.is_anonymous():
%username = target_user.get_username()
%end

<!DOCTYPE html>
<html lang="en">
   <head>
      <!--
         %# Web UI application about content
         %from bottle import request
         %from alignak_webui import manifest
         This file is a part of {{request.app.config.get('name', 'WebUI')}}.

         {{request.app.config.get('about_name', manifest['name'])}} {{request.app.config.get('about_version', manifest['version'])}}, &copy;&nbsp;{{request.app.config.get('about_copyright', manifest['copyright'])}}
      -->

      <!--[if lt IE 9]>
      <script src="http://html5shim.googlecode.com/svn/trunk/html5.js"></script>
      <![endif]-->

      <meta charset="utf-8">
      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1">

      <title>{{title}}</title>

      <link href="/static/images/favicon.ico" rel="shortcut icon">

      <!-- Stylesheets
      ================================================== -->
      <link rel="stylesheet" href="/static/css/bootstrap.min.css" >
      <link rel="stylesheet" href="/static/css/bootstrap-theme.min.css" >
      <link rel="stylesheet" href="/static/css/font-awesome.min.css" >
      <link rel="stylesheet" href="/static/css/typeahead.css" >
      <link rel="stylesheet" href="/static/css/daterangepicker.css" >
      <link rel="stylesheet" href="/static/css/alertify.min.css" >
      <link rel="stylesheet" href="/static/css/alertify.bootstrap.min.css" >

      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >

      <link rel="stylesheet" href="/static/css/timeline.css" >

      <!-- jsTree jQuery plugin -->
      <link rel="stylesheet" href="/static/css/jstree/style.min.css" >

      <!-- Datatables jQuery plugin -->
      <link rel="stylesheet" href="/static/css/datatables.min.css" >

      %# Specific CSS files
      %for f in css:
      <link rel="stylesheet" href="/static/plugins/{{f}}">
      %end

      <!-- Opensearch
      ================================================== -->
      <link rel="search" type="application/opensearchdescription+xml" href="/opensearch.xml" title="Search for hosts and services in Alignak WebUI" />

      <!-- Scripts
      ================================================== -->
      <script type="text/javascript" src="/static/js/jquery-1.12.0.min.js"></script>
      <script type="text/javascript" src="/static/js/jquery-ui-1.11.4.min.js"></script>
      <script type="text/javascript" src="/static/js/bootstrap.min.js"></script>
      <script type="text/javascript" src="/static/js/bootstrap-tab-bookmark.js"></script>
      <script type="text/javascript" src="/static/js/moment-with-langs.min.js"></script>
      <script type="text/javascript" src="/static/js/daterangepicker.js"></script>
      <script type="text/javascript" src="/static/js/jquery.jclock.js"></script>
      <script type="text/javascript" src="/static/js/jquery.jTruncate.js"></script>
      <script type="text/javascript" src="/static/js/alertify.min.js"></script>
      <script type="text/javascript" src="/static/js/typeahead.bundle.min.js"></script>
      <script type="text/javascript" src="/static/js/screenfull.js"></script>

      <!-- jQuery Chart -->
      <script type="text/javascript" src="/static/js/Chart.min.js"></script>

      <!-- jsTree jQuery plugin -->
      <script type="text/javascript" src="/static/js/jstree.min.js"></script>

      <!-- Datatables jQuery plugin -->
      <script type="text/javascript" src="/static/js/datatables.min.js"></script>

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
                        <strong>Target user</strong>: {{target_user}}
                     </small></div>
                     <div><small>
                        <strong>Request</strong>:
                        <div class="panel panel-default">
                           <div class="panel-heading">
                              <a data-toggle="collapse" href="#panel2">Request['environ']:</a>
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
                              <a data-toggle="collapse" href="#panel3">Request['app']:</a>
                           </div>
                           <div id="panel3" class="panel-collapse collapse">
                              <ul class="list-group">
                                 %for k in request.app.__dict__:
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
            <div id="page-content" class="{{'col-offset-sidebar' if sidebar else 'col-md-12'}}">
               <!-- Page content header -->
               <section class="content-header">
                  %if pagination:
                  %include("_pagination_element", pagination=pagination, page=page, elts_per_page=elts_per_page, display_steps_form=True)
                  %end
               </section>

               <!-- Page content -->
               <section class="content">
                  {{!base}}
               </section>

               %if pagination_bottom:
               <!-- Page content footer -->
               <section class="content-footer">
                  %include("_pagination_element", pagination=pagination, page=page, elts_per_page=None)
               </section>
               %end
            </div>
         </div>
      </div>

      %include("_footer", commands=True)

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
   </body>
</html>
