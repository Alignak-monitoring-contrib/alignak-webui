<!-- Hosts chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%if not elements:
   <center>
      <h4>{{_('No services matching the filter...')}}</h4>
   </center>
%else:
   %lv = datamgr.get_livesynthesis()
   %ss = lv['services_synthesis']
   %if ss:
   <div class="well">
      <!-- Chart -->
      <div id="pc_services_{{widget_id}}">
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
         data.push({{ss["nb_" + state] if ss["nb_" + state] >= 0 else 0}});
         colors.push(g_services_states["{{state.lower()}}"]['color'])
         hover_colors.push(g_services_states["{{state.lower()}}"]['background'])
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
      var ctx = $("#pc_services_{{widget_id}} canvas");

      // Create chart
      var myBarChart = new Chart(ctx, {
         type: 'doughnut',
         data: data,
         options: {
            responsive: true,
            maintainAspectRatio: false,
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