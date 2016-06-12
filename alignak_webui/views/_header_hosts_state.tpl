%setdefault('datamgr', None)

%if datamgr:
%from alignak_webui.objects.item import Host

%hosts_states = datamgr.get_livesynthesis()['hosts_synthesis']
%if hosts_states:
<div id="hosts-states-popover-content" class="hidden">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %for state in 'up', 'unreachable', 'down':
           <td>
              %label = "%s <i>(%s%%)</i>" % (hosts_states["nb_" + state], hosts_states["pct_" + state])
              {{! Host({'status':state}).get_html_state(title=label, disabled=(not hosts_states["nb_" + state]))}}
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%label = 'success'
<a id="hosts-states-popover"
   class="hosts-all" data-count="{{ hosts_states['nb_elts'] }}" data-problems="{{ hosts_states['nb_problems'] }}"
   href="{{webui.get_url('Hosts')}}"
   data-original-title="{{_('Hosts states')}}" data-toggle="popover popover-hosts" title="{{_('Overall hosts states: %d hosts (%d) up') % (hosts_states['nb_elts'], hosts_states['nb_up'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-server"></i>
   <span class="label label-as-badge label-{{label}}">{{hosts_states["nb_up"]}}</span>
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