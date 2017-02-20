%from bottle import request

%#Set default values
%setdefault('debug', False)
%setdefault('js', [])
%setdefault('css', [])
%setdefault('title', _('Untitled...'))
%# Current page may be refreshed or not (default is True)
%setdefault('refresh', True)
%setdefault('current_user', None)
%setdefault('sidebar', True)
%setdefault('elts_per_page', 25)
%setdefault('pagination', None)
%setdefault('pagination_bottom', False)

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
      <meta name="viewport" content="width=device-width, initial-scale=1">

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

      <!-- Specific scripts ... -->
      %# Specific Js files ...
      %for f in js:
      <script type="text/javascript" src="/static/plugins/{{f}}"></script>
      %end
   </head>

   <body>
      <header>
         <nav id="topbar" class="navbar navbar-fixed-top">
            <div class="navbar-header">
               <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapsible-part">
                  <span class="sr-only">{{_('Toggle navigation')}}</span>
                  <span class="icon-bar"></span>
                  <span class="icon-bar"></span>
                  <span class="icon-bar"></span>
               </button>
               <a class="navbar-brand" href="/">
                  <img
                     src="{{request.app.config.get('app_logo', '/static/images/alignak_white_logo.png')}}"
                     style="{{request.app.config.get('app_logo_css', '')}}"
                     alt="{{_('Alignak WebUI logo')}}"
                     title="{{request.app.config.get('app_logo_title', _('Alignak Web User Interface'))}}" />
               </a>

               <ul class="nav navbar-nav navbar-left">
               <li class="pull-left">
                  <a tabindex="0" role="button"
                     data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Go back to the dashboard')}}" href="/dashboard">
                     <span class="fa fa-home"></span>
                     <span class="sr-only">{{_('Go back to the main dashboard')}}</span>
                  </a>
               </li>
               <li class="pull-left">
                  <a tabindex="0" role="button"
                     data-action="fullscreen-request"
                     data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Fullscreen page')}}" href="#">
                     <span class="fa fa-desktop"></span>
                     <span class="sr-only">{{_('Fullscreen page')}}</span>
                  </a>
               </li>
               %if request.app.config.get('play_sound', 'no') == 'yes':
               <li id="sound_alerting" class="pull-left">
                  <a tabindex="0" role="button"
                     data-action="toggle-sound-alert"
                     data-toggle="tooltip" data-placement="bottom"
                     title="{{_('Sound alert on/off')}}" href="#">
                     <span class="fa fa-music"></span>
                     <span class="sr-only">{{_('Change sound playing state')}}</span>
                  </a>
               </li>
               %end
            </ul>
            </div>

            <!-- Right part ... -->
            <div id="navbar-collapsible-part" class="collapse navbar-collapse">
                <ul class="nav navbar-nav navbar-left">
                  <li class="hidden-xs" id="loading" style="display: none;">
                     <a href="#">
                        <span class="fa fa-spinner fa-pulse fa-1x"></span>
                        <span class="sr-only">{{_('Loading...')}}</span>
                     </a>
                  </li>
                </ul>

                <ul class="nav navbar-nav navbar-right">
            %if refresh:
            <li id="refresh_active">
               <a data-action="toggle-page-refresh"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Refresh page every %d seconds.') % (int(request.app.config.get('refresh_period', '60')))}}"
                  href="#">
                  <span class="fa fa-refresh"></span>
                  <span class="sr-only">{{_('Change page refresh state')}}</span>
               </a>
            </li>
            %end

                  <li>
                     <a class="font-darkgrey"
                        title="{{_('Current date / time')}}"
                        href="#">
                       <span id="date"></span>&nbsp;&hyphen;&nbsp;<span id="clock"></span>
                     </a>
                  </li>
                </ul>
            </div>
         </nav>
      </header>

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

      %include("modal_waiting")

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
