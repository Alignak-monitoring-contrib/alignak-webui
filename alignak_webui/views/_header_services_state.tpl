%setdefault('datamgr', None)

%if datamgr:
%import time
%from alignak_webui.objects.item import Service

%ss = datamgr.get_livesynthesis()['services_synthesis']
%if ss:
%# Store N last livesynthesis in a user preference ... this to allow charting last minutes activity.
%services_states_queue = datamgr.get_user_preferences(current_user.name, 'services_states_queue', [])
%services_states_queue = services_states_queue['value']
%services_states_queue.append({'date': time.time(), 'ss': ss})
%if len(services_states_queue) > 120:
%services_states_queue.pop(0)
%end
%datamgr.set_user_preferences(current_user.name, 'services_states_queue', services_states_queue)
<div id="services-states-popover-content" class="hidden">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %for state in ['ok', 'warning', 'critical', 'unknown']:
            <td>
              %label = "%s <i>(%s%%)</i>" % (ss["nb_" + state], ss["pct_" + state])
              %label = "%s" % (ss["nb_" + state])
              {{! Service({'status':state}).get_html_state(text=label, title=label, disabled=(not ss["nb_" + state]))}}
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%font='danger' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'success'
<a id="services-states-popover"
   class="services-all" data-count="{{ ss['nb_elts'] }}" data-problems="{{ ss['nb_problems'] }}"
   href="{{webui.get_url('Services')}}"
   data-original-title="{{_('Services states')}}" data-toggle="popover popover-services" title="{{_('Overall services states: %d services (%d problems)') % (ss['nb_elts'], ss['nb_problems'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-cubes"></i>
   <span class="label label-as-badge label-{{font}}">{{ss["nb_problems"] if ss["nb_problems"] else ''}}</span>
</a>

<script>
   // Activate the popover ...
   $('#services-states-popover').popover({
      placement: 'bottom',
      animation: true,
      template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>',
      content: function() {
         return $('#services-states-popover-content').html();
      }
   });
</script>
%end
%end
