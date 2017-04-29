%from bottle import request

%setdefault('ls', None)

%webui = request.app.config['webui']
%datamgr = webui.datamgr
%if datamgr is not None:
%import time
%from alignak_webui.objects.element_state import ElementState
%from alignak_webui.objects.item_host import Host
%from alignak_webui.objects.item_service import Service

%if request.app.config.get('header_refresh_period', '30') != '0':

%if ls is None:
%ls = datamgr.get_livesynthesis()
%end
%hs = ls['hosts_synthesis']
%ss = ls['services_synthesis']

<div id="hosts-states-popover-content" class="hidden">
    <table class="table table-invisible">
    <tbody>
        <tr>
            %for state in ['up', 'unreachable', 'down', 'acknowledged', 'in_downtime']:
            <td>
                %title = _('%s hosts %s (%s%%)') % (hs["nb_" + state], state, hs["pct_" + state])
                %label = "%s <i>(%s%%)</i>" % (hs["nb_" + state], hs["pct_" + state])
                %if state in ['up', 'unreachable', 'down']:
                    <a href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}">
                %elif state in ['acknowledged']:
                    <a href="{{ webui.get_url('Hosts table') }}?search=ls_acknowledged:yes">
                %elif state in ['in_downtime']:
                    <a href="{{ webui.get_url('Hosts table') }}?search=ls_downtime:yes">
                %end
                %h = Host({'ls_state': state, 'active_checks_enabled': True})
                {{! h.get_html_state(text=label, title=title, disabled=(not hs["nb_" + state]))}}
                </a>
            </td>
            %end
        </tr>
    </tbody>
    </table>
</div>

<li id="overall-hosts-states" class="pull-left">
%font='danger' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'success'
%items_states = ElementState()
%cfg_state = items_states.get_icon_state('host', 'up')
%icon = cfg_state['icon']
<a id="hosts-states-popover"
    href="#"
    title="{{_('Overall hosts states: %d hosts (%d problems)') % (hs['nb_elts'], hs['nb_problems'])}}"
    data-count="{{ hs['nb_elts'] }}"
    data-problems="{{ hs['nb_problems'] }}"
    data-original-title="{{_('Hosts states')}}"
    data-toggle="popover"
    data-html="true"
    data-trigger="hover focus">
    <span class="fa fa-w fa-{{icon}}"></span>
    <span class="label label-as-badge label-{{font}}">{{hs["nb_problems"] if hs["nb_problems"] > 0 else ''}}</span>
</a>
</li>

<script>
    // Activate the popover ...
    $('#hosts-states-popover').popover({
        placement: 'bottom',
        animation: true,
        container: 'body',
        template: '<div class="popover popover-hosts"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
        content: function() {
            return $('#hosts-states-popover-content').html();
        }
    });
</script>

<div id="services-states-popover-content" class="hidden">
    <table class="table table-invisible">
    <tbody>
        <tr>
            %for state in ['ok', 'warning', 'critical', 'unknown', 'unreachable', 'acknowledged', 'in_downtime']:
            <td>
                %title = _('%s services %s (%s%%)') % (ss["nb_" + state], state, ss["pct_" + state])
                %label = "%s <i>(%s%%)</i>" % (ss["nb_" + state], ss["pct_" + state])
                %if state in ['ok', 'warning', 'critical', 'unknown', 'unreachable']:
                    <a href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}">
                %elif state in ['acknowledged']:
                    <a href="{{ webui.get_url('Services table') }}?search=ls_acknowledged:yes">
                %elif state in ['in_downtime']:
                    <a href="{{ webui.get_url('Services table') }}?search=ls_downtime:yes">
                %end
                %s = Service({'ls_state': state, 'active_checks_enabled': True})
                {{! s.get_html_state(text=label, title=title, disabled=(not ss["nb_" + state]))}}
                </a>
            </td>
            %end
        </tr>
    </tbody>
    </table>
</div>

<li id="overall-services-states" class="pull-left">
%font='danger' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'success'
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
    <span class="fa fa-w fa-{{icon}}"></span>
    <span class="label label-as-badge label-{{font}}">{{ss["nb_problems"] if ss["nb_problems"] else ''}}</span>
</a>
</li>

<script>
    // Activate the popover ...
    $('#services-states-popover').popover({
        placement: 'bottom',
        animation: true,
        container: 'body',
        template: '<div class="popover popover-services"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
        content: function() {
            return $('#services-states-popover-content').html();
        }
    });
</script>
%end
%end
