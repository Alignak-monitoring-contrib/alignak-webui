<!-- Hosts view widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.objects.item_host import Host
%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

%services_plugin = webui.find_plugin('Services')
%if services_plugin:
   %# Get host services
   %services = datamgr.get_services(search={'where': {'host': host.id}})
   %# Aggregate host services in a tree
   %tree_items = datamgr.get_services_aggregated(services)

   %# Get host services metrics
   %from alignak_webui.utils.metrics import HostMetrics
   %metrics = HostMetrics(host, services, plugin_parameters, host.tags)
%end

<div id="host_view_left" class="col-lg-4 col-sm-4 text-center">
   <div class="overall_state">
      {{! host.get_html_state(text=None, title=_('Host is %s' % host.overall_status), size="fa-4x", use_status=host.overall_status)}}
      <legend><strong>{{host.alias}}</strong></legend>
   </div>
   <div class="actions">
      %if current_user.is_power():
         {{! Helper.get_html_commands_buttons(host, _('Actions'))}}
      %end
   </div>
   %if services:
   <div class="host_services text-left">
      <table class="table table-condensed table-invisible">
         <tbody>
            %for service in sorted(services, key=lambda x: x['alias'], reverse=False):
            <tr id="#host-service-{{service.name}}">
               <td title="{{service.alias}}">
                  %extra=''
                  %if service.acknowledged:
                  %extra += _(' and acknowledged')
                  %end
                  %if service.downtimed:
                  %extra += _(' and in scheduled downtime')
                  %end
                  %title = "%s - %s (%s)" % (service.status, Helper.print_duration(service.last_check, duration_only=True, x_elts=0), service.output)
                  {{! service.get_html_state(text=None, title=title, extra=extra, use_status=service.overall_status)}}
               </td>

               <td>
                  <small>{{! service.get_html_link()}}</small>
               </td>

               %if current_user.is_power():
               <td>
                  {{! Helper.get_html_commands_buttons(service, _('Actions'))}}
               </td>
               %end
            </tr>
            %end
         </tbody>
      </table>
   </div>
   %end
</div>

