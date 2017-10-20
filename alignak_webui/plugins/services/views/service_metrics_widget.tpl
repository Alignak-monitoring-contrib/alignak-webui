<!-- Service metrics widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

%if service:
<table class="table table-condensed">
   <thead>
      <tr>
         <th>{{_('Service')}}</th>
         <th>{{_('Metric')}}</th>
         <th>{{_('Value')}}</th>
         <th>{{_('Warning')}}</th>
         <th>{{_('Critical')}}</th>
         <th>{{_('Min')}}</th>
         <th>{{_('Max')}}</th>
         <th>{{_('UOM')}}</th>
         <th></th>
      </tr>
   </thead>
   <tbody style="font-size:x-small;">
   %if service.perf_data:
      %name_line = True
      %perfdatas = PerfDatas(service.perf_data)
      %if perfdatas:
      %for metric in sorted(perfdatas, key=lambda metric: metric.name):
      %if metric.name:
      <tr>
         %if name_line:
         <td><strong>{{_('service check')}}</strong></td>
         %else:
         <td></td>
         %end
         %name_line = False
         <td><strong>{{metric.name}}</strong></td>
         <td>{{metric.value}}</td>
         <td>{{metric.warning if metric.warning!=None else ''}}</td>
         <td>{{metric.critical if metric.critical!=None else ''}}</td>
         <td>{{metric.min if metric.min!=None else ''}}</td>
         <td>{{metric.max if metric.max!=None else ''}}</td>
         <td>{{metric.uom if metric.uom else ''}}</td>
      </tr>
      %end
      %end
      %end
   %else:
      <tr>
         <td colspan="8"><strong>{{_('No metrics are available for this service.')}}</strong></td>
      </tr>
   %end
   </tbody>
</table>
%else:
   <div class="alert alert-info">
      <p>{{_('No metrics available.')}}</p>
   </div>
%end
