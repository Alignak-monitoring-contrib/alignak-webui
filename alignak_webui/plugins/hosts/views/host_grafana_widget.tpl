<!-- Hosts metrics widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui import get_app_config
%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

%if livestate:
%app_config = get_app_config()
%grafana_url = app_config.get('grafana', '')
%if not grafana_url:
   <center>
      <h3>{{_('Grafana panels is not configured.')}}</h3>
   </center>
%else:
   %if livestate.grafana and livestate.grafana_panelid:
   <iframe src="{{grafana_url}}/dashboard-solo/db/my-dashboard?panelId={{livestate.grafana_panelid}}&from=1467756000000&to=1467812182220&theme=light" width="450" height="200" frameborder="0"></iframe>
   %else:
   <div class="alert alert-info">
      <p class="font-blue">{{_('No Grafana panel available for this element.')}}</p>
   </div>
   %end
%end
%else:
   <div class="alert alert-info">
      <p class="font-blue">{{_('No livestate for this element.')}}</p>
   </div>
%end