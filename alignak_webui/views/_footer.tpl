%from bottle import request
%from alignak_webui import manifest

<!-- Page footer -->
<footer class="page-footer navbar-default navbar-fixed-bottom">
   <div class="container-fluid">
      <!-- Page footer -->
      %if request.app.config.get('webui_logo', '/static/images/logo_webui_xxs.png'):
      <a href="{{request.app.config.get('about_url', manifest['doc'])}}" target="_blank">
         <img src="{{request.app.config.get('webui_logo', '/static/images/logo_webui_xxs.png')}}" alt="{{_('WebUI Logo')}}" style="height: 18px">
      </a>
      %end

      <a href="{{request.app.config.get('about_url', manifest['doc'])}}" target="_blank">
      <span><em class="text-muted">
         {{! _('%s, version %s, &copy;&nbsp;%s') % (request.app.config.get('about_name', manifest['name']), request.app.config.get('about_version', manifest['version']), request.app.config.get('about_copyright', manifest['copyright']))}}
      </em></span>
      </a>
   </div>
</footer>