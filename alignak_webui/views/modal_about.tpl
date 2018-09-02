%from bottle import request
%from alignak_webui import __manifest__

<div class="modal-header">
   <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
   <h4 class="modal-title">{{_('About ')}}{{request.app.config.get('about_name', __manifest__['name'])}}</h4>
</div>
<div class="modal-body">
   <!-- About Form -->
   <form class="form">
      <div class="form-group">
        <label class="control-label" for="app_version">{{_('Application version')}}</label>
        <input readonly="" id="app_version" type="text" class="form-control" placeholder="Not set" class="input-medium" value="{{request.app.config.get('about_name', __manifest__['name'])}}, version: {{request.app.config.get('about_version', __manifest__['version'])}}">

        <label class="control-label" for="app_copyright">{{_('Copyright')}}</label>
        <input readonly="" id="app_copyright" type="text" class="form-control" placeholder="Not set" class="input-medium" value="{{request.app.config.get('about_copyright', __manifest__['copyright'])}}">

        <label class="control-label" for="alignak_url">{{_('Alignak')}}</label>
        <p>
        <a id="alignak_url" href="http://www.alignak.net" target="_blank">http://www.alignak.net/</a>
        </p>

        <label class="control-label" for="app_url">{{_('Home page')}}</label>
        <p>
        <a id="app_url" href="{{request.app.config.get('about_url', __manifest__['url'])}}" target="_blank">{{request.app.config.get('about_url', __manifest__['url'])}}</a>
        </p>

        <label class="control-label" for="app_doc">{{_('User documentation')}}</label>
        <p>
        <a id="app_doc" href="{{request.app.config.get('about_doc', __manifest__['doc'])}}" target="_blank">{{request.app.config.get('about_doc', __manifest__['doc'])}}</a>
        </p>

        <label class="control-label" for="app_release">{{_('Release notes')}}</label>
        <textarea id="app_release" readonly="" rows="5" class="form-control">{{request.app.config.get('about_release', __manifest__['release'])}}</textarea>
      </div>
   </form>
</div>
