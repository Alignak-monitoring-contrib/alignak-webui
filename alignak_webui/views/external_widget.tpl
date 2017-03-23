%from bottle import request

%#Set default values
%setdefault('debug', False)
%setdefault('title', request.app.config.get('title', _('Untitled...')))

%setdefault('embedded', False)
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('embedded_element', _('No content embedded'))
<!DOCTYPE html>
<html lang="en">
   <head>
      <!--
         %# Web UI application about content
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

      <!-- Stylesheets -->
      %# WebUI CSS files
      %for f in webui.css_list:
      <link rel="stylesheet" href="{{f}}">
      %end
      <!--
         Application libraries
      -->
      %# WebUI Javascript files
      %for f in webui.js_list:
      <script type="text/javascript" src="{{f}}"></script>
      %end
   </head>

   <body>
      <section>
         {{! embedded_element}}
      </section>
   </body>
</html>
