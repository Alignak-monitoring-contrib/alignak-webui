%from bottle import request
%from alignak_webui import manifest

%setdefault('action_bar', False)

<!-- Page footer -->
<footer>
   <nav class="navbar navbar-default navbar-fixed-bottom">
         <!-- Page footer -->
         <div class="col-sm-12">
            <img src="/static/logo/{{request.app.config.get('webui_logo', 'logo_webui_xxs')}}" alt="{{_('WebUI Logo')}}" style="height: 18px">

            <small><em class="text-muted">
               {{! _('%s, version %s, &copy;&nbsp;%s') % (request.app.config.get('about_name', manifest['name']), request.app.config.get('about_version', manifest['version']), request.app.config.get('about_copyright', manifest['copyright']))}}
            </em></small>
         </div>
   </nav>
</footer>