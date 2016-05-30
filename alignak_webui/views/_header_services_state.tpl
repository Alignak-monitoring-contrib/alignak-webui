%from alignak_webui.objects.item import UserService

%uss = datamgr.get_userservices_synthesis()
<div id="services-states-popover-content" class="hidden">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %for state in "active", "inactive", "unknown":
            <td>
              %label = "%s <i>(%s%%)</i>" % (uss["nb_" + state], uss["pct_" + state])
              {{! UserService({'status':state}).get_html_state(label=label, disabled=(not uss["nb_" + state]))}}
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%label = 'primary'
<a id="services-states-popover"
   class="services-all" data-count="{{ uss['nb_elts'] }}" data-problems="{{ uss['nb_problem'] }}"
   href="{{webui.get_url('User services')}}"
   data-original-title="{{_('Services states')}}" data-toggle="popover popover-services" title="{{_('Overall services states: %d services') % (uss['nb_elts'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-desktop"></i>
   <span class="label label-as-badge label-{{label}}">{{uss["nb_active"]}}</span>
</a>
