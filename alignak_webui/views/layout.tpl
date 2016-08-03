%from bottle import request
%from alignak_webui import _

%#Set default values
%setdefault('debug', False)
%setdefault('js', [])
%setdefault('css', [])
%setdefault('title', _('Untitled...'))
%# Current page may be refreshed or not (default is True)
%setdefault('refresh', True)
%setdefault('refresh_header', True)
%setdefault('current_user', None)
%setdefault('target_user', None)
%setdefault('sidebar', False)
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
      <meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">

      <title>{{title}}</title>

      <link href="/static/images/favicon.ico" rel="shortcut icon">

      <!-- Stylesheets
      ================================================== -->
      %if request.app.config.get('bootstrap4', '0') == '1':
      <link rel="stylesheet" href="/static/css/bootstrap4/bootstrap.min.css" >
      %else:
      <link rel="stylesheet" href="/static/css/bootstrap3/bootstrap.min.css" >
      <link rel="stylesheet" href="/static/css/bootstrap3/bootstrap-theme.min.css" >
      %end
      <link rel="stylesheet" href="/static/css/font-awesome.min.css" >
      <link rel="stylesheet" href="/static/css/typeahead.css" >
      <link rel="stylesheet" href="/static/css/daterangepicker.css" >

      <!-- alertify.js dialog boxes -->
      <link rel="stylesheet" href="/static/css/alertify.min.css" >
      <link rel="stylesheet" href="/static/css/alertify.bootstrap.min.css" >

      <!-- select2 -->
      <link rel="stylesheet" href="/static/css/select2.min.css" >

      <!-- selectize
      <link rel="stylesheet" href="/static/css/selectize.css" >
      <link rel="stylesheet" href="/static/css/selectize.bootstrap3.css" >-->

      <link rel="stylesheet" href="/static/css/timeline.css" >

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Material Design fonts -->
      <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Roboto:300,400,500,700">
      <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/icon?family=Material+Icons">

      <!-- Bootstrap Material Design -->
      <link rel="stylesheet" type="text/css" href="/static/css/material/bootstrap-material-design.css">
      <link rel="stylesheet" type="text/css" href="/static/css/material/ripples.min.css">
      -->
      %end

      <!-- jsTree jQuery plugin -->
      <link rel="stylesheet" href="/static/css/jstree/style.min.css" >

      <!-- Datatables jQuery plugin - download builder file
      <link rel="stylesheet" href="/static/css/datatables/all_datatables.min.css" >
      -->
      <!-- Datatable, CDN version:
      <link rel="stylesheet" type="text/css" href="https://cdn.datatables.net/v/dt/jszip-2.5.0/pdfmake-0.1.18/dt-1.10.12/b-1.2.1/b-colvis-1.2.1/b-flash-1.2.1/b-html5-1.2.1/b-print-1.2.1/r-2.1.0/se-1.2.0/datatables.min.css"/>
      -->
      <!-- Datatables jQuery plugin - separate files -->
      <link rel="stylesheet" href="/static/css/datatables/jquery.dataTables.min.css" >
      %if request.app.config.get('material_design', '0') == '1':
      <link rel="stylesheet" href="/static/css/datatables/dataTables.material.min.css" >
      %else:
      %if request.app.config.get('bootstrap4', '0') == '1':
      <link rel="stylesheet" href="/static/css/datatables/dataTables.bootstrap4.min.css" >
      %else:
      <link rel="stylesheet" href="/static/css/datatables/dataTables.bootstrap.min.css" >
      %end
      %end

      <link rel="stylesheet" href="/static/css/datatables/responsive.dataTables.min.css" >
      %if request.app.config.get('bootstrap4', '0') == '1':
      <link rel="stylesheet" href="/static/css/datatables/responsive.bootstrap4.min.css" >
      %else:
      <link rel="stylesheet" href="/static/css/datatables/responsive.bootstrap.min.css" >
      %end

      <link rel="stylesheet" href="/static/css/datatables/buttons.dataTables.min.css" >
      %if request.app.config.get('bootstrap4', '0') == '1':
      <link rel="stylesheet" href="/static/css/datatables/buttons.bootstrap4.min.css" >
      %else:
      <link rel="stylesheet" href="/static/css/datatables/buttons.bootstrap.min.css" >
      %end

      <link rel="stylesheet" href="/static/css/datatables/select.dataTables.min.css" >
      <link rel="stylesheet" href="/static/css/datatables/select.bootstrap.min.css" >

      <!-- Alignak Web UI -->
      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >

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
      %if request.app.config.get('bootstrap4', '0') == '1':
      <script type="text/javascript" src="/static/js/bootstrap4/bootstrap.min.js"></script>
      %else:
      <script type="text/javascript" src="/static/js/bootstrap3/bootstrap.min.js"></script>
      %end
      <!--
      <script type="text/javascript" src="/static/js/bootstrap-tab-bookmark.js"></script>
      -->
      <script type="text/javascript" src="/static/js/moment-with-langs.min.js"></script>
      <script type="text/javascript" src="/static/js/daterangepicker.js"></script>
      <script type="text/javascript" src="/static/js/jquery.jclock.js"></script>
      <script type="text/javascript" src="/static/js/jquery.jTruncate.js"></script>
      <script type="text/javascript" src="/static/js/typeahead.bundle.min.js"></script>
      <script type="text/javascript" src="/static/js/screenfull.js"></script>

      <!-- alertify.js dialog boxes -->
      <script type="text/javascript" src="/static/js/alertify.min.js"></script>
      <script type="text/javascript">
      alertify.defaults.transition = "slide";
      alertify.defaults.theme.ok = "btn btn-primary";
      alertify.defaults.theme.cancel = "btn btn-danger";
      alertify.defaults.theme.input = "form-control";
      </script>

      <!-- select2 -->
      <script type="text/javascript" src="/static/js/select2.full.min.js"></script>

      <!-- jQuery Chart -->
      <script type="text/javascript" src="/static/js/Chart.min.js"></script>

      <!-- jsTree jQuery plugin -->
      <script type="text/javascript" src="/static/js/jstree.min.js"></script>

      <!-- Datatables jQuery plugin - download builder file
      <script type="text/javascript" src="/static/js/datatables/all_datatables.min.js"></script>
      -->
      <!-- Datatable, CDN version:
      <script type="text/javascript" src="https://cdn.datatables.net/v/dt/jszip-2.5.0/pdfmake-0.1.18/dt-1.10.12/b-1.2.1/b-colvis-1.2.1/b-flash-1.2.1/b-html5-1.2.1/b-print-1.2.1/r-2.1.0/se-1.2.0/datatables.min.js"></script>
      -->
      <!-- Datatables jQuery plugin - separate files -->
      <script type="text/javascript" src="/static/js/datatables/jquery.dataTables.min.js"></script>
      %if request.app.config.get('material_design', '0') == '1':
      <script type="text/javascript" src="/static/js/datatables/dataTables.material.min.js"></script>
      %else:
      %if request.app.config.get('bootstrap4', '0') == '1':
      <script type="text/javascript" src="/static/js/datatables/dataTables.bootstrap4.min.js"></script>
      %else:
      <script type="text/javascript" src="/static/js/datatables/dataTables.bootstrap.min.js"></script>
      %end
      %end

      <script type="text/javascript" src="/static/js/datatables/dataTables.responsive.min.js"></script>
      %if request.app.config.get('bootstrap4', '0') == '1':
      <script type="text/javascript" src="/static/js/datatables/responsive.bootstrap4.min.js"></script>
      %else:
      <script type="text/javascript" src="/static/js/datatables/responsive.bootstrap.min.js"></script>
      %end

      <script type="text/javascript" src="/static/js/datatables/dataTables.buttons.min.js"></script>
      <script type="text/javascript" src="/static/js/datatables/buttons.bootstrap.min.js"></script>
      <script type="text/javascript" src="/static/js/datatables/buttons.colVis.min.js"></script>
      <script type="text/javascript" src="/static/js/datatables/buttons.flash.min.js"></script>
      <script type="text/javascript" src="/static/js/datatables/buttons.html5.min.js"></script>
      <script type="text/javascript" src="/static/js/datatables/buttons.print.min.js"></script>

      <script type="text/javascript" src="/static/js/datatables/dataTables.select.min.js"></script>

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
      %if refresh_header:
      <script>
      var header_refresh_period = {{int(request.app.config.get('header_refresh_period', '30'))}};
      </script>
      %else:
      var header_refresh_period = 0;
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
            <div id="page-content" class="{{'col-offset-sidebar' if sidebar else 'col-xs-12'}}">
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

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Bootstrap Material Design
      -->
      <script src="/static/js/material/material.min.js"></script>
      <script src="/static/js/material/ripples.min.js"></script>

      <script>
      $.material.init();
      </script>
      %end
   </body>
</html>
