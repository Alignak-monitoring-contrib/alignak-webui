%from bottle import request
%from alignak_webui import manifest

<div class="modal-header">
   <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
   <h4 class="modal-title">{{_('About ')}}{{request.app.config.get('about_name', manifest['name'])}}</h4>
</div>
<div class="modal-body">
   <!-- About Form -->
   <form class="form">
   <fieldset>
      <div class="form-group">
        <label class="control-label" for="app_version">{{_('Application version')}}</label>
        <input readonly="" id="app_version" type="text" class="form-control" placeholder="Not set" class="input-medium" value="{{request.app.config.get('about_name', manifest['name'])}}, version: {{request.app.config.get('about_version', manifest['version'])}}">
      </div>

      <div class="form-group">
        <label class="control-label" for="app_copyright">{{_('Copyright')}}</label>
        <input readonly="" id="app_copyright" type="text" class="form-control" placeholder="Not set" class="input-medium" value="{{request.app.config.get('about_copyright', manifest['copyright'])}}">
      </div>

      <div class="form-group">
        <label class="control-label" for="app_url">{{_('Home page')}}</label>
        <p>
        <a id="app_url" href="{{request.app.config.get('about_url', manifest['doc'])}}">{{request.app.config.get('about_url', manifest['url'])}}</a>
        </p>
      </div>

      <div class="form-group">
        <label class="control-label" for="app_doc">{{_('User documentation')}}</label>
        <p>
        <a id="app_doc" href="">{{request.app.config.get('about_doc', manifest['doc'])}}</a>
        </p>
      </div>

      <div class="form-group">
        <label class="control-label" for="app_release">{{_('Release notes')}}</label>
        <textarea id="app_release" readonly="" rows="5" class="form-control">{{request.app.config.get('about_release', manifest['release'])}}</textarea>
      </div>
   </fieldset>
   </form>
</div>
<div class="modal-footer">
   <a href="#" class="btn btn-default" data-dismiss="modal">{{_('Close')}}</a>
</div>
