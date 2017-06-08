<!-- Services view widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%extra=''
%if service.acknowledged:
%extra += _(' and acknowledged')
%end
%if service.downtimed:
%extra += _(' and in scheduled downtime')
%end

<div id="service_view_left" class="col-lg-4 col-sm-4 text-center">
   <div class="overall_state">
      {{! service.get_html_state(text=None, title=_('Service is %s' % service.overall_status), size="fa-5x", use_status=service.overall_status)}}
      <legend><strong>{{service.alias}}</strong></legend>
      <center>
         <h4>{{_('Attached to ')}} {{! host.html_state_link}}</h4>
      </center>
   </div>
   <div class="actions">
   %if current_user.is_power():
      {{! Helper.get_html_commands_buttons(service, _('Actions'))}}
   %end
   </div>
</div>

<div id="service_view_right" class="col-lg-8 col-sm-8">
   <div class="panel panel-default">
      %collapsed = datamgr.get_user_preferences(current_user, "service-panel-check", {'opened': False})
      <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
           data-action="save-panel" data-target="#service-panel-check" data-toggle="collapse"
           aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
         <span class="caret"></span>&nbsp;{{ _('My last check') }}
      </div>

      <div id="service-panel-check" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
         <!-- Last check output -->
         <table class="table table-condensed table-nowrap">
            <colgroup>
               <col style="width: 100px;">
            </colgroup>
            <tbody>
               <tr>
                  <td><strong>{{_('State:')}}</strong></td>
                  <td>
                     {{! service.get_html_state(extra=extra, text=None, title=_('Service is %s' % service.state))}}
                  </td>
               </tr>
               %if service.last_check:
               <tr>
                  <td><strong>{{_('When:')}}</strong></td>
                  <td>
                     {{Helper.print_duration(service.last_check, duration_only=False, x_elts=0)}}
                  </td>
               </tr>
               %else:
               <tr>
                  <td></td>
                  <td class="text-danger"><strong>{{_('Not yet checked!')}}</strong></td>
               </tr>
               %end
               %if service.output:
               <tr>
                  <td><strong>{{_('Output:')}}</strong></td>
                  <td>
                     {{! service.html_output}}
                  </td>
               </tr>
               %end
               %if service.long_output:
               <tr>
                  <td><strong>{{_('Long output:')}}</strong></td>
                  <td>
                     {{! service.html_long_output}}
                  </td>
               </tr>
               %end
               %if service.perf_data:
               <tr>
                  <td><strong>{{_('Performance data:')}}</strong></td>
                  <td>
                     {{! service.html_perf_data if service.perf_data else '(none)'}}
                  </td>
               </tr>
               %end
            </tbody>
         </table>
      </div>
   </div>

   <div class="panel panel-default">
      %collapsed = datamgr.get_user_preferences(current_user, "service-panel-perfdata", {'opened': False})
      <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
           data-action="save-panel" data-target="#service-panel-perfdata" data-toggle="collapse"
           aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
         <span class="caret"></span>&nbsp;{{ _('My metrics') }}
      </div>

      <div id="service-panel-perfdata" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
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
   </div>
</div>
