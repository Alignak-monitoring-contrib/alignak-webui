<!-- Livestate services states history chart widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%services_states_queue = datamgr.get_user_preferences(current_user.name, 'services_states_queue', [])
%services_states_queue = services_states_queue['value']
%if not services_states_queue:
   <center>
      <h3>{{_('Not enough services states stored to build a graph...')}}</h3>
   </center>
%else:
   <div class="well">
      <!-- Chart -->
      <div id="pc_services_history_{{widget_id}}">
         <canvas></canvas>
      </div>
   </div>
%end
<script>
   // Note: g_ prefixed variables are defined in the global alignak_layout.js file.
   $(document).ready(function() {
      var labels=[];
      %idx=len(services_states_queue)
      %for ls in services_states_queue:
         labels.push('{{ls['date']}}');
         %idx=idx-1
      %end
      %for state in ['ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime']:
         var data_{{state}}=[];
         %for ls in services_states_queue:
         data_{{state}}.push({{ls["ss"]["nb_" + state]}});
         %end
      %end
      var data = {
         labels: labels,
         datasets: [
            %for state in ['ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime']:
            {
               label: g_services_states["{{state.lower()}}"]['label'],
               fill: false,
               lineTension: 0.1,
               borderWidth: 1,
               borderColor: g_services_states["{{state.lower()}}"]['color'],
               backgroundColor: g_services_states["{{state.lower()}}"]['background'],
               pointBorderWidth: 1,
               pointRadius: 2,
               pointBorderColor: g_services_states["{{state.lower()}}"]['color'],
               pointBackgroundColor: g_services_states["{{state.lower()}}"]['background'],
               data: data_{{state}}
            },
            %end
         ]
      };
      var ctx = $("#pc_services_history_{{widget_id}} canvas");

      // Set moment libray locale
      moment.locale('fr');

      // Create chart
      var myBarChart = new Chart(ctx, {
         type: 'line',
         data: data,
         options: {
            title: {
               display: true,
               text: '{{title}}'
            },
            legend: {
               display: true,
               position: 'bottom'
            },
            scales: {
               xAxes: [{
                  type: 'time',
                  ticks: {
                     fontSize: 10,
                     fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                     autoSkip: true
                  },
                  time: {
                     parser: 'X',
                     tooltipFormat: 'LTS',
                     unit: 'minute',
                     displayFormats: {
                        second: 'LTS',
                        minute: 'LTS',
                        hour: 'LTS',
                        day: 'LTS'
                     }
                  }
               }],
               yAxes: [{
                  ticks: {
                     fontSize: 10,
                     fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                     autoSkip: false
                  },
                  stacked: true
               }]
            }
         }
      });
   });
</script>