%setdefault('ls', None)

<style>
    #problems-synthesis {
        margin-top: 0px;
        margin-bottom: 10px;
    }

    .icon-title {
        display: block;

        color: #666;
        state-size: 1em;
    }

    .icon-badge {
        background-color: #cccccc;
        border-radius: 3px;
        state-size: 1em;
        text-transform: uppercase;

        width: 100px;

        opacity: 0.9;
    }

    .icon-badge-top {
        background-color: #ffffff;
        state-size: 1.3em;
    }

    #problems-synthesis a span.fa {
        opacity: 0.8;
    }
    .icon-info {
        color: #2980b9;
    }

    .icon-danger {
        color: #e74c3c;
    }

    .icon-warning {
        color: #e67e22;
    }

    .icon-success {
        color: #27ae60;
    }
</style>

<div id="problems-synthesis" class="row">
    %if ls is None:
    %ls = datamgr.get_livesynthesis()
    %end
    <div class="col-xs-4">
        %hs = ls['hosts_synthesis']
        %if hs:
        %state='critical' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'ok'
        %from alignak_webui.objects.element_state import ElementState
        %cfg_state = ElementState().get_icon_state('host', 'up')
        %icon = cfg_state['icon']
        <center>
            <div class="icon-badge icon-badge-top" title="{{_('Number of unhandled hosts problems')}}">
                <strong><span class="item_host_{{state}}">{{hs["nb_problems"]}}</span></strong>
            </div>
            <div>
                <a href="{{ webui.get_url('Hosts table') }}">
                    <span class="fa fa-4x fa-{{icon}} item_host_{{state}}"></span>
                </a>
            </div>
            <div class="icon-badge text-primary" title="{{_('Number of monitored hosts')}}">
                <strong>{{hs["nb_elts"]}}</strong>
            </div>
        </center>
        %end
    </div>

    <div class="col-xs-4">
        %ss = ls['services_synthesis']
        %if ss:
        %state='critical' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'ok'
        %from alignak_webui.objects.element_state import ElementState
        %cfg_state = ElementState().get_icon_state('service', 'ok')
        %icon = cfg_state['icon']
        <center>
            <div class="icon-badge icon-badge-top" title="{{_('Number of unhandled services problems')}}">
                <strong><span class="item_host_{{state}}">{{ss["nb_problems"]}}</span></strong>
            </div>
            <div>
                <a class="item_host_{{state}}" href="{{ webui.get_url('Services table') }}">
                    <span class="fa fa-4x fa-{{icon}}"></span>
                </a>
            </div>
            <div class="icon-badge text-primary" title="{{_('Number of monitored services')}}">
                <strong>{{ss["nb_elts"]}}</strong>
            </div>
        </center>
        %end
    </div>

    <div class="col-xs-4">
        %if hs and ss:
        %problems = hs['nb_problems'] + ss['nb_problems']
        %elements = hs['nb_elts'] + ss['nb_elts']
        %pct_problems = round(100.0 * problems / elements, 2) if elements else 0.0
        %state='critical' if pct_problems >= hs['global_critical_threshold'] else 'warning' if pct_problems >= hs['global_warning_threshold'] else 'ok'
        <center>
            <div class="icon-badge icon-badge-top" title="{{_('Number of problems')}}">
                <strong><span class="item_host_{{state}}">{{hs["nb_problems"] + ss["nb_problems"]}}</span></strong>
            </div>
            <div>
                <a href="{{ webui.get_url('Hosts table') }}?search=ls_state_id:1 ls_state_id:2">
                    <span class="fa fa-4x fa-exclamation-triangle item_host_{{state}}"></span>
                </a>
            </div>
            <div class="icon-badge text-primary" title="{{_('Number of monitored items')}}">
                <strong>{{hs["nb_elts"] + ss["nb_elts"]}}</strong>
            </div>
        </center>
        %end
    </div>
</div>
