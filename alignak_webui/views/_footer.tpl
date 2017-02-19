%from bottle import request
%from alignak_webui import __manifest__

<!-- Page footer -->
<footer class="page-footer navbar-default navbar-fixed-bottom">
   <div class="container-fluid">
      %if request.app.config.get('webui_logo', '/static/images/logo_webui_xxs.png'):
      <a href="{{request.app.config.get('about_url', __manifest__['doc'])}}" target="_blank">
         <img src="{{request.app.config.get('webui_logo', '/static/images/logo_webui_xxs.png')}}" alt="{{_('WebUI Logo')}}" style="height: 18px">
      </a>
      %end

      <a href="{{request.app.config.get('about_url', __manifest__['url'])}}" target="_blank">
      <span><em class="text-muted">
         {{! _('%s, version %s, &copy;&nbsp;%s') % (request.app.config.get('about_name', __manifest__['name']), request.app.config.get('about_version', __manifest__['version']), request.app.config.get('about_copyright', __manifest__['copyright']))}}
      </em></span>
      </a>
   </div>
</footer>