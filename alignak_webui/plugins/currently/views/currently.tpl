%from bottle import request

%setdefault('refresh', True)
%rebase("fullscreen", css=[], js=[], title=title)

%import json
%from alignak_webui.utils.helper import Helper

%setdefault('currently_panels', None)
%#Set this to True to reset saved parameters
%create_panels_preferences = False
%if create_panels_preferences or not currently_panels:
%currently_panels = {}
%currently_panels['panel_counters_hosts'] = {'collapsed': False}
%currently_panels['panel_counters_services'] = {'collapsed': False}
%currently_panels['panel_percentage_hosts'] = {'collapsed': False}
%currently_panels['panel_percentage_services'] = {'collapsed': False}
%currently_panels['panel_pie_graph_hosts'] = {'collapsed': False}
%currently_panels['panel_pie_graph_services'] = {'collapsed': False}
%currently_panels['panel_line_graph_hosts'] = {'collapsed': False}
%currently_panels['panel_line_graph_services'] = {'collapsed': False}
%create_panels_preferences = True
%end

%setdefault('currently_graphs', None)
%setdefault('hosts_states', ['up','down','unreachable'])
%setdefault('services_states', ['ok','warning','critical','unreachable','unknown'])

%#Set this to True to reset saved parameters
%create_graphs_preferences = False
%if create_graphs_preferences or not currently_graphs:
%currently_graphs = {}
%currently_graphs['pie_graph_hosts'] = {'legend': True, 'title': True, 'states': hosts_states}
%currently_graphs['pie_graph_services'] = {'legend': True, 'title': True, 'states': services_states}
%currently_graphs['line_graph_hosts'] = {'legend': True, 'title': True, 'states': hosts_states}
%currently_graphs['line_graph_services'] = {'legend': True, 'title': True, 'states': services_states}
%create_graphs_preferences = True
%end

%#Set this to True to reset saved parameters
%create_graphs_preferences = False
%if create_graphs_preferences or not 'display_states' in currently_graphs['pie_graph_hosts']:
%currently_graphs['pie_graph_hosts']['display_states'] = {}
%currently_graphs['line_graph_hosts']['display_states'] = {}
%for state in hosts_states:
%currently_graphs['pie_graph_hosts']['display_states'][state] = True
%currently_graphs['line_graph_hosts']['display_states'][state] = True
%end
%currently_graphs['pie_graph_services']['display_states'] = {}
%currently_graphs['line_graph_services']['display_states'] = {}
%for state in services_states:
%currently_graphs['pie_graph_services']['display_states'][state] = True
%currently_graphs['line_graph_services']['display_states'][state] = False if state in ['ok'] else True
%end
%create_graphs_preferences = True
%end

<style>
div.pull-right a, div.pull-right div {
   margin-top: 0px; margin-bottom: 0px;
}
.hosts-count, .services-count {
   font-size: 24px;
}
.hosts-state, .services-state {
   font-size: 12px;
}
</style>

