%#Set default values
%setdefault('js', [])
%setdefault('css', [])
%setdefault('title', _('Untitled...'))

%# Current page may be refreshed or not
%setdefault('refresh', True)

<!DOCTYPE html>
<html lang="en">
   <head>
      <meta charset="utf-8">
      <title>{{title}}</title>

      <meta http-equiv="X-UA-Compatible" content="IE=edge">
      <meta name="viewport" content="width=device-width, initial-scale=1">

      <!--
         This file is a part of {{webui.app_name}}.

         {{webui.app_name}} {{webui.app_version}}, &copy;&nbsp;{{webui.app_copyright}}
      -->

      <link href="/static/images/favicon.ico" rel="shortcut icon">

      <!--[if lt IE 9]>
      <script src="/static/js/ie9/html5.js"></script>
      <script src="/static/js/ie9/json2.js"></script>
      <![endif]-->

      <!-- Stylesheets
      ================================================== -->
      <link rel="stylesheet"href="/static/css/bootstrap.min.css" >
      <link rel="stylesheet"href="/static/css/bootstrap-theme.min.css" >
      <link rel="stylesheet"href="/static/css/font-awesome.min.css" >
      <link rel="stylesheet" href="/static/css/alertify.css" >

      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >

      %# Specific CSS files
      %for f in css:
      <link rel="stylesheet" type="text/css" href="/plugins/{{f}}">
      %end

      <!-- Scripts
      ================================================== -->
      <script src="/static/js/jquery-1.12.0.min.js"></script>
      <script src="/static/js/jquery-ui-1.11.4.min.js"></script>
      <script src="/static/js/bootstrap.min.js"></script>

      <script src="/static/js/moment.min.js"></script>

      <script src="/static/js/jquery.jclock.js"></script>
      <script src="/static/js/alertify.js"></script>
      <script src="/static/js/screenfull.js"></script>

      <!--
       Shinken globals ...
      -->
      <script>
      var dashboard_currently = false;
      </script>

      <!--Shinken ones : refresh pages -->
      %if refresh:
      <script>
      var app_refresh_period = {{webui.refresh_period}};
      </script>
      <script src="/static/js/alignak_webui-refresh.js"></script>
      %end
      <script src="/static/js/alignak_webui-layout.js"></script>
      <script src="/static/js/alignak_webui-actions.js"></script>
      <script src="/static/js/alignak_webui-bookmarks.js"></script>
   </head>

   <body>
      <div id="page-wrapper" class="container-fluid">
         <div class="row">
            <div id="page-content" class="col-lg-12">

               <!-- Page content -->
               <section class="content">
                  %setdefault('base', 'nothing')
                  {{!base}}
               </section>
            </div>
         </div>
      </div>
      %include("_footer", commands=True)

      <!--
       Specific scripts ...
      -->
      %# Specific Js files ...
      %for f in js:
      <script type="text/javascript" src="/plugins/{{f}}"></script>
      %end
   </body>
</html>
