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

      <title>{{_('Application login page')}}</title>

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

      <!--
         Application libraries
      -->
      %# WebUI Javascript files
      %for f in webui.js_list:
      <script type="text/javascript" src="{{f}}"></script>
      %end
   </head>

   <body>
      <div class="container" style="padding-top: 10vh;">
         <div class="col-xs-12 col-sm-6 col-sm-offset-3">
            <div class="login-panel panel panel-default" style="padding: 2vh;">
               <div class="panel-heading">
                  <h2>{{request.app.config.get('about_name', __manifest__['name'])}}</h2>
                  <h3>{{_('Version ')}}{{request.app.config.get('about_version', __manifest__['version'])}}</h3>
                  <center>
                     <img
                        src="{{request.app.config.get('app_logo', '/static/images/alignak_white_logo.png')}}"
                        style="{{request.app.config.get('login_logo_css', 'width:90%')}}"
                        alt="{{_('Alignak WebUI logo')}}"
                        title="{{request.app.config.get('app_logo_title', _('Alignak Web User Interface'))}}" />
                  </center>
               </div>
               <div class="panel-body">
                  <form role="form" method="post" action="/login">
                     <fieldset>
                        <div class="form-group label-floating">
                           <label for="username" class="control-label">{{_('Username')}}</label>
                           <input id="username" class="form-control" name="username" type="text" autofocus=autofocus>
                        </div>
                        <div class="form-group">
                           <label for="password" class="control-label">{{_('Password')}}</label>
                           <input id="password" class="form-control" name="password" type="password">
                        </div>

                        <button class="btn btn-lg btn-success btn-block btn-raised" type="submit"><i class="fa fa-sign-in"></i> {{_('Login')}}</button>
                     </fieldset>
                  </form>
                  %if message:
                  <div id="login-message" class="alert alert-danger" role="alert">
                     <strong>{{_('Warning!')}}</strong>
                     {{message}}
                  </div>
                  %end
               </div>
               %login_text=request.app.config.get('login_text', _('Welcome!<br> Log-in to use the application'))
               %if login_text:
               <div class="panel-footer">
                  <h4>{{! login_text}}</h4>
               </div>
               %end
            </div>
         </div>
      </div>

      %include("_footer")

      <script>
      $(document).ready(function() {
         /*
          * This event handler catches the submit event for the login form.
          */
         $('body').on("submit", 'form[action="/login"]', function (evt) {
            $('#login-message').hide();
         });

         $.material.init();
      });
      </script>
   </body>
</html>
