%from alignak_webui.objects.item import Session

%hosts_states = datamgr.get_hosts_synthesis()
<div id="hosts-states-popover-content" class="hidden">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %for state in 'up', 'unreachable', 'down', 'unknown':
           <td>
              %label = "%s <i>(%s%%)</i>" % (hosts_states["nb_" + state], hosts_states["pct_" + state])
              {{! Session({'status':state}).get_html_state(label=label, disabled=(not hosts_states["nb_" + state]))}}
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%label = 'primary'
%if 'nb_open' in hosts_states:
<a id="hosts-states-popover"
   class="hosts-all" data-count="{{ hosts_states['nb_elts'] }}" data-problems="{{ hosts_states['nb_problem'] }}"
   href="{{webui.get_url('Hosts')}}"
   data-original-title="{{_('Hosts states')}}" data-toggle="popover popover-hosts" title="{{_('Overall hosts states: %d hosts (%d) opened') % (hosts_states['nb_elts'], hosts_states['nb_up'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-exchange"></i>
   <span class="label label-as-badge label-{{label}}">{{hosts_states["nb_up"]}}</span>
</a>
%else:
<a id="hosts-states-popover"
   class="hosts-all" data-count="{{ hosts_states['nb_elts'] }}" data-problems="{{ hosts_states['nb_problem'] }}"
   href="{{webui.get_url('Hosts')}}"
   data-original-title="{{_('Hosts states')}}" data-toggle="popover popover-hosts" title="{{_('Overall hosts states: %d hosts (%d) opened') % (hosts_states['nb_elts'], 128)}}" data-html="true" data-trigger="hover">
   <i class="fa fa-exchange"></i>
   <span class="label label-as-badge label-{{label}}">XxX</span>
</a>
%end