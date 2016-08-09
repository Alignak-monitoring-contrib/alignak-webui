%from bottle import request
%from alignak_webui import _

%#Set default values
%setdefault('debug', False)
%setdefault('title', _('Untitled...'))

%setdefault('embedded', False)
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('embedded_element', _('No content embedded'))
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
      %end
      <link rel="stylesheet"href="/static/css/font-awesome.min.css" >

      <!-- Datatables jQuery plugin - separate files -->
      <link rel="stylesheet" href="/static/css/datatables/jquery.dataTables.min.css" >
      %if request.app.config.get('material_design', '1') == '1':
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

      <!--
      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >
      -->

      <!-- Scripts
      ================================================== -->
      <script type="text/javascript" src="/static/js/jquery-1.12.0.min.js"></script>
      %if request.app.config.get('bootstrap4', '0') == '1':
      <script type="text/javascript" src="/static/js/bootstrap4/bootstrap.min.js"></script>
      %else:
      <script type="text/javascript" src="/static/js/bootstrap3/bootstrap.min.js"></script>
      %end

      <!-- selectize -->
      <script type="text/javascript" src="/static/js/selectize.min.js"></script>

      <!-- jQuery Chart -->
      <script type="text/javascript" src="/static/js/Chart.min.js"></script>

      <!-- Datatables jQuery plugin -->
      <!-- Datatables jQuery plugin - separate files -->
      <script type="text/javascript" src="/static/js/datatables/jquery.dataTables.min.js"></script>
      %if request.app.config.get('material_design', '1') == '1':
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
   </head>

   <body>
      <section>
         {{! embedded_element}}
      </section>

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Bootstrap Material Design -->
      <script src="/static/js/material/material.min.js"></script>
      <script src="/static/js/material/ripples.min.js"></script>

      <script>
      $.material.init();
      </script>
      %end
   </body>
</html>
