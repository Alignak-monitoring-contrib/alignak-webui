<!-- Hosts metrics widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%setdefault('links', False)
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%rebase("_widget", js=[], css=[], options=options)

%from alignak_webui.utils.helper import Helper

%if perf_data:
%from alignak_webui.utils.perfdata import PerfDatas
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
      %host_line = True
      %perfdatas = PerfDatas(perf_data)
      %if perfdatas:
      %for metric in sorted(perfdatas, key=lambda metric: metric.name):
      %if metric.name:
      <tr>
         <td><strong>{{'Host check' if host_line else ''}}</strong></td>
         %host_line = False
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
   </tbody>
</table>
%else:
<div class="alert alert-info">
   <p class="font-blue">{{_('No metrics are available.')}}</p>
</div>
%end
