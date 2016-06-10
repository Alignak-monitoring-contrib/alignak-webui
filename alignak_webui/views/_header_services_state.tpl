%setdefault('datamgr', None)

%if datamgr:
%from alignak_webui.objects.item import Service

%services_states = datamgr.get_livesynthesis()['services_synthesis']
%if services_states:
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

%label = 'success'
<a id="services-states-popover"
   class="services-all" data-count="{{ services_states['nb_elts'] }}" data-problems="{{ services_states['nb_problems'] }}"
   href="{{webui.get_url('Services')}}"
   data-original-title="{{_('Services states')}}" data-toggle="popover popover-services" title="{{_('Overall services states: %d services (%d) up') % (services_states['nb_elts'], services_states['nb_ok'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-cubes"></i>
   <span class="label label-as-badge label-{{label}}">{{services_states["nb_ok"]}}</span>
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
