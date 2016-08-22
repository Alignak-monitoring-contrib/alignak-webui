%setdefault('datamgr', None)

%if datamgr:
%import time
%from alignak_webui.objects.item_service import Service

%ss = datamgr.get_livesynthesis()['services_synthesis']
%if ss:

%from bottle import request
%if request.app.config.get('header_refresh_period', '30') != '0':
%# Store N last livesynthesis in a user preference ... this to allow charting last minutes activity.
%services_states_queue = datamgr.get_user_preferences(current_user.name, 'services_states_queue', [])
%services_states_queue.append({'date': time.time(), 'ss': ss})
%if len(services_states_queue) > 120:
%services_states_queue.pop(0)
%end
%datamgr.set_user_preferences(current_user.name, 'services_states_queue', services_states_queue)
%end

<!-- Declared here to make sure they are applied -->
<style>
.popover-services {
   background: #eee;
   color: #fff;
   border-radius: 3px;
}
.popover-title {
   background: #009688;
   color: #FFF;
}
</style>
<div id="services-states-popover-content" class="hidden">
   <table class="table table-invisible">
      <tbody>
         <tr>
            %for state in ['ok', 'warning', 'critical', 'unknown']:
            <td>
              %title = _('%s services %s (%s%%)') % (ss["nb_" + state], state, ss["pct_" + state])
              %label = "%s <i>(%s%%)</i>" % (ss["nb_" + state], ss["pct_" + state])
               <a href="{{ webui.get_url('Livestate table') }}?search=type:service state:{{state.upper()}}">
              {{! Service({'status':state}).get_html_state(text=label, title=title, disabled=(not ss["nb_" + state]))}}
               </a>
            </td>
            %end
         </tr>
      </tbody>
   </table>
</div>

%font='danger' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'success'
%from alignak_webui.objects.element_state import ElementState
%items_states = ElementState()
%cfg_state = items_states.get_icon_state('service', 'ok')
%icon = cfg_state['icon']
<a id="services-states-popover"
   href="#"
   title="{{_('Overall services states: %d services (%d problems)') % (ss['nb_elts'], ss['nb_problems'])}}"
   data-count="{{ ss['nb_elts'] }}"
   data-problems="{{ ss['nb_problems'] }}"
   data-original-title="{{_('Services states')}}"
   data-toggle="popover"
   data-html="true"
   data-trigger="hover focus">
   <span class="fa fa-{{icon}}"></span>
   <span class="label label-as-badge label-{{font}}">{{ss["nb_problems"] if ss["nb_problems"] else ''}}</span>
</a>

<script>
   // Activate the popover ...
   $('#services-states-popover').popover({
      placement: 'bottom',
      animation: true,
      template: '<div class="popover popover-services"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
      content: function() {
         return $('#services-states-popover-content').html();
      }
   });
</script>
%end
%end
