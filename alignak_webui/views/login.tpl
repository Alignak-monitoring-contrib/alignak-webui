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
      %if request.app.config.get('bootstrap4', '0') == '1':
      <link rel="stylesheet" href="/static/css/bootstrap4/bootstrap.min.css" >
      %else:
      <link rel="stylesheet" href="/static/css/bootstrap3/bootstrap.min.css" >
      <link rel="stylesheet" href="/static/css/bootstrap3/bootstrap-theme.min.css" >
      %end
      <link href="/static/css/font-awesome.min.css" rel="stylesheet">
      <link href="/static/css/alignak_webui.css" rel="stylesheet">

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Material Design fonts -->
      <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/css?family=Roboto:300,400,500,700">
      <link rel="stylesheet" type="text/css" href="//fonts.googleapis.com/icon?family=Material+Icons">

      <!-- Bootstrap Material Design -->
      <link rel="stylesheet" type="text/css" href="/static/css/material/bootstrap-material-design.css">
      <link rel="stylesheet" type="text/css" href="/static/css/material/ripples.min.css">
      -->
      %end

      <!-- Scripts
      ================================================== -->
      <script src="/static/js/jquery-1.12.0.min.js"></script>
      %if request.app.config.get('bootstrap4', '0') == '1':
      <script type="text/javascript" src="/static/js/bootstrap4/bootstrap.min.js"></script>
      %else:
      <script type="text/javascript" src="/static/js/bootstrap3/bootstrap.min.js"></script>
      %end

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Bootstrap Material Design -->
      <script src="/static/js/material/material.min.js"></script>
      <script src="/static/js/material/ripples.min.js"></script>
      %end
   </head>

   <body>
      <div class="container" style="padding-top: 10vh;">
         <div class="col-sm-6 col-sm-offset-3">
            <div class="login-panel panel panel-default" style="padding: 2vh;">
               <div class="panel-heading">
                  <h2>{{request.app.config.get('about_name', manifest['name'])}} <small>{{_('version ')}}{{request.app.config.get('about_version', manifest['version'])}}</small></h2>
                  <center>
                     <img src="{{company_logo}}" alt="{{_('Company Logo')}}" style="width: 80%"/>
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
               %if message or login_text:
               <div class="panel-footer">
                  %if login_text:
                  <h4>{{! login_text}}</h4>
                  %end
               </div>
               %end
            </div>
         </div>
      </div>

      %include("_footer")

      %if request.app.config.get('material_design', '0') == '1':
      <!-- Bootstrap Material Design -->
      <script src="/static/js/material/material.min.js"></script>
      <script src="/static/js/material/ripples.min.js"></script>
      <script>
      $.material.init();
      </script>
      %end

      <script>
      $(document).ready(function() {
         /*
          * This event handler catches the submit event for the login form.
          */
         $('body').on("submit", 'form[action="/login"]', function (evt) {
            $('#login-message').hide();
         });
      });
      </script>
   </body>
</html>
