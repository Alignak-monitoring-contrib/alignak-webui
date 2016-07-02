<!-- Hosts metrics widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.metrics import HostMetrics
%metrics = HostMetrics(livestate, livestate_services)

<div class="col-lg-4 col-sm-3 text-center">
   {{! livestate.get_html_state(text=None, size="fa-5x")}}
   <div>
      <strong>{{host.alias}}</strong>
   </div>
   <div>
      <table class="table table-condensed">
         <thead><tr>
            <th style="width: 40px"></th>
            <th></th>
         </tr></thead>

         <tbody>
            %for lv_service in livestate_services:
            <tr id="#{{lv_service.id}}">
               <td title="{{lv_service.alias}}">
                  %title = "%s - %s (%s)" % (lv_service.status, Helper.print_duration(lv_service.last_check, duration_only=True, x_elts=0), lv_service.output)
                  {{! lv_service.get_html_state(text=None, title=title)}}
               </td>

               <td>
                  <small>{{! lv_service.get_html_link()}}</small>
               </td>
            </tr>
            %end
         </tbody>
      </table>
   </div>
</div>
<div class="col-lg-8 col-sm-9">
%for svc in ['load', 'cpu', 'mem', 'disk', 'net']:
<div id="bc_{{svc}}" class="well well-sm">
   <div>
      <div class="graph">
         <canvas></canvas>
      </div>
      <div class="title">
         <div class="text-center">
            <h4>{{svc}}</h4>
         </div>
      </div>
   </div>
</div>
%end
</div>

<script>
   var state_colors = [
      '#ddffcc', '#ffd9b3', '#ffb3b3', '#b3d9ff', '#dddddd', '#666666'
   ];
   var bar_backgroundColor = "#9999ff";
   var bar_borderColor = "#0000b3";
   var bar_hoverBackgroundColor = "rgba(255,99,132,0.4)";
   var bar_hoverBorderColor = "rgba(255,99,132,1)";

   $(document).ready(function() {
      %for svc in ['cpu']:
         %svc_state, svc_name, svc_metrics = metrics.get_service_metric(svc)
         %if svc_state == 3:
         $("#bc_{{svc}}").hide();
         %else:
         // Update Load
         var data = [], labels= [];
         %for perf in svc_metrics:
            labels.push("{{perf}}");
            data.push({{svc_metrics[perf]}});
         %end
         var data = {
            labels: labels,
            datasets: [{
               label: '{{svc_name}}',
               backgroundColor: bar_backgroundColor, borderColor: bar_borderColor,
               borderWidth: 1,
               hoverBackgroundColor: bar_hoverBackgroundColor, hoverBorderColor: bar_hoverBorderColor,
               data: data,
            }]
         };
         var ctx = $("#bc_{{svc}} canvas");
         // Set color depending upon state
         ctx.css({'backgroundColor': state_colors[{{svc_state}}]});
         var myBarChart = new Chart(ctx, {
            type: 'horizontalBar',
            data: data,
            options: {}
         });
         %end
      %end

      %for svc in ['load', 'mem', 'disk', 'net']:
         %svc_state, svc_name, svc_metrics = metrics.get_service_metric(svc)
         %if svc_state == 3:
         $("#bc_{{svc}}").hide();
         %else:
         // Update Load
         var data = [], labels= [];
         %for perf in svc_metrics:
            labels.push("{{perf}}");
            data.push({{svc_metrics[perf]}});
         %end
         var data = {
            labels: labels,
            datasets: [{
               label: '{{svc_name}}',
               backgroundColor: bar_backgroundColor, borderColor: bar_borderColor,
               borderWidth: 1,
               hoverBackgroundColor: bar_hoverBackgroundColor, hoverBorderColor: bar_hoverBorderColor,
               data: data,
            }]
         };
         var ctx = $("#bc_{{svc}} canvas");
         // Set color depending upon state
         ctx.css({'backgroundColor': state_colors[{{svc_state}}]});
         var myBarChart = new Chart(ctx, {
            type: 'horizontalBar',
            data: data,
            options: {}
         });
         %end
      %end
   });
</script>