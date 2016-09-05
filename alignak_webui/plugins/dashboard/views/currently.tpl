%from bottle import request

%setdefault('refresh', True)
%rebase("fullscreen", css=['dashboard/htdocs/css/currently.css'], js=[], title=title)

%import json
%from alignak_webui.utils.helper import Helper

%setdefault('panels', None)
%#Set this to True to reset saved parameters
%create_panels_preferences = True
%if create_panels_preferences or not panels:
%panels = {}
%panels['panel_counters_hosts'] = {'collapsed': False}
%panels['panel_counters_services'] = {'collapsed': False}
%panels['panel_percentage_hosts'] = {'collapsed': False}
%panels['panel_percentage_services'] = {'collapsed': False}
%panels['panel_pie_graph_hosts'] = {'collapsed': False}
%panels['panel_pie_graph_services'] = {'collapsed': False}
%panels['panel_line_graph_hosts'] = {'collapsed': False}
%panels['panel_line_graph_services'] = {'collapsed': False}
%create_panels_preferences = True
%end

%setdefault('graphs', None)
%setdefault('hosts_states', ['up','down','unreachable'])
%setdefault('services_states', ['ok','warning','critical','unknown'])

%#Set this to True to reset saved parameters
%create_graphs_preferences = True
%if create_graphs_preferences or not graphs:
%graphs = {}
%graphs['pie_graph_hosts'] = {'legend': True, 'title': True, 'states': hosts_states}
%graphs['pie_graph_services'] = {'legend': True, 'title': True, 'states': services_states}
%graphs['line_graph_hosts'] = {'legend': True, 'title': True, 'states': hosts_states}
%graphs['line_graph_services'] = {'legend': True, 'title': True, 'states': services_states}
%create_graphs_preferences = True
%end

%#Set this to True to reset saved parameters
%create_graphs_preferences = False
%if create_graphs_preferences or not 'display_states' in graphs['pie_graph_hosts']:
%graphs['pie_graph_hosts']['display_states'] = {}
%graphs['line_graph_hosts']['display_states'] = {}
%for state in hosts_states:
%graphs['pie_graph_hosts']['display_states'][state] = True
%graphs['line_graph_hosts']['display_states'][state] = True
%end
%graphs['pie_graph_services']['display_states'] = {}
%graphs['line_graph_services']['display_states'] = {}
%for state in services_states:
%graphs['pie_graph_services']['display_states'][state] = True
%graphs['line_graph_services']['display_states'][state] = False if state in ['ok'] else True
%end
%create_graphs_preferences = True
%end

%setdefault('hosts_states_queue_length', 30)
%setdefault('services_states_queue_length', 30)