<div id="currently">
<script type="text/javascript">
   var dashboard_logs = false;

   // Application globals
   dashboard_currently = true;

   panels = {{ ! json.dumps(currently_panels) }};
   graphs = {{ ! json.dumps(currently_graphs) }};

   %if create_panels_preferences:
   save_user_preference('currently_panels', JSON.stringify(panels));
   %end
   %if create_graphs_preferences:
   save_user_preference('currently_graphs', JSON.stringify(graphs));
   %end

   var no_default_page_refresh = true;

   // Set moment libray locale
   moment.locale('fr');

   // Function called on each page refresh ... update graphs!
   function on_page_refresh(forced) {
      // Hosts data
      var hosts_count = parseInt($('#one-eye-overall .hosts-all').data("count"));
      var hosts_problems = parseInt($('#one-eye-overall .hosts-all').data("problems"));
      if (! sessionStorage.getItem("hosts_problems")) {
        sessionStorage.setItem("hosts_problems", hosts_problems);
      }
      var old_hosts_problems = Number(sessionStorage.getItem("hosts_problems"));
      if (dashboard_logs) console.debug("Hosts problems count: ", hosts_count, hosts_problems, old_hosts_problems);

      // Services data
      var services_count = parseInt($('#one-eye-overall .services-all').data("count"));
      var services_problems = parseInt($('#one-eye-overall .services-all').data("problems"));
      if (! sessionStorage.getItem("services_problems")) {
        sessionStorage.setItem("services_problems", services_problems);
      }
      var old_services_problems = Number(sessionStorage.getItem("services_problems"));
      if (dashboard_logs) console.debug("Services problems count: ", services_count, services_problems, old_services_problems);

      // Refresh user's preferences
      get_user_preference('currently_panels', function(data) {
         panels=data;
         if (dashboard_logs) console.debug("Saved panels: ", panels);
         get_user_preference('currently_graphs', function(data) {
            graphs=data;
            if (dashboard_logs) console.debug("Saved graphs: ", graphs);

            // Sound alerting
            if (sound_activated) {
               if ((old_hosts_problems < hosts_problems) || (old_services_problems < services_problems)) {
                  playAlertSound();
               }
            }
            raise_message_info("Refresh...");
            if (old_hosts_problems < hosts_problems) {
               var message = (hosts_problems - old_hosts_problems) + " more " + ((hosts_problems - old_hosts_problems)==1 ? "hosts problem" : "hosts problems") + " since last "+app_refresh_period+" seconds."
               raise_message_ko(message);
               if (dashboard_logs) console.debug(message);
            }
            if (hosts_problems < old_hosts_problems) {
               var message = (old_hosts_problems - hosts_problems) + " less " + ((old_hosts_problems - hosts_problems)==1 ? "hosts problem" : "hosts problems") + " since last "+app_refresh_period+" seconds."
               raise_message_ok(message);
               if (dashboard_logs) console.debug(message);
            }
            sessionStorage.setItem("hosts_problems", hosts_problems);
            if (old_services_problems < services_problems) {
               var message = (services_problems - old_services_problems) + " more " + ((services_problems - old_services_problems)==1 ? "services problem" : "services problems") + " since last "+app_refresh_period+" seconds."
               raise_message_ko(message);
               if (dashboard_logs) console.debug(message);
            }
            if (services_problems < old_services_problems) {
               var message = (old_services_problems - services_problems) + " less " + ((old_services_problems - services_problems)==1 ? "services problem" : "services problems") + " since last "+app_refresh_period+" seconds."
               raise_message_ok(message);
               if (dashboard_logs) console.debug(message);
            }
            sessionStorage.setItem("services_problems", services_problems);

            // Hosts pie chart
            if (panels && $("#panel_pie_graph_hosts").is(":visible") && ! panels["panel_pie_graph_hosts"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_pie_graph_hosts', panels["panel_pie_graph_hosts"]);
               var data=[], labels=[], colors=[], hover_colors=[];
               $.each(graphs['pie_graph_hosts']['display_states'], function(state, active) {
                  if (! active) return;
                  var counter_value = parseInt($('#one-eye-overall span.hosts-count[data-state="'+state+'"]').data("count"));

                  labels.push(g_hosts_states[state]['label']);
                  data.push(counter_value);
                  colors.push(g_hosts_states[state]['color'])
                  hover_colors.push(g_hoverBackgroundColor)
               })
               if (dashboard_logs) console.debug('Refresh: panel_pie_graph_hosts data', data);

               // Update graph
               new Chart($("#pie-graph-hosts canvas"), {
                  type: 'doughnut',
                  data: {
                     labels: labels,
                     datasets: [
                        {
                           data: data,
                           backgroundColor: colors,
                           hoverBackgroundColor: hover_colors
                        }
                     ]
                  },
                  options: {
                     title: {
                        display: graphs['pie_graph_hosts']['title'],
                        text: '{{_('Hosts states graph')}}'
                     },
                     legend: {
                        display: graphs['pie_graph_hosts']['legend'],
                        position: 'bottom'
                     }
                  }
               });
            }

            // Hosts line chart
            if (panels && $("#panel_line_graph_hosts").is(":visible") && ! panels["panel_line_graph_hosts"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_line_graph_hosts', panels["panel_line_graph_hosts"]);
               var labels=[];
               %idx=len(history)
               %for ls in history:
                  labels.push('{{ls['_timestamp']}}');
                  %idx=idx-1
               %end
               %for state in ['up', 'unreachable', 'down', 'acknowledged', 'in_downtime']:
                  var data_{{state}}=[];
                  %for ls in history:
                  data_{{state}}.push({{ls["hosts_synthesis"]["nb_" + state]}});
                  %end
               %end
               var data = {
                  labels: labels,
                  datasets: [
                     %for state in ['up', 'unreachable', 'down', 'acknowledged', 'in_downtime']:
                     {
                        label: g_hosts_states["{{state.lower()}}"]['label'],
                        fill: false,
                        lineTension: 0.1,
                        borderWidth: 1,
                        borderColor: g_hosts_states["{{state.lower()}}"]['color'],
                        backgroundColor: g_hosts_states["{{state.lower()}}"]['background'],
                        pointBorderWidth: 1,
                        pointRadius: 1,
                        pointBorderColor: g_hosts_states["{{state.lower()}}"]['color'],
                        pointBackgroundColor: g_hosts_states["{{state.lower()}}"]['background'],
                        data: data_{{state}}
                     },
                     %end
                  ]
               };
               if (dashboard_logs) console.debug('Refresh: panel_line_graph_hosts', data);

               new Chart($("#line-graph-hosts canvas"), {
                  type: 'line',
                  data: data,
                  options: {
                     title: {
                        display: true,
                        text: '{{_('Hosts states history')}}'
                     },
                     legend: {
                        display: true,
                        position: 'bottom'
                     },
                     scales: {
                        xAxes: [{
                           type: 'time',
                           ticks: {
                              fontSize: 10,
                              fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                              autoSkip: true
                           },
                           time: {
                              parser: 'X',
                              tooltipFormat: 'LTS',
                              unit: 'minute',
                              displayFormats: {
                                 second: 'LTS',
                                 minute: 'LTS',
                                 hour: 'LTS',
                                 day: 'LTS'
                              }
                           }
                        }],
                        yAxes: [{
                           ticks: {
                              fontSize: 10,
                              fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                              autoSkip: false
                           },
                           stacked: true
                        }]
                     }
                  }
               });
            }

            // Services pie chart
            if (panels && $("#panel_pie_graph_services").is(":visible") && ! panels["panel_pie_graph_services"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_pie_graph_services', panels["panel_pie_graph_services"]);
               var data=[], labels=[], colors=[], hover_colors=[];
               $.each(graphs['pie_graph_services']['display_states'], function(state, active) {
                  if (! active) return;
                  var counter_value = parseInt($('#one-eye-overall span.services-count[data-state="'+state+'"]').data("count"));

                  // Update table rows
                  labels.push(g_services_states[state]['label']);
                  data.push(counter_value);
                  colors.push(g_services_states[state]['color'])
                  hover_colors.push(g_hoverBackgroundColor)
               });
               if (dashboard_logs) console.debug('Refresh: panel_pie_graph_services data', data);

               // Update graph
               new Chart($("#pie-graph-services canvas"), {
                  type: 'doughnut',
                  data: {
                     labels: labels,
                     datasets: [
                        {
                           data: data,
                           backgroundColor: colors,
                           hoverBackgroundColor: hover_colors
                        }
                     ]
                  },
                  options: {
                     title: {
                        display: graphs['pie_graph_services']['title'],
                        text: '{{_('Services states graph')}}'
                     },
                     legend: {
                        display: graphs['pie_graph_services']['legend'],
                        position: 'bottom'
                     }
                  }
               });
            }

            // Services line chart
            if (panels && $("#panel_line_graph_services").is(":visible") && ! panels["panel_line_graph_services"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_line_graph_services', panels["panel_line_graph_services"]);
               var labels=[];
               %idx=len(history)
               %for ls in history:
                  labels.push('{{ls['_timestamp']}}');
                  %idx=idx-1
               %end
               %for state in ['ok', 'warning', 'critical', 'unreachable', 'unknown', 'acknowledged', 'in_downtime']:
                  var data_{{state}}=[];
                  %for ls in history:
                  data_{{state}}.push({{ls["services_synthesis"]["nb_" + state]}});
                  %end
               %end
               var data = {
                  labels: labels,
                  datasets: [
                     %for state in ['ok', 'warning', 'critical', 'unreachable', 'unknown', 'acknowledged', 'in_downtime']:
                     {
                        label: g_services_states["{{state.lower()}}"]['label'],
                        fill: false,
                        lineTension: 0.1,
                        borderWidth: 1,
                        borderColor: g_services_states["{{state.lower()}}"]['color'],
                        backgroundColor: g_services_states["{{state.lower()}}"]['background'],
                        pointBorderWidth: 1,
                        pointRadius: 2,
                        pointBorderColor: g_services_states["{{state.lower()}}"]['color'],
                        pointBackgroundColor: g_services_states["{{state.lower()}}"]['background'],
                        data: data_{{state}}
                     },
                     %end
                  ]
               };

               new Chart($("#line-graph-services canvas"), {
                  type: 'line',
                  data: data,
                  options: {
                     title: {
                        display: true,
                        text: '{{_('Services states history')}}'
                     },
                     legend: {
                        display: true,
                        position: 'bottom'
                     },
                     scales: {
                        xAxes: [{
                           type: 'time',
                           ticks: {
                              fontSize: 10,
                              fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                              autoSkip: true
                           },
                           time: {
                              parser: 'X',
                              tooltipFormat: 'LTS',
                              unit: 'minute',
                              displayFormats: {
                                 second: 'LTS',
                                 minute: 'LTS',
                                 hour: 'LTS',
                                 day: 'LTS'
                              }
                           }
                        }],
                        yAxes: [{
                           ticks: {
                              fontSize: 10,
                              fontFamily: 'HelveticaNeue, HelveticaNeue, Roboto, ArialRounded',
                              autoSkip: false
                           },
                           stacked: true
                        }]
                     }
                  }
               });
            }

            wait_message('', false);
         });
      });
   }

   $(document).ready(function(){
      on_page_refresh();

      // Date / time
      $('#clock').jclock({ format: '%H:%M:%S' });
      $('#date').jclock({ format: '%A, %B %d' });

      // Fullscreen management
      if (screenfull.enabled) {
         $('a[data-action="fullscreen-request"]').on('click', function() {
            screenfull.request();
         });

         // Fullscreen changed event
         document.addEventListener(screenfull.raw.fullscreenchange, function () {
            if (screenfull.isFullscreen) {
               $('a[data-action="fullscreen-request"]').hide();
            } else {
               $('a[data-action="fullscreen-request"]').show();
            }
         });
      }
   });
</script>

<nav id="topbar" class="navbar navbar-fixed-top">
   <div id="one-eye-toolbar" class="col-xs-12">
      <ul class="nav navbar-nav navbar-left">
         <li>
            <a tabindex="0" role="button"
               data-toggle="tooltip" data-placement="bottom"
               title="{{_('Go back to the dashboard')}}" href="/dashboard">
               <span class="fa fa-home"></span>
               <span class="sr-only">{{_('Go back to the main dashboard')}}</span>
            </a>
         </li>
         <li>
            <a tabindex="0" role="button"
               data-action="fullscreen-request"
               data-toggle="tooltip" data-placement="bottom"
               title="{{_('Fullscreen page')}}" href="#">
               <span class="fa fa-desktop"></span>
               <span class="sr-only">{{_('Fullscreen page')}}</span>
            </a>
         </li>
         %if request.app.config.get('play_sound', 'no') == 'yes':
         <li id="sound_alerting">
            <a tabindex="0" role="button"
               data-action="toggle-sound-alert"
               data-toggle="tooltip" data-placement="bottom"
               title="{{_('Sound alert on/off')}}" href="#">
               <span class="fa fa-music"></span>
               <span class="sr-only">{{_('Change sound playing state')}}</span>
            </a>
         </li>
         %end
      </ul>

      <ul class="nav navbar-nav navbar-right">
         <li>
            <p class="navbar-text font-darkgrey">
               <span id="date"></span>&nbsp;&hyphen;&nbsp;<span id="clock"></span>
            </p>
         </li>
      </ul>
   </div>
</nav>


%if request.app.config.get('play_sound', 'no') == 'yes':
   %include("_sound_play.tpl")
%end

<div class="row" style="margin-top:60px;">
   <div id="one-eye-overall" class="col-xs-12">
      <div class="col-md-6" id="panel_counters_hosts">
         <div class="panel panel-default">
            <div class="panel-heading clearfix">
               <i class="fa fa-server"></i>
               <span class="hosts-all" data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}">
                  {{hs['nb_elts']}} hosts{{! "<em class='font-down'> (%d problems).</em>" % (hs['nb_problems']) if hs['nb_problems'] else '.'}}
               </span>

               <div class="pull-right">
                  <a href="#p_panel_counters_hosts" data-toggle="collapse" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_counters_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
            </div>
            <div id="p_panel_counters_hosts" class="panel-collapse collapse {{'in' if not currently_panels['panel_counters_hosts']['collapsed'] else ''}}">
               <div class="panel-body">
                  %for state in 'up', 'unreachable', 'down':
                  <div class="col-xs-4 col-sm-4 col-md-2 text-center">
                     <a href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}" title="{{ state }}">
                        <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}">{{ hs['nb_' + state] }}</span>
                        <!-- <br/>
                        <span class="hosts-state">{{ state }}</span> -->
                     </a>
                  </div>
                  %end
                  <div class="col-xs-4 col-sm-4 col-md-2 text-center">
                     %state='acknowledged'
                     <a href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}" title="{{ state }}">
                        <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}">{{ hs['nb_' + state] }}</span>
                     </a>
                     <span>/</span>
                     %state='in_downtime'
                     <a href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}" title="{{ state }}">
                        <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}">{{ hs['nb_' + state] }}</span>
                     </a>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <div class="col-md-6" id="panel_counters_services">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-cubes"></i>
               <span class="services-all" data-count="{{ ss['nb_elts'] }}" data-problems="{{ ss['nb_problems'] }}">
                  {{ss['nb_elts']}} services{{! "<em class='font-down'> (%d problems).</em>" % (ss['nb_problems']) if ss['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <a href="#p_panel_counters_services" data-toggle="collapse" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_counters_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
             </div>
            <div id="p_panel_counters_services" class="panel-collapse collapse {{'in' if not currently_panels['panel_counters_services']['collapsed'] else ''}}">
               <div class="panel-body">
                  %for state in 'ok', 'warning', 'critical', 'unreachable', 'unknown':
                  <div class="col-xs-4 col-sm-4 col-md-2 text-center">
                     <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}" class="item_service_{{state}}" title="{{ state }}">
                        <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}">{{ ss['nb_' + state] }}</span>
                     </a>
                  </div>
                  %end
                  <div class="col-xs-4 col-sm-4 col-md-2 text-center">
                     %state='acknowledged'
                     <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}" class="item_service_{{state}}" title="{{ state }}">
                        <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}">{{ ss['nb_' + state] }}</span>
                     </a>
                     <span>/</span>
                     %state='in_downtime'
                     <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}" class="item_service_{{state}}" title="{{ state }}">
                        <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}">{{ ss['nb_' + state] }}</span>
                     </a>
                  </div>
               </div>
            </div>
         </div>
      </div>
   </div>

   <div id="one-eye-icons" class="col-xs-12">
      <div class="col-md-6" id="panel_percentage_hosts">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-server"></i>
               <span class="hosts-all" data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}">
                  {{hs['nb_elts']}} hosts{{! "<em class='font-down'> (%d problems).</em>" % (hs['nb_problems']) if hs['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <a href="#p_panel_percentage_hosts" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_percentage_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
            </div>
            <div id="p_panel_percentage_hosts" class="panel-collapse collapse {{'in' if not currently_panels['panel_percentage_hosts']['collapsed'] else ''}}">
               <div class="panel-body">
                   <div class="row">
                      <!-- Hosts SLA icons -->
                      <div class="col-xs-3 col-sm-3 text-center">
                         <div class="col-xs-12 text-center">
                            %sla = hs['pct_up']
                            %font='ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
                            <a href="{{ webui.get_url('Hosts table') }}" class="sla_hosts_{{font}}">
                               <div>{{sla}}%</div>
                               <i class="fa fa-4x fa-server"></i>
                               <p>{{_('Hosts SLA')}}</p>
                            </a>
                         </div>
                      </div>

                      %for state in 'up', 'unreachable', 'down':
                      <div class="col-xs-3 col-sm-3 col-md-3 text-center">
                         <a role="button" href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}" title="{{ state }}">
                            <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}">{{ hs['pct_' + state] }}%</span>
                            <br/>
                            <span class="hosts-state">{{ state }}</span>
                         </a>
                      </div>
                      %end
                   </div>
                   <div class="row">
                      <!-- Hosts SLA icons -->
                      <div class="col-xs-3 col-sm-3 text-center">
                         %unmanaged_problems=hs['nb_problems'] - (hs['nb_acknowledged']+hs['nb_in_downtime'])
                         %pct_unmanaged_problems=round(100.0 * unmanaged_problems / hs['nb_elts'], 2) if hs['nb_elts'] else -1
                         <div class="col-xs-12 text-center">
                            <a role="button" href="{{ webui.get_url('Hosts table') }}?search=ls_state:down" class="sla_hosts_problems">
                               <span class="hosts-count" data-count="{{ hs['nb_problems'] }}" data-state="problem">{{ pct_unmanaged_problems }}%</span>
                               <br/>
                               <span class="hosts-state">{{_('Unmanaged problems')}}</span>
                            </a>
                         </div>
                      </div>

                      %for state in 'acknowledged', 'in_downtime':
                      <div class="col-xs-3 col-sm-3 col-md-3 text-center">
                         <a role="button" href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}" title="{{ state }}">
                            <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}">{{ hs['pct_' + state] }}%</span>
                            <br/>
                            <span class="hosts-state">{{ state }}</span>
                         </a>
                      </div>
                      %end
                   </div>
               </div>
            </div>
            </div>
      </div>
      <div class="col-md-6" id="panel_percentage_services">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-cubes"></i>
               <span class="services-all" data-count="{{ ss['nb_elts'] }}" data-problems="{{ ss['nb_problems'] }}">
                  {{ss['nb_elts']}} services{{! "<em class='font-down'> (%d problems).</em>" % (ss['nb_problems']) if ss['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <a href="#p_panel_percentage_services" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_percentage_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
            </div>
            <div id="p_panel_percentage_services" class="panel-collapse collapse {{'in' if not currently_panels['panel_percentage_services']['collapsed'] else ''}}">
               <div class="panel-body">
                  <!-- Services SLA icons -->
                  <div class="row">
                      <div class="col-xs-3 col-sm-3 text-center">
                         <div class="col-xs-12 text-center">
                            %sla = ss['pct_ok']
                            %font='ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
                            <a href="/all?search=type:service" class="sla_services_{{font}}">
                               <div>{{sla}}%</div>

                               <i class="fa fa-4x fa-server font-{{font}}"></i>
                               <p>{{_('Services SLA')}}</p>
                            </a>
                         </div>
                      </div>

                      %for state in 'ok', 'warning', 'critical', 'unreachable', 'unknown':
                      <div class="col-xs-3 col-sm-3 col-md-3 text-center">
                          <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}" class="item_service_{{state}}">
                              <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}">{{ ss['pct_' + state] }}%</span>
                              <br/>
                              <span class="services-state">{{ state }}</span>
                          </a>
                      </div>
                      %end
                  </div>
                  <div class="row">
                      <div class="col-xs-3 col-sm-3 text-center">
                         %unmanaged_problems=ss['nb_problems'] - (ss['nb_acknowledged']+ss['nb_in_downtime'])
                         %pct_unmanaged_problems=round(100.0 * unmanaged_problems / ss['nb_elts'], 2) if ss['nb_elts'] else -1
                         <div class="col-xs-12 text-center">
                             <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:down" class="sla_services_problems">
                                 <span class="services-count" data-count="{{ ss['nb_problems'] }}" data-state="problem">{{ pct_unmanaged_problems }}%</span>
                                 <br/>
                                 <span class="services-state">{{_('Unmanaged problems')}}</span>
                             </a>
                         </div>
                      </div>

                      %for state in 'acknowledged', 'in_downtime':
                      <div class="col-xs-3 col-sm-3 col-md-3 text-center">
                          <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}" class="item_service_{{state}}">
                              <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}">{{ ss['pct_' + state] }}%</span>
                              <br/>
                              <span class="services-state">{{ state }}</span>
                          </a>
                      </div>
                      %end
                  </div>
               </div>
            </div>
         </div>
      </div>
   </div>

   <div id="livestate-graphs" class="col-xs-12">
      <div class="col-md-6" id="panel_pie_graph_hosts">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-pie-chart"></i>
               <span class="hosts-all" data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}">
                  {{hs['nb_elts']}} hosts{{! "<em class='font-down'> (%d problems).</em>" % (hs['nb_problems']) if hs['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <div class="btn-group">
                     <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
                        <i class="fa fa-gear fa-fw"></i>
                        <span class="caret"></span>
                     </button>
                     <ul class="dropdown-menu pull-right" role="menu">
                        <li>
                           <a href="#" data-action="toggle-legend" data-graph="pie_graph_hosts">
                              <i class="fa fa-check fa-fw" style="{{'display:none;' if not currently_graphs['pie_graph_hosts']['legend'] else ''}}"></i>{{_('Display graph legend?')}}
                           </a>
                        </li>
                        <li>
                           <a href="#" data-action="toggle-title" data-graph="pie_graph_hosts">
                              <i class="fa fa-check fa-fw" style="{{'display:none;' if not currently_graphs['pie_graph_hosts']['title'] else ''}}"></i>{{_('Display graph title?')}}
                           </a>
                        </li>
                        <li class="divider"></li>
                        %for state in currently_graphs['pie_graph_hosts']['states']:
                        <li>
                           <a href="#" data-action="toggle-state" data-graph="pie_graph_hosts" data-state="{{state}}" class="{{'active' if currently_graphs['pie_graph_hosts']['display_states'][state] else ''}}">
                              <i class="fa fa-check fa-fw" style="{{'display:none;' if not currently_graphs['pie_graph_hosts']['display_states'][state] else ''}}"></i>{{_('Display state %s?') % state}}
                           </a>
                        </li>
                        %end
                     </ul>
                  </div>
                  <a href="#p_panel_pie_graph_hosts" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_pie_graph_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
            </div>
            <div id="p_panel_pie_graph_hosts" class="panel-collapse collapse {{'in' if not currently_panels['panel_pie_graph_hosts']['collapsed'] else ''}}">
               <div class="panel-body">
                  <!-- Chart -->
                  <div id="pie-graph-hosts">
                     <canvas></canvas>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <div class="col-md-6" id="panel_pie_graph_services">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-pie-chart"></i>
               <span class="services-all" data-count="{{ ss['nb_elts'] }}" data-problems="{{ ss['nb_problems'] }}">
                  {{ss['nb_elts']}} services{{! "<em class='font-down'> (%d problems).</em>" % (ss['nb_problems']) if ss['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <div class="btn-group">
                     <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
                        <i class="fa fa-gear fa-fw"></i>
                        <span class="caret"></span>
                     </button>
                     <ul class="dropdown-menu pull-right" role="menu">
                        <li>
                           <a href="#" data-action="toggle-legend" data-graph="pie_graph_services">
                              <i class="fa fa-check fa-fw" style="{{'display:none;' if not currently_graphs['pie_graph_services']['legend'] else ''}}"></i>{{_('Display graph legend?')}}
                           </a>
                        </li>
                        <li>
                           <a href="#" data-action="toggle-title" data-graph="pie_graph_services">
                              <i class="fa fa-check fa-fw" style="{{'display:none;' if not currently_graphs['pie_graph_services']['title'] else ''}}"></i>{{_('Display graph title?')}}
                           </a>
                        </li>
                        <li class="divider"></li>
                        %for state in currently_graphs['pie_graph_services']['states']:
                        <li>
                           <a href="#" data-action="toggle-state" data-graph="pie_graph_services" data-state="{{state}}" class="{{'active' if currently_graphs['pie_graph_services']['display_states'][state] else ''}}">
                              <i class="fa fa-check fa-fw" style="{{'display:none;' if not currently_graphs['pie_graph_services']['display_states'][state] else ''}}"></i>{{_('Display state %s?') % state}}
                           </a>
                        </li>
                        %end
                     </ul>
                  </div>
                  <a href="#p_panel_pie_graph_services" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_pie_graph_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
            </div>
            <div id="p_panel_pie_graph_services" class="panel-collapse collapse {{'in' if not currently_panels['panel_pie_graph_services']['collapsed'] else ''}}">
               <div class="panel-body">
                  <!-- Chart -->
                  <div id="pie-graph-services">
                     <canvas></canvas>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <div class="col-md-6" id="panel_line_graph_hosts">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-bar-chart"></i>
               <span class="hosts-all" data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}">
                  {{hs['nb_elts']}} hosts{{! "<em class='font-down'> (%d problems).</em>" % (hs['nb_problems']) if hs['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <a href="#p_panel_line_graph_hosts" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_line_graph_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
              </div>
            </div>
            <div id="p_panel_line_graph_hosts" class="panel-collapse collapse {{'in' if not currently_panels['panel_line_graph_hosts']['collapsed'] else ''}}">
               <div class="panel-body">
                  <!-- Chart -->
                  <div id="line-graph-hosts">
                     <canvas></canvas>
                  </div>
               </div>
            </div>
         </div>
      </div>
      <div class="col-md-6" id="panel_line_graph_services">
         <div class="panel panel-default">
            <div class="panel-heading">
               <i class="fa fa-bar-chart"></i>
               <span class="services-all" data-count="{{ ss['nb_elts'] }}" data-problems="{{ ss['nb_problems'] }}">
                  {{ss['nb_elts']}} services{{! "<em class='font-down'> (%d problems).</em>" % (ss['nb_problems']) if ss['nb_problems'] else '.'}}
               </span>
               <div class="pull-right">
                  <a href="#p_panel_line_graph_services" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not currently_panels['panel_line_graph_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
               </div>
            </div>
            <div id="p_panel_line_graph_services" class="panel-collapse collapse {{'in' if not currently_panels['panel_line_graph_services']['collapsed'] else ''}}">
               <div class="panel-body">
                  <!-- Chart -->
                  <div id="line-graph-services">
                     <canvas></canvas>
                  </div>
               </div>
            </div>
         </div>
      </div>
   </div>
</div>

<script type="text/javascript">
   // Panels collapse state
   $('.panel').on('hidden.bs.collapse', function () {
      wait_message('{{_('Saving configuration...')}}', true)

      panels[$(this).parent().attr('id')].collapsed = true;
      $(this).find('.fa-minus-square').removeClass('fa-minus-square').addClass('fa-plus-square');
      save_user_preference('currently_panels', JSON.stringify(panels), function() {
         wait_message('', false)
         // Page refresh required
         refresh_required = true;
      });
   });
   $('.panel').on('shown.bs.collapse', function () {
      wait_message('{{_('Saving configuration...')}}', true)

      panels[$(this).parent().attr('id')].collapsed = false;
      $(this).find('.fa-plus-square').removeClass('fa-plus-square').addClass('fa-minus-square');
      save_user_preference('currently_panels', JSON.stringify(panels), function() {
         wait_message('', false)
         // Page refresh required
         refresh_required = true;
      });
   });

   // Graphs options
   $('[data-action="toggle-title"]').on('click', function () {
      wait_message('{{_('Saving configuration...')}}', true)

      if (dashboard_logs) console.debug('Toggle title', graphs[$(this).data('graph')]);
      graphs[$(this).data('graph')].title = ! graphs[$(this).data('graph')].title;
      if (graphs[$(this).data('graph')].title) {
         $(this).children('i').show();
      } else {
         $(this).children('i').hide();
      }
      save_user_preference('currently_graphs', JSON.stringify(graphs), function() {
         wait_message('', false)
         // Page refresh required
         refresh_required = true;
      });
   });
   $('[data-action="toggle-legend"]').on('click', function () {
      wait_message('{{_('Saving configuration...')}}', true)

      if (dashboard_logs) console.debug('Toggle legend', graphs[$(this).data('graph')]);
      graphs[$(this).data('graph')].legend = ! graphs[$(this).data('graph')].legend;
      if (graphs[$(this).data('graph')].legend) {
         $(this).children('i').show();
      } else {
         $(this).children('i').hide();
      }
      save_user_preference('currently_graphs', JSON.stringify(graphs), function() {
         wait_message('', false)
         // Page refresh required
         refresh_required = true;
      });
   });
   $('[data-action="toggle-state"]').on('click', function () {
      wait_message('{{_('Saving configuration...')}}', true)

      if (dashboard_logs) console.debug('Toggle state', graphs[$(this).data('graph')]);
      graphs[$(this).data('graph')]['display_states'][$(this).data('state')] = ! graphs[$(this).data('graph')]['display_states'][$(this).data('state')];
      if (graphs[$(this).data('graph')]['display_states'][$(this).data('state')]) {
         $(this).children('i').show();
      } else {
         $(this).children('i').hide();
      }
      save_user_preference('currently_graphs', JSON.stringify(graphs), function() {
         wait_message('', false)
         // Page refresh required
         refresh_required = true;
      });
   });
</script>

</div>