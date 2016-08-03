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
      %if request.app.config.get('bootstrap4', '0') == '1':
      <link rel="stylesheet" href="/static/css/bootstrap4/bootstrap.min.css" >
      %else:
      <link rel="stylesheet" href="/static/css/bootstrap3/bootstrap.min.css" >
      <link rel="stylesheet" href="/static/css/bootstrap3/bootstrap-theme.min.css" >
      %end
      <link rel="stylesheet"href="/static/css/font-awesome.min.css" >

      <!-- alertify.js dialog boxes -->
      <link rel="stylesheet" href="/static/css/alertify.min.css" >
      <link rel="stylesheet" href="/static/css/alertify.bootstrap.min.css" >

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Material Design fonts -->
      <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Roboto:300,400,500,700">
      <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/icon?family=Material+Icons">

      <!-- Bootstrap Material Design -->
      <link rel="stylesheet" type="text/css" href="/static/css/material/bootstrap-material-design.css">
      <link rel="stylesheet" type="text/css" href="/static/css/material/ripples.min.css">
      -->
      %end

      <!-- Alignak Web UI -->
      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >

      %# Specific CSS files
      %for f in css:
      <link rel="stylesheet" href="/static/plugins/{{f}}">
      %end

      <!-- Scripts
      ================================================== -->
      <script type="text/javascript" src="/static/js/jquery-1.12.0.min.js"></script>
      <!--
      <script type="text/javascript" src="/static/js/jquery-ui-1.11.4.min.js"></script>
      -->
      %if request.app.config.get('bootstrap4', '0') == '1':
      <script type="text/javascript" src="/static/js/bootstrap4/bootstrap.min.js"></script>
      %else:
      <script type="text/javascript" src="/static/js/bootstrap3/bootstrap.min.js"></script>
      %end

      <script type="text/javascript" src="/static/js/moment-with-langs.min.js"></script>

      <script type="text/javascript" src="/static/js/jquery.jclock.js"></script>

      <!-- alertify.js dialog boxes -->
      <script type="text/javascript" src="/static/js/alertify.min.js"></script>
      <script type="text/javascript">
      alertify.defaults.transition = "slide";
      alertify.defaults.theme.ok = "btn btn-primary";
      alertify.defaults.theme.cancel = "btn btn-danger";
      alertify.defaults.theme.input = "form-control";
      </script>

      <script type="text/javascript" src="/static/js/screenfull.js"></script>

      <!-- jQuery Chart -->
      <script type="text/javascript" src="/static/js/Chart.min.js"></script>

      <!--
       Application globals ...
      -->
      <script>
      var dashboard_currently = false;
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

      <script src="/static/js/alignak_webui-layout.js"></script>
      <script src="/static/js/alignak_webui-actions.js"></script>
      <script src="/static/js/alignak_webui-bookmarks.js"></script>

      <!-- Specific scripts ... -->
      %# Specific Js files ...
      %for f in js:
      <script type="text/javascript" src="/static/plugins/{{f}}"></script>
      %end
   </head>

   <body>
      <div id="page-wrapper" class="container-fluid">
         <div class="row">
            <div id="page-content" class="col-xs-12">

               <!-- Page content -->
               <section class="content">
                  {{!base}}
               </section>
            </div>
         </div>
      </div>
      %include("_footer", commands=True)

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
