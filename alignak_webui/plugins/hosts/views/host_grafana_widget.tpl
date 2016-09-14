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
      <!--
      <div class="alert alert-info">
         <p class="font-blue">{{_('No Grafana panel available for %s.' % service.name)}}</p>
      </div>
      -->
      %end
   %end
%end
