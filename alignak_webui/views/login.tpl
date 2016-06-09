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

      <title>{{_('Application login page')}}</title>

      <link href="/static/images/favicon.ico" rel="shortcut icon">

      <!-- Stylesheets
      ================================================== -->
      <link href="/static/css/bootstrap.min.css" rel="stylesheet">
      <link href="/static/css/bootstrap-theme.min.css" rel="stylesheet">
      <link href="/static/css/font-awesome.min.css" rel="stylesheet">
      <link href="/static/css/alignak_webui.css" rel="stylesheet">

      <!-- Scripts
      ================================================== -->
      <script src="/static/js/jquery-1.12.0.min.js"></script>
      <script src="/static/js/bootstrap.min.js"></script>
   </head>

   <body>
      <div class="container" style="padding-top: 10vh;">
         <div class="col-sm-6 col-sm-offset-3">
            <div class="login-panel panel panel-default" style="padding: 2vh;">
               <div class="panel-heading">
                  <h2>{{request.app.config.get('about_name', manifest['name'])}} <small>{{_('version ')}}{{request.app.config.get('about_version', manifest['version'])}}</small></h2>
                  <center>
                     <img src="/static/images/{{request.app.config.get('company_logo', 'default_company.png')}}" alt="{{_('Company Logo')}}" style="width: 80%"/>
                  </center>
               </div>
               <div class="panel-body">
                  <form role="form" method="post" action="/login">
                     <fieldset>
                        <div class="form-group">
                           <input class="form-control" placeholder="{{_('Username')}}" name="username" type="text" autofocus=autofocus>
                        </div>
                        <div class="form-group">
                           <input class="form-control" placeholder="{{_('Password')}}" name="password" type="password" value="">
                        </div>

                        <button class="btn btn-lg btn-success btn-block" type="submit"><i class="fa fa-sign-in"></i> {{_('Login')}}</button>
                     </fieldset>
                  </form>
               </div>
               %if message or login_text:
               <div class="panel-footer">
                  %if login_text:
                  <h4>{{! login_text}}</h4>
                  %end
                  %if message:
                  <div id="login-message" class="alert alert-danger" role="alert">
                     <strong>{{_('Warning!')}}</strong>
                     {{message}}
                  </div>
                  %end
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
            console.debug('Submit login form: ', $(this));

            $('#login-message').hide();
         });
      });
      </script>
   </body>
</html>
