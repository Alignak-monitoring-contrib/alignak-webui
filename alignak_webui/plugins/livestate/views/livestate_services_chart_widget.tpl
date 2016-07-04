<!-- livestates chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%if not livestates:
   <center>
      <h3>{{_('No livestate services matching the filter...')}}</h3>
   </center>
%else:
   %ss = datamgr.get_livesynthesis()['services_synthesis']
   %if ss:
   <div class="well">
      <!-- Chart -->
      <div id="pc_lv_services_{{widget_id}}">
         <canvas></canvas>
      </div>
   </div>
   %end
%end
<script>
   // Note: g_ prefixed variables are defined in the global alignak_layout.js file.
   $(document).ready(function() {
      var data=[], labels=[], colors=[], hover_colors=[];
      %for state in 'ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime':
         labels.push(g_services_states["{{state.lower()}}"]['label']);
         data.push({{ss["nb_" + state]}});
         colors.push(g_services_states["{{state.lower()}}"]['color'])
         hover_colors.push(g_hoverBackgroundColor)
      %end
      var data = {
         labels: labels,
         datasets: [
            {
               data: data,
               backgroundColor: colors,
               hoverBackgroundColor: hover_colors
            }
         ]
      };
      var ctx = $("#pc_lv_services_{{widget_id}} canvas");

      // Create chart
      var myBarChart = new Chart(ctx, {
         type: 'doughnut',
         data: data,
         options: {
            title: {
               display: true,
               text: '{{title}}'
            },
            legend: {
               display: true,
               position: 'bottom'
            }
         }
      });
   });
</script>