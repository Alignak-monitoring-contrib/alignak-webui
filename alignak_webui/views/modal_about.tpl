%from bottle import request
%from alignak_webui import manifest

<div class="modal-header">
  <button type="button" class="close" data-dismiss="modal" aria-hidden="true">&times;</button>
  <h4 class="modal-title">{{_('About ')}}{{request.app.config.get('about_name', manifest['name'])}}</h4>
</div>
<div class="modal-body">
  <!-- About Form -->
  <form class="form-horizontal">
  <fieldset>
     <div class="control-group">
        <label class="control-label" for="app_version">{{_('Application version')}}</label>
        <div class="controls">
           <input readonly="" name="app_version" type="text" class="form-control" placeholder="Not set" class="input-medium" value="{{request.app.config.get('about_name', manifest['name'])}}, version: {{request.app.config.get('about_version', manifest['version'])}}">
        </div>
     </div>

     <div class="control-group">
        <label class="control-label" for="app_copyright">{{_('Copyright')}}</label>
        <div class="controls">
           <input readonly="" name="app_copyright" type="text" class="form-control" placeholder="Not set" class="input-medium" value="{{request.app.config.get('about_copyright', manifest['copyright'])}}">
        </div>
     </div>

     <div class="control-group">
        <label class="control-label" for="app_release">{{_('Release notes')}}</label>
        <div class="controls">
           <textarea readonly="" name="app_release" rows="5" class="form-control" placeholder="Not set">{{request.app.config.get('about_release', manifest['release'])}}</textarea>
        </div>
     </div>
  </fieldset>
  </form>
</div>
<div class="modal-footer">
  <a href="#" class="btn btn-default" data-dismiss="modal">{{_('Close')}}</a>
</div>
