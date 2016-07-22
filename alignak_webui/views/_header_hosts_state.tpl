%setdefault('datamgr', None)

%if datamgr:
%import time
%from alignak_webui.objects.item_host import Host

%hs = datamgr.get_livesynthesis()['hosts_synthesis']
%if hs:
%# Store N last livesynthesis in a user preference ... this to allow charting last minutes activity.
%hosts_states_queue = datamgr.get_user_preferences(current_user.name, 'hosts_states_queue', [])
%hosts_states_queue = hosts_states_queue['value']
%hosts_states_queue.append({'date': time.time(), 'hs': hs})
%if len(hosts_states_queue) > 120:
%hosts_states_queue.pop(0)
%end
%datamgr.set_user_preferences(current_user.name, 'hosts_states_queue', hosts_states_queue)
<div id="hosts-states-popover-content" class="hidden">
   <table class="table table-invisible">
      <tbody>
         <tr>
            %for state in ['up', 'unreachable', 'down']:
            <td>
              %label = "%s <i>(%s%%)</i>" % (hs["nb_" + state], hs["pct_" + state])
              %label = "%s%%" % (hs["pct_" + state])
              {{! Host({'status':state}).get_html_state(text=label, title=label, disabled=(not hs["nb_" + state]))}}
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%font='danger' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'success'
%from alignak_webui.objects.element_state import ElementState
%items_states = ElementState()
%cfg_state = items_states.get_icon_state('host', 'up')
%icon = cfg_state['icon']
<a id="hosts-states-popover"
   href="{{webui.get_url('Livestate table')}}?search=type:host"
   title="{{_('Overall hosts states: %d hosts (%d problems)') % (hs['nb_elts'], hs['nb_problems'])}}"
   data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}"
   data-original-title="{{_('Hosts states')}}"
   data-toggle="popover popover-hosts"
   data-html="true" data-trigger="hover">
   <span class="fa fa-{{icon}}"></span>
   <span class="label label-as-badge label-{{font}}">{{hs["nb_problems"] if hs["nb_problems"] > 0 else ''}}</span>
</a>

<script>
   // Activate the popover ...
   $('#hosts-states-popover').popover({
      placement: 'bottom',
      animation: true,
      template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>',
      content: function() {
         return $('#hosts-states-popover-content').html();
      }
   });
</script>
%end
%end