<div id="host_view_right" class="col-lg-8 col-sm-8">
   <div class="panel panel-default">
      %collapsed = datamgr.get_user_preferences(current_user, "host-panel-check", {'opened': False})
      <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
           data-action="save-panel" data-target="#host-panel-check" data-toggle="collapse"
           aria-controls="host-panel-check" aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
         <span class="caret"></span>&nbsp;{{ _('My last check') }}
      </div>

      <div id="host-panel-check" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
         <!-- Last check output -->
         <table class="table table-condensed table-nowrap">
            <colgroup>
               <col style="width: 100px;">
            </colgroup>
            <tbody>
               <tr>
                  <td><strong>{{_('State:')}}</strong></td>
                  <td>
                     %extra=''
                     %if host.acknowledged:
                     %extra += _(' and acknowledged')
                     %end
                     %if host.downtimed:
                     %extra += _(' and in scheduled downtime')
                     %end
                     {{! host.get_html_state(extra=extra, text=None, title=_('Host is %s' % host.state))}}
                  </td>
               </tr>
               %if host.last_check:
               <tr>
                  <td><strong>{{_('When:')}}</strong></td>
                  <td>
                     {{Helper.print_duration(host.last_check, duration_only=False, x_elts=0)}}
                  </td>
               </tr>
               %else:
               <tr>
                  <td></td>
                  <td class="text-danger"><strong>{{_('Not yet checked!')}}</strong></td>
               </tr>
               %end
               %if host.output:
               <tr>
                  <td><strong>{{_('Output:')}}</strong></td>
                  <td>
                     {{! host.html_output}}
                  </td>
               </tr>
               %end
               %if host.long_output:
               <tr>
                  <td><strong>{{_('Long output:')}}</strong></td>
                  <td>
                     {{! host.html_long_output}}
                  </td>
               </tr>
               %end
               %if host.perf_data:
               <tr>
                  <td><strong>{{_('Performance data:')}}</strong></td>
                  <td>
                     {{! host.html_perf_data if host.perf_data else '(none)'}}
                  </td>
               </tr>
               %end
            </tbody>
         </table>
      </div>
   </div>

   %#if plugin.variables:
   <div class="panel panel-default">
      %collapsed = datamgr.get_user_preferences(current_user, "host-panel-variables", {'opened': False})
      <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
           data-action="save-panel" data-target="#host-panel-variables" data-toggle="collapse"
           aria-controls="host-panel-variables" aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
         <span class="caret"></span>&nbsp;{{ _('My variables') }}
      </div>

      <div id="host-panel-variables" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
         <table class="table table-condensed table-bordered">
            <colgroup>
               <col style="width: 40%" />
               <col style="width: 60%" />
            </colgroup>
            <thead>
               <tr>
                  <th colspan="3">{{_('Variables:')}}</th>
               </tr>
            </thead>
            <tbody style="font-size:x-small;">
            %for var in sorted(plugin.variables):
               <tr>
                  %if plugin.variables[var] is True:
                  % field=plugin.table[var]
                  % hint = _('Field name: %s\nComment: %s') % (var, field.get('comment', ''))
                  % name=field.get('title', '')
                  % value=getattr(host, var, 'XxX')
                  % if hasattr(value, 'name'):
                  %  value = getattr(value, 'name')
                  % end
                  %else:
                  % name=var
                  % value=plugin.variables[var]
                  % hint = ''
                  %end
                  <td>{{name}}</td>
                  <td title="{{ hint }}">{{ value }}</td>
               </tr>
            %end
            </tbody>
         </table>
      </div>
   </div>
   %#end

   %if host.perf_data:
   <div class="panel panel-default">
      %collapsed = datamgr.get_user_preferences(current_user, "host-panel-perfdata", {'opened': False})
      <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
           data-action="save-panel" data-target="#host-panel-perfdata" data-toggle="collapse"
           aria-controls="host-panel-perfdata" aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
         <span class="caret"></span>&nbsp;{{ _('My metrics') }}
      </div>

      <div id="host-panel-perfdata" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
         <table class="table table-condensed">
            <thead>
               <tr>
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
            %if host.perf_data:
               %name_line = True
               %perfdatas = PerfDatas(host.perf_data)
               %if perfdatas:
               %for metric in sorted(perfdatas, key=lambda metric: metric.name):
               %if metric.name:
               <tr>
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
                  <td colspan="8"><strong>{{_('No metrics are available for this host.')}}</strong></td>
               </tr>
            %end
            </tbody>
         </table>
      </div>
   </div>
   %end

%if not services_plugin:
   <center>
      <h3>{{_('The services plugin is not installed or enabled.')}}</h3>
   </center>
