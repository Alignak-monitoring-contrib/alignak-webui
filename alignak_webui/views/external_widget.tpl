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
         %from alignak_webui import __manifest__
         This file is a part of {{request.app.config.get('name', 'WebUI')}}.

         {{request.app.config.get('about_name', __manifest__['name'])}} {{request.app.config.get('about_version', __manifest__['version'])}}, &copy;&nbsp;{{request.app.config.get('about_copyright', __manifest__['copyright'])}}
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
      <link rel="stylesheet"href="/static/css/bootstrap.min.css" >
      <link rel="stylesheet"href="/static/css/font-awesome.min.css" >

      <!--
      <link rel="stylesheet" href="/static/css/alignak_webui.css" >
      <link rel="stylesheet" href="/static/css/alignak_webui-items.css" >
      -->

      <!-- Scripts
      ================================================== -->
      <script type="text/javascript" src="/static/js/jquery-1.12.0.min.js"></script>
      <script type="text/javascript" src="/static/js/bootstrap.min.js"></script>

      <!-- jQuery Chart -->
      <script type="text/javascript" src="/static/js/Chart.min.js"></script>
   </head>

   <body>
      <section>
         {{! embedded_element}}
      </section>
   </body>
</html>
