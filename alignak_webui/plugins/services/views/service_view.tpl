<!-- Services view widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

<div id="service_view_information" class="col-lg-4 col-sm-4 text-center">
   {{! service.get_html_state(text=None, size="fa-5x")}}
   <div>
      <strong>{{service.alias}}</strong>
   </div>
   <hr/>
   <center>
      <h4>{{_('Attached to %s') % service.host.alias}}</h4>
   </center>
   {{! host.html_state_link}}
</div>
<div id="service_view_graphes" class="col-lg-8 col-sm-8">



   %from alignak_webui.utils.helper import Helper
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
      %if service.perf_data:
         %name_line = True
         %perfdatas = PerfDatas(service.perf_data)
         %if perfdatas:
         %for metric in sorted(perfdatas, key=lambda metric: metric.name):
         %if metric.name:
         <tr>
            %if name_line:
            <td><strong>{{service.name}}</strong></td>
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

</div>
