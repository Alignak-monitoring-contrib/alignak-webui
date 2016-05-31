%from alignak_webui.objects.item import Service

%services_states = datamgr.get_services_synthesis()
<div id="services-states-popover-content" class="hidden">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %for state in "ok", "warning", "critical", "unknown":
            <td>
              %label = "%s <i>(%s%%)</i>" % (services_states["nb_" + state], services_states["pct_" + state])
              {{! Service({'status':state}).get_html_state(label=label, disabled=(not services_states["nb_" + state]))}}
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%label = 'primary'
<a id="services-states-popover"
   class="services-all" data-count="{{ services_states['nb_elts'] }}" data-problems="{{ services_states['nb_problem'] }}"
   href="{{webui.get_url('Services')}}"
   data-original-title="{{_('Services states')}}" data-toggle="popover popover-services" title="{{_('Overall services states: %d services') % (services_states['nb_elts'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-desktop"></i>
   <span class="label label-as-badge label-{{label}}">{{services_states["nb_ok"]}}</span>
</a>