<div id="currently">
<script type="text/javascript">
   var dashboard_logs = true;

   // Application globals
   dashboard_currently = true;

   panels = {{ ! json.dumps(panels) }};
   graphs = {{ ! json.dumps(graphs) }};

   %if create_panels_preferences:
   save_user_preference('panels', JSON.stringify(panels));
   %end
   %if create_graphs_preferences:
   save_user_preference('graphs', JSON.stringify(graphs));
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
      get_user_preference('panels', function(panels_data) {
         panels=panels_data;
         get_user_preference('graphs', function(graphs_data) {
            graphs=graphs_data;

            // Sound alerting
            if (sound_activated) {
               if ((old_hosts_problems < hosts_problems) || (old_services_problems < services_problems)) {
                  playAlertSound();
               }
            }
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
            if ($("#panel_pie_graph_hosts").is(":visible") && ! panels["panel_pie_graph_hosts"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_pie_graph_hosts', graphs['pie_graph_hosts']);
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
            if ($("#panel_line_graph_hosts").is(":visible") && ! panels["panel_line_graph_hosts"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_line_graph_hosts', graphs['line_graph_hosts']);
               var labels=[];
               %idx=len(hosts_states_queue)
               %for ls in hosts_states_queue:
                  labels.push('{{ls['date']}}');
                  %idx=idx-1
               %end
               %for state in ['up', 'unreachable', 'down', 'acknowledged', 'in_downtime']:
                  var data_{{state}}=[];
                  %for ls in hosts_states_queue:
                  data_{{state}}.push({{ls["hs"]["nb_" + state]}});
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
            if ($("#panel_pie_graph_services").is(":visible") && ! panels["panel_pie_graph_services"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_pie_graph_services', graphs['pie_graph_services']);
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
            if ($("#panel_line_graph_services").is(":visible") && ! panels["panel_line_graph_services"].collapsed) {
               if (dashboard_logs) console.debug('Refresh: panel_line_graph_services', graphs['line_graph_services']);
               var labels=[];
               %idx=len(services_states_queue)
               %for ls in services_states_queue:
                  labels.push('{{ls['date']}}');
                  %idx=idx-1
               %end
               %for state in ['ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime']:
                  var data_{{state}}=[];
                  %for ls in services_states_queue:
                  data_{{state}}.push({{ls["ss"]["nb_" + state]}});
                  %end
               %end
               var data = {
                  labels: labels,
                  datasets: [
                     %for state in ['ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime']:
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

%hs = datamgr.get_livesynthesis()['hosts_synthesis']
%ss = datamgr.get_livesynthesis()['services_synthesis']

<style>
div.pull-right a, div.pull-right div {
   margin-top: 0px; margin-bottom: 0px;
}

.hosts-count, .services-count {
   font-size: 32px;
}
.hosts-state, .services-state {
   font-size: 16px;
}
</style>
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
                     <a href="#p_panel_counters_hosts" data-toggle="collapse" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_counters_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
               </div>
               <div id="p_panel_counters_hosts" class="panel-collapse collapse {{'in' if not panels['panel_counters_hosts']['collapsed'] else ''}}">
                  <div class="panel-body">
                     %for state in 'up', 'unreachable', 'down':
                     <div class="col-xs-6 col-md-3 text-center">
                        %label = "%d<br/><em>(%s)</em>" % (hs['nb_' + state], state)
                        <a role="button" href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}">
                           <span class="hosts-count" data-count="{{ hs['nb_' + state] }}" data-state="{{ state }}">{{ hs['nb_' + state] }}</span>
                           <br/>
                           <span class="hosts-state">{{ state }}</span>
                        </a>
                     </div>
                     %end
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
                     <a href="#p_panel_counters_services" data-toggle="collapse" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_counters_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
                </div>
               <div id="p_panel_counters_services" class="panel-collapse collapse {{'in' if not panels['panel_counters_services']['collapsed'] else ''}}">
                  <div class="panel-body">
                     %for state in 'ok', 'warning', 'critical', 'unknown':
                     <div class="col-xs-6 col-md-3 text-center">
                        %label = "%d<br/><em>(%s)</em>" % (ss['nb_' + state], state)
                        <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:{{state.upper()}}" class="item_service_{{state}}">
                           <span class="services-count" data-count="{{ ss['nb_' + state] }}" data-state="{{ state }}">{{ ss['nb_' + state] }}</span>
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

      <div id="one-eye-icons" class="col-xs-12">
         <div class="col-md-6" id="panel_percentage_hosts">
            <div class="panel panel-default">
               <div class="panel-heading">
                  <i class="fa fa-server"></i>
                  <span class="hosts-all" data-count="{{ hs['nb_elts'] }}" data-problems="{{ hs['nb_problems'] }}">
                     {{hs['nb_elts']}} hosts{{! "<em class='font-down'> (%d problems).</em>" % (hs['nb_problems']) if hs['nb_problems'] else '.'}}
                  </span>
                  <div class="pull-right">
                     <a href="#p_panel_percentage_hosts" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_percentage_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
               </div>
               <div id="p_panel_percentage_hosts" class="panel-collapse collapse {{'in' if not panels['panel_percentage_hosts']['collapsed'] else ''}}">
                  <div class="panel-body">
                     <!-- Hosts SLA icons -->
                     <div class="col-xs-4 col-sm-4 text-center">
                        <div class="col-xs-12 text-center">
                           %sla = (100 - hs['pct_up'])
                           %font='ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
                           <a href="{{ webui.get_url('Hosts table') }}" class="sla_hosts_{{font}}">
                              <div>{{sla}}%</div>

                              <i class="fa fa-4x fa-server"></i>
                              <p>{{_('Hosts SLA')}}</p>
                           </a>
                        </div>
                        %known_problems=hs['nb_acknowledged']+hs['nb_in_downtime']+hs['nb_problems']
                        %pct_known_problems=round(100.0 * known_problems / hs['nb_elts'], 2) if hs['nb_elts'] else -1
                        <div class="col-xs-12 text-center">
                           <a role="button" href="{{ webui.get_url('Hosts table') }}?search=ls_state:down" class="sla_hosts_problems">
                              <span class="hosts-count" data-count="{{ known_problems }}" data-state="problem">{{ pct_known_problems }}%</span>
                              <br/>
                              <span class="hosts-state">{{_('Known problems')}}</span>
                           </a>
                        </div>
                     </div>

                     %for state in 'up', 'unreachable', 'down':
                     <div class="col-xs-4 col-sm-4 text-center">
                        <a role="button" href="{{ webui.get_url('Hosts table') }}?search=ls_state:{{state.upper()}}" class="item_host_{{state}}">
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
         <div class="col-md-6" id="panel_percentage_services">
            <div class="panel panel-default">
               <div class="panel-heading">
                  <i class="fa fa-cubes"></i>
                  <span class="services-all" data-count="{{ ss['nb_elts'] }}" data-problems="{{ ss['nb_problems'] }}">
                     {{ss['nb_elts']}} services{{! "<em class='font-down'> (%d problems).</em>" % (ss['nb_problems']) if ss['nb_problems'] else '.'}}
                  </span>
                  <div class="pull-right">
                     <a href="#p_panel_percentage_services" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_percentage_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
               </div>
               <div id="p_panel_percentage_services" class="panel-collapse collapse {{'in' if not panels['panel_percentage_services']['collapsed'] else ''}}">
                  <div class="panel-body">
                     <!-- Services SLA icons -->
                     <div class="col-xs-4 col-sm-4 text-center">
                        <div class="col-xs-12 text-center">
                           %sla = (100 - ss['pct_ok'])
                           %font='ok' if sla >= 95.0 else 'warning' if sla >= 90.0 else 'critical'
                           <a href="/all?search=type:service" class="sla_services_{{font}}">
                              <div>{{sla}}%</div>

                              <i class="fa fa-4x fa-server font-{{font}}"></i>
                              <p>{{_('Services SLA')}}</p>
                           </a>
                        </div>
                        %known_problems=ss['nb_acknowledged']+ss['nb_in_downtime']+ss['nb_problems']
                        %pct_known_problems=round(100.0 * known_problems / ss['nb_elts'], 2) if ss['nb_elts'] else -1
                        <div class="col-xs-12 text-center">
                            <a role="button" href="{{ webui.get_url('Services table') }}?search=ls_state:down" class="sla_services_problems">
                                <span class="services-count" data-count="{{ known_problems }}" data-state="problem">{{ pct_known_problems }}%</span>
                                <br/>
                                <span class="services-state">{{_('Known problems')}}</span>
                            </a>
                        </div>
                     </div>

                     %for state in 'ok', 'warning', 'critical', 'unknown':
                     <div class="col-xs-4 col-sm-4 text-center">
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
                                 <i class="fa fa-check fa-fw" style="{{'display:none;' if not graphs['pie_graph_hosts']['legend'] else ''}}"></i>{{_('Display graph legend?')}}
                              </a>
                           </li>
                           <li>
                              <a href="#" data-action="toggle-title" data-graph="pie_graph_hosts">
                                 <i class="fa fa-check fa-fw" style="{{'display:none;' if not graphs['pie_graph_hosts']['title'] else ''}}"></i>{{_('Display graph title?')}}
                              </a>
                           </li>
                           <li class="divider"></li>
                           %for state in graphs['pie_graph_hosts']['states']:
                           <li>
                              <a href="#" data-action="toggle-state" data-graph="pie_graph_hosts" data-state="{{state}}" class="{{'active' if graphs['pie_graph_hosts']['display_states'][state] else ''}}">
                                 <i class="fa fa-check fa-fw" style="{{'display:none;' if not graphs['pie_graph_hosts']['display_states'][state] else ''}}"></i>{{_('Display state %s?') % state}}
                              </a>
                           </li>
                           %end
                        </ul>
                     </div>
                     <a href="#p_panel_pie_graph_hosts" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_pie_graph_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
               </div>
               <div id="p_panel_pie_graph_hosts" class="panel-collapse collapse {{'in' if not panels['panel_pie_graph_hosts']['collapsed'] else ''}}">
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
                                 <i class="fa fa-check fa-fw" style="{{'display:none;' if not graphs['pie_graph_services']['legend'] else ''}}"></i>{{_('Display graph legend?')}}
                              </a>
                           </li>
                           <li>
                              <a href="#" data-action="toggle-title" data-graph="pie_graph_services">
                                 <i class="fa fa-check fa-fw" style="{{'display:none;' if not graphs['pie_graph_services']['title'] else ''}}"></i>{{_('Display graph title?')}}
                              </a>
                           </li>
                           <li class="divider"></li>
                           %for state in graphs['pie_graph_services']['states']:
                           <li>
                              <a href="#" data-action="toggle-state" data-graph="pie_graph_services" data-state="{{state}}" class="{{'active' if graphs['pie_graph_services']['display_states'][state] else ''}}">
                                 <i class="fa fa-check fa-fw" style="{{'display:none;' if not graphs['pie_graph_services']['display_states'][state] else ''}}"></i>{{_('Display state %s?') % state}}
                              </a>
                           </li>
                           %end
                        </ul>
                     </div>
                     <a href="#p_panel_pie_graph_services" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_pie_graph_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
               </div>
               <div id="p_panel_pie_graph_services" class="panel-collapse collapse {{'in' if not panels['panel_pie_graph_services']['collapsed'] else ''}}">
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
                     <a href="#p_panel_line_graph_hosts" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_line_graph_hosts']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                 </div>
               </div>
               <div id="p_panel_line_graph_hosts" class="panel-collapse collapse {{'in' if not panels['panel_line_graph_hosts']['collapsed'] else ''}}">
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
                     <a href="#p_panel_line_graph_services" data-toggle="collapse" type="button" class="btn btn-xs btn-raised"><i class="fa {{'fa-minus-square' if not panels['panel_line_graph_services']['collapsed'] else 'fa-plus-square'}} fa-fw"></i></a>
                  </div>
               </div>
               <div id="p_panel_line_graph_services" class="panel-collapse collapse {{'in' if not panels['panel_line_graph_services']['collapsed'] else ''}}">
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

<script>
   // Panels collapse state
   $('.panel').on('hidden.bs.collapse', function () {
      panels[$(this).parent().attr('id')].collapsed = true;
      $(this).find('.fa-minus-square').removeClass('fa-minus-square').addClass('fa-plus-square');
      save_user_preference('panels', JSON.stringify(panels), function() {
         // Page refresh required
         refresh_required = true;
      });
   });
   $('.panel').on('shown.bs.collapse', function () {
      panels[$(this).parent().attr('id')].collapsed = false;
      $(this).find('.fa-plus-square').removeClass('fa-plus-square').addClass('fa-minus-square');
      save_user_preference('panels', JSON.stringify(panels), function() {
         // Page refresh required
         refresh_required = true;
      });
   });

   // Graphs options
   $('[data-action="toggle-title"]').on('click', function () {
      if (dashboard_logs) console.debug('Toggle title', graphs[$(this).data('graph')]);
      graphs[$(this).data('graph')].title = ! graphs[$(this).data('graph')].title;
      if (graphs[$(this).data('graph')].title) {
         $(this).children('i').show();
      } else {
         $(this).children('i').hide();
      }
      save_user_preference('graphs', JSON.stringify(graphs), function() {
         // Page refresh required
         refresh_required = true;
      });
   });
   $('[data-action="toggle-legend"]').on('click', function () {
      if (dashboard_logs) console.debug('Toggle legend', graphs[$(this).data('graph')]);
      graphs[$(this).data('graph')].legend = ! graphs[$(this).data('graph')].legend;
      if (graphs[$(this).data('graph')].legend) {
         $(this).children('i').show();
      } else {
         $(this).children('i').hide();
      }
      save_user_preference('graphs', JSON.stringify(graphs), function() {
         // Page refresh required
         refresh_required = true;
      });
   });
   $('[data-action="toggle-state"]').on('click', function () {
      if (dashboard_logs) console.debug('Toggle state', graphs[$(this).data('graph')]);
      graphs[$(this).data('graph')]['display_states'][$(this).data('state')] = ! graphs[$(this).data('graph')]['display_states'][$(this).data('state')];
      if (graphs[$(this).data('graph')]['display_states'][$(this).data('state')]) {
         $(this).children('i').show();
      } else {
         $(this).children('i').hide();
      }
      save_user_preference('graphs', JSON.stringify(graphs), function() {
         // Page refresh required
         refresh_required = true;
      });
   });
</script>

</div>