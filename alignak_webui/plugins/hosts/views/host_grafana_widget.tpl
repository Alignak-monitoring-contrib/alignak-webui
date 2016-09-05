<!-- Hosts Grafana widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui import get_app_config
%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

%app_config = get_app_config()
%grafana_url = app_config.get('grafana', '')
%if not grafana_url:
   <center>
      <h3>{{_('Grafana panels is not configured.')}}</h3>
   </center>
%else:
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}"><i class="fa fa-bug"></i> Host as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(host.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}_services"><i class="fa fa-bug"></i> Host services as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}_services" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
            %for service in services:
            <div class="panel panel-default">
               <div class="panel-heading">
                  <h4 class="panel-title">
                     <a data-toggle="collapse" href="#collapse{{service.id}}_services"><i class="fa fa-bug"></i> Service: {{service.name}}</a>
                  </h4>
               </div>
               <div id="collapse{{service.id}}_services" class="panel-collapse collapse" style="height: 200px;">
                  <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                     %for k,v in sorted(service.__dict__.items()):
                        <dt>{{k}}</dt>
                        <dd>{{v}}</dd>
                     %end
                  </dl>
               </div>
            </div>
            %end
         </div>
      </div>
   </div>
   %end

   %if host.ls_grafana and host.ls_grafana_panelid:
   %dashboard_name = host.name.replace('.', '-')
   %panel_id = host.ls_grafana_panelid
   <iframe src="{{grafana_url}}/dashboard-solo/db/host_{{dashboard_name}}?panelId={{panel_id}}" width="100%" height="320" frameborder="0"></iframe>
   %else:
   <div class="alert alert-info">
      <p class="font-blue">{{_('No Grafana panel available for %s.' % host.name)}}</p>
   </div>
   %end

   %for service in services or []:
      %if service.ls_grafana and service.ls_grafana_panelid:
      %dashboard_name = host.name.replace('.', '-')
      %panel_id = service.ls_grafana_panelid
      <iframe class="embed-responsive-item" src="{{grafana_url}}/dashboard-solo/db/host_{{dashboard_name}}?panelId={{panel_id}}" width="100%" height="240" frameborder="0"></iframe>
      %else:
      <div class="alert alert-info">
         <p class="font-blue">{{_('No Grafana panel available for %s.' % service.name)}}</p>
      </div>
      %end
   %end
%end
