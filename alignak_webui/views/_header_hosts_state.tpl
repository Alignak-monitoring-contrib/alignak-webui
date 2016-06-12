%setdefault('datamgr', None)

%if datamgr:
%from alignak_webui.objects.item import Host

%hs = datamgr.get_livesynthesis()['hosts_synthesis']
%if hs:
<div id="hosts-states-popover-content" class="hidden">
   <table class="table table-invisible table-condensed">
      <tbody>
         <tr>
            %for state in 'up', 'unreachable', 'down':
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
<a id="hosts-states-popover"
   class="hosts-all" data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}"
   href="{{webui.get_url('Hosts')}}"
   data-original-title="{{_('Hosts states')}}" data-toggle="popover popover-hosts" title="{{_('Overall hosts states: %d hosts (%d) up') % (hs['nb_elts'], hs['nb_up'])}}" data-html="true" data-trigger="hover">
   <i class="fa fa-server"></i>
   <span class="label label-as-badge label-{{font}}">{{hs["nb_up"]}}</span>
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