%else:
   <!-- Service tree view -->
   %include("services_tree.tpl", tree_items=tree_items, elts=services, tree_type='service', in_host_view=True, title=_('My services'), layout=False, pagination=webui.helper.get_pagination_control('service', len(services), 0, len(services)))

   %if not services:
   <center>
      <h3>{{_('No services defined for this host.')}}</h3>
   </center>
   %else:
      %if metrics.params:
      <div class="panel panel-default">
         %collapsed = datamgr.get_user_preferences(current_user, "host-panel-metrics", {'opened': False})
         <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
              data-action="save-panel" data-target="#host-panel-metrics" data-toggle="collapse"
              aria-controls="host-panel-metrics" aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
            <span class="caret"></span>&nbsp;{{ _('My metrics graphs') }}
         </div>

         <div id="host-panel-metrics" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
         %for svc in metrics.params:
            %svc_state, svc_name, svc_min, svc_max, svc_warning, svc_critical, svc_metrics = metrics.get_service_metric(svc)
            %if svc_state == -1:
            %continue
            %end
            <div id="bc_{{svc}}" class="well well-sm test">
               <div class="graph">
                  <canvas></canvas>
               </div>
            </div>
         %end
         </div>
      </div>
      %end
   %end

   %if services:
   <script>
      var state_colors = [
         '#ddffcc', '#ffd9b3', '#ffb3b3', '#b3d9ff', '#dddddd', '#666666'
      ];
      var bar_backgroundColor = "rgba(0, 0, 0, 0.3)";
      var bar_borderColor = "#0000b3";
      var bar_hoverBackgroundColor = "rgba(255,99,132,0.4)";
      var bar_hoverBorderColor = "rgba(255,99,132,1)";

      // Fix for pie/doughnut with a percentage ...
      Chart.controllers.doughnut.prototype.calculateTotal = function() { return 100; }

      $(document).ready(function() {
         %for svc in sorted(metrics.params):
            %svc_state, svc_name, svc_min, svc_max, svc_warning, svc_critical, svc_metrics = metrics.get_service_metric(svc)
            %if svc_state == -1:
            %continue
            %end

            var data=[], labels=[], warning=[], critical=[];
            %chart_type = metrics.params[svc].get('type', 'bar')
            %sum_values = 0
            %for perf in sorted(svc_metrics):
               labels.push("{{perf.name}}");
               data.push({{perf.value}});
               warning.push({{perf.warning}});
               critical.push({{perf.critical}});
               %sum_values += perf.value
            %end
            %if chart_type == 'gauge':
               //data.push({{100 - sum_values}});
            %end
            var data = {
               labels: labels,
               datasets: [
                  {
                     label: '{{svc_name}}',
                     backgroundColor: bar_backgroundColor,
                     borderColor: bar_borderColor,
                     borderWidth: 1,
                     hoverBackgroundColor: bar_hoverBackgroundColor,
                     hoverBorderColor: bar_hoverBorderColor,
                     data: data,
                  }
                  %if chart_type == 'bar' or chart_type == 'horizontalBar':
                  %if svc_warning >= 0:
                  ,{
                     label: 'Warning',
                     type: 'line',
                     fill: false,
                     //backgroundColor: "rgba(151,187,205,0.5)",
                     borderColor: state_colors[1],
                     borderWidth: 2,
                     pointBorderColor: state_colors[2],
                     pointBorderWidth: 2,
                     showLine: false,
                     data: warning,
                  }
                  %end
                  %if svc_critical >= 0:
                  ,{
                     label: 'Critical',
                     type: 'line',
                     fill: false,
                     //backgroundColor: "rgba(151,187,205,0.5)",
                     borderColor: state_colors[2],
                     borderWidth: 2,
                     pointBorderColor: state_colors[2],
                     pointBorderWidth: 2,
                     showLine: false,
                     data: critical
                  }
                  %end
                  %end
               ]
            };
            var ctx = $("#bc_{{svc}} canvas");
            // Set color depending upon state
            ctx.css({'backgroundColor': state_colors[{{svc_state}}]});
            var myChart = new Chart(ctx, {
               %if chart_type == 'gauge':
               type: 'doughnut',
               %else:
               type: '{{metrics.params[svc].get('type', 'bar')}}',
               %end
               data: data,
               options: {
                  %if chart_type == 'gauge':
                     rotation: Math.PI,
                     circumference: Math.PI,
                  %end
                  title: {
                     display: true,
                     text: '{{svc_name}}'
                  },
                  %if chart_type != 'pie' and chart_type != 'gauge':
                  scales: {
                     %if chart_type == 'horizontalBar':
                     xAxes: [{
                     %else:
                     yAxes: [{
                     %end
                        stacked: false,
                        ticks: {
                           %if svc_min >= 0:
                           min: {{svc_min}},
                           %end
                           %if svc_max >= 0:
                           max: {{svc_max}},
                           %end
                        }
                     }]
                  }
                  ,animation: {
                     onComplete: function () {
                        var chartInstance = this.chart;
                        var ctx = chartInstance.ctx;
                        ctx.textAlign = "center";
                        Chart.helpers.each(this.data.datasets.forEach(function (dataset, i) {
                           var meta = chartInstance.controller.getDatasetMeta(i);
                           Chart.helpers.each(meta.data.forEach(function (bar, index) {
                              ctx.fillText(dataset.data[index], bar._model.x - 10, bar._model.y - 10);
                           }),this)
                        }),this);
                     }
                  }
                  %end
               }
            });
         %end

         $(window).resize();
      });
   </script>
   %end
%end
</div>
