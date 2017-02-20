%setdefault('ls', None)

<style>
#problems-synthesis {
    margin-top: 15px;
}

.icon-title {
    display: block;

    color: #666;
    font-size: 1em;
}

.icon-badge {
    background-color: #999999;
    border-radius: 3px;
    color: #ffffff;
    font-size: 1em;
    text-transform: uppercase;

    width: 45%;
    max-width: 50px;
    position: relative;
    bottom: 6em;

    opacity: 0.75;
}
.icon-badge-left {
    float: left;
    left: 52%;
}
.icon-badge-right {
    float: right;
    right: 52%;
}

#problems-synthesis a span.fa {
    opacity: 0.6;
}
.icon-info {
    color: #337ABF;
}

.icon-danger {
    color: #FF2727;
}

.icon-warning {
    color: #FFA827;
}

.icon-success {
    color: #7AB317;
}

.icon-badge-info {
    background-color: #337ABF;
}

.icon-badge-danger {
    background-color: #FF2727;
}

.icon-badge-warning {
    background-color: #FFA827;
}

.icon-badge-success {
    background-color: #7AB317;
}
</style>

<div id="problems-synthesis" class="row">
    %if ls is None:
    %ls = datamgr.get_livesynthesis()
    %end
    <div class="col-sm-4 col-xs-6">
        %hs = ls['hosts_synthesis']
        %if hs:
        %font='danger' if hs['pct_problems'] >= hs['critical_threshold'] else 'warning' if hs['pct_problems'] >= hs['warning_threshold'] else 'success'
        %from alignak_webui.objects.element_state import ElementState
        %cfg_state = ElementState().get_icon_state('host', 'up')
        %icon = cfg_state['icon']
        <center>
            <a href="{{ webui.get_url('Hosts table') }}">
                <span class="fa fa-4x fa-{{icon}} icon-{{font}}"></span>
                <span class="icon-title"><span class="fa fa-plus"></span>&nbsp;{{_('Hosts')}}</span>
                <span class="icon-badge icon-badge-left icon-badge-info" title="{{_('Number of monitored hosts')}}">{{hs["nb_elts"]}}</span>
                <span class="icon-badge icon-badge-right icon-badge-{{font}}" title="{{_('Number of unhandled hosts problems')}}">{{hs["nb_problems"]}}</span>
            </a>
        </center>
        %end
    </div>

    <div class="col-sm-4 col-xs-6">
        %ss = ls['services_synthesis']
        %if ss:
        %font='danger' if ss['pct_problems'] >= ss['critical_threshold'] else 'warning' if ss['pct_problems'] >= ss['warning_threshold'] else 'success'
        %from alignak_webui.objects.element_state import ElementState
        %cfg_state = ElementState().get_icon_state('service', 'ok')
        %icon = cfg_state['icon']
        <center>
            <a class="icon-{{font}}" href="{{ webui.get_url('Services table') }}">
                <span class="fa fa-4x fa-{{icon}} icon-{{font}}"></span>
                <span class="icon-title"><span class="fa fa-plus"></span>&nbsp;{{_('Services')}}</span>
                <div class="icon-badge icon-badge-left icon-badge-info" title="{{_('Number of monitored services')}}">{{ss["nb_elts"]}}</div>
                <div class="icon-badge icon-badge-right icon-badge-{{font}}" title="{{_('Number of unhandled services problems')}}">{{ss["nb_problems"]}}</div>
            </a>
        </center>
        %end
    </div>

    <div class="col-sm-4 col-xs-6">
        %if hs and ss:
        %problems = hs['nb_problems'] + ss['nb_problems']
        %elements = hs['nb_elts'] + ss['nb_elts']
        %pct_problems = round(100.0 * problems / elements, 2) if elements else 0.0
        %font='danger' if pct_problems >= hs['global_critical_threshold'] else 'warning' if pct_problems >= hs['global_warning_threshold'] else 'success'
        <center>
            <a href="{{ webui.get_url('Hosts table') }}?search=ls_state_id:1 ls_state_id:2">
                <span class="fa fa-4x fa-exclamation-triangle icon-{{font}}"></span>
                <span class="icon-title"><span class="fa fa-plus"></span>&nbsp;{{_('Problems')}}</span>
                <span class="icon-badge icon-badge-left icon-badge-info" title="{{_('Number of monitored items')}}">{{hs["nb_elts"] + ss["nb_elts"]}}</span>
                <span class="icon-badge icon-badge-right icon-badge-{{font}}" title="{{_('Number of problems')}}">{{hs["nb_problems"] + ss["nb_problems"]}}</span>
            </a>
        </center>
        %end
    </div>
<!--
  <div class="col-sm-2 col-xs-5">
     %if hs and ss:

     %# TO BE REPLACED WITH IMPACTS DATA ...

     %problems = hs['nb_problems'] + ss['nb_problems']
     %elements = hs['nb_elts'] + ss['nb_elts']
     %pct_problems = round(100.0 * problems / elements, 2) if elements else 0.0
     %font='info'
     <center>
        <a href="{{ webui.get_url('Services table') }}">
           <span class="fa fa-4x fa-bolt icon-{{font}}"></span>
           <span class="icon-title"><span class="fa fa-plus"></span>&nbsp;{{_('Impacts')}}</span>
           <span class="icon-badge icon-badge-left icon-badge-info" title="{{_('Number of monitored items')}}">{{hs["nb_elts"] + ss["nb_elts"]}}</span>
           <span class="icon-badge icon-badge-right icon-badge-{{font}}" title="{{_('Number of problems')}}">{{hs["nb_problems"] + ss["nb_problems"]}}</span>
        </a>
     </center>
     %end
  </div>
-->
</div>
