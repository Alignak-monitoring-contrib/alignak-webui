%setdefault('debug', True)

%rebase("layout", title=title, js=[], css=[], page="/host")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Command, Service

<!-- Host view -->
<div id="host">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Host as dictionary</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <dl class="dl-horizontal">
               %for k,v in sorted(host.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
            </ul>
         </div>
      </div>
   </div>
   %end

   <!-- First row : tags and actions ... -->
   %groups = [ {'_id':'1', 'name':'g1', 'level': 1}, {'_id':'2', 'name':'g2', 'level': 2} ]
   %tags = ['t1', 't2']
   %if host.action_url or tags or groups:
   <div>
      %if groups:
      <div class="btn-group pull-right">
         <button class="btn btn-primary btn-xs"><i class="fa fa-sitemap"></i>{{_('Groups')}}</button>
         <button class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
         <ul class="dropdown-menu pull-right">
         %for g in groups:
            <li>
            <a href="/hostgroup/{{g['_id']}}">{{g['level']}} - {{g['name']}}</a>
            </li>
         %end
         </ul>
      </div>
      <div class="pull-right">&nbsp;&nbsp;</div>
      %end
      %if host.action_url != '':
      <div class="btn-group pull-right">
         %action_urls = host.action_url.split('|')
         <button class="btn btn-info btn-xs"><i class="fa fa-external-link"></i> {{'Action' if len(action_urls) == 1 else 'Actions'}}</button>
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown"><span class="caret"></span></button>
         <ul class="dropdown-menu pull-right">
            %for action_url in helper.get_element_actions_url(elt, default_title="Url", default_icon="globe", popover=True):
            <li>{{!action_url}}</li>
            %end
         </ul>
      </div>
      <div class="pull-right">&nbsp;&nbsp;</div>
      %end
      %if tags:
      <div class="btn-group pull-right">
         %for tag in sorted(tags):
            <a>
               <button class="btn btn-default btn-xs"><i class="fa fa-tag"></i> {{tag.lower()}}</button>
            </a>
         %end
      </div>
      %end
   </div>
   %end

   <!-- Second row : host/service overview ... -->
   <div class="panel panel-default">
      <div class="panel-heading" data-toggle="collapse" data-parent="#hostOverview" href="#collapseHostOverview">
         <h4 class="panel-title"><span class="caret"></span>
            {{_('Overview for %s') % host.get_name()}} {{! Helper.get_html_business_impact(host.business_impact, icon=True, text=False)}}
         </h4>
      </div>

      <div id="collapseHostOverview" class="panel-body panel-collapse collapse">
         %if host.customs:
         <div class="row">
            <dl class="dl-horizontal">
               %if '_DETAILLEDESC' in host.customs:
               <dt>{{_('Description:')}}</dt>
               <dd>{{host.customs['_DETAILLEDESC']}}</dd>
               %end
               %if '_IMPACT' in host.customs:
               <dt>{{_('Impact:')}}</dt>
               <dd>{{host.customs['_IMPACT']}}</dd>
               %end
               %if '_FIXACTIONS' in host.customs:
               <dt>{{_('Fix actions:')}}</dt>
               <dd>{{host.customs['_FIXACTIONS']}}</dd>
               %end
            </dl>
         </div>
         %end

         <div class="row">
            <dl class="col-sm-6 col-md-4 dl-horizontal">
               <dt>{{_('Alias:')}}</dt>
               <dd>{{host.alias}}</dd>

               <dt>{{_('Address:')}}</dt>
               <dd>{{host.address}}</dd>

               <dt>{{_('Importance:')}}</dt>
               <dd>{{!Helper.get_html_business_impact(host.business_impact, icon=True, text=True)}}</dd>
            </dl>

            <dl class="col-sm-6 col-md-4 dl-horizontal">
               <dt>{{_('Depends upon:')}}</dt>
               %if hasattr(host, 'parent_dependencies'):
               <dd>
               %parents=['<a href="/host/'+parent.host_name+'" class="link">'+parent.display_name+'</a>' for parent in sorted(host.parent_dependencies,key=lambda x:x.display_name)]
               {{!','.join(parents)}}
               </dd>
               %else:
               <dd>{{_('Depends upon nothing')}}</d>
               %end

               <dt>{{_('Parents:')}}</dt>
               %if hasattr(host, 'parents'):
               <dd>
               %parents=['<a href="/host/'+parent.host_name+'" class="link">'+parent.display_name+'</a>' for parent in sorted(host.parents,key=lambda x:x.display_name)]
               {{!','.join(parents)}}
               </dd>
               %else:
               <dd>{{_('No parents')}}</dd>
               %end

               <dt>{{_('Depends upon me:')}}</dt>
               %if hasattr(host, 'child_dependencies'):
               <dd>
               %children=['<a href="/host/'+child.host_name+'" class="link">'+child.display_name+'</a>' for child in sorted(host.child_dependencies,key=lambda x:x.display_name) if child.__class__.my_type=='host']
               {{!','.join(children)}}
               </dd>
               %else:
               <dd>{{_('Nothing depends upon me')}}</dd>
               %end

               <dt>{{_('Children:')}}</dt>
               %if hasattr(host, 'childs'):
               <dd>
               %children=['<a href="/host/'+child.host_name+'" class="link">'+child.display_name+'</a>' for child in sorted(host.childs,key=lambda x:x.display_name)]
               {{!','.join(children)}}
               </dd>
               %else:
               <dd>{{_('No children')}}</dd>
               %end
            </dl>

            <dl class="col-sm-6 col-md-4 dl-horizontal">
               <dt>{{_('Member of:')}}</dt>
               %if hasattr(host, 'hostgroups'):
               <dd>
               %for hg in host.hostgroups:
               <a href="/hosts-group/{{hg.get_name()}}" class="link">{{hg.alias if hg.alias else hg.get_name()}}</a>
               %end
               </dd>
               %else:
               <dd>{{_('Not member of any group')}}</dd>
               %end

               <dt>{{_('Notes:')}}</dt>
               <dd>
               %for note_url in Helper.get_element_notes_url(host, default_title="Note", default_icon="tag", popover=True):
                  <button class="btn btn-default btn-xs">{{! note_url}}</button>
               %end
               </dd>
            </dl>
         </div>
      </div>
   </div>

   <!-- Third row : business impact alerting ... -->
   %if current_user.can_submit_commands():
      %if host.is_problem and host.business_impact > 2 and not host.problem_has_been_acknowledged:
      <div class="panel panel-default">
         <div class="panel-heading" style="padding-bottom: -10">
            <div class="aroundpulse pull-left" style="padding: 8px;">
               <span class="big-pulse pulse"></span>
               <i class="fa fa-3x fa-spin fa-gear"></i>
            </div>
            <div style="margin-left: 60px;">
            %disabled_ack = '' if host.is_problem and not host.problem_has_been_acknowledged else 'disabled'
            %disabled_fix = '' if host.is_problem and host.event_handler_enabled and host.event_handler else 'disabled'
            <p class="alert alert-danger" style="margin-bottom:0">
               {{_('This element has an important impact on your business, you may acknowledge it or try to fix it.')}}
            </p>
            </div>
         </div>
      </div>
      %end
   %end

   %services = datamgr.get_services(search={'where': '{"host_name":host.get_name()}'})
   %synthesis = datamgr.get_services_synthesis(services)
   <!-- Fourth row : services synthesis ... -->
   <div class="panel panel-default">
     <div class="panel-body">
       <table class="table table-invisible table-condensed">
         <tbody>
           <tr>
             <td>
               <a role="menuitem" href="/all?search=type:service {{host.get_name()}}">
                  <b>{{synthesis['nb_elts']}} services:&nbsp;</b>
               </a>
             </td>

             %for state in 'ok', 'warning', 'critical', 'unknown', 'ack', 'downtime':
             <td>
               %if synthesis['nb_' + state]>0:
               <a role="menuitem" href="/all?search=type:service is:{{state}} {{host.get_name()}}">
               %end
                 %label = "%s <i>(%s%%)</i>" % (synthesis["nb_" + state], synthesis["pct_" + state])
                 {{! Service({'status':state}).get_html_state(label=label, disabled=(not synthesis["nb_" + state]))}}

               %if synthesis['nb_' + state]>0:
               </a>
               %end
             </td>
             %end
           </tr>
         </tbody>
       </table>
     </div>
   </div>

   <!-- Fifth row : host information -->
   <div>
      <!-- Detail info box start -->
      <ul class="nav nav-tabs">
         %_go_active = 'active'
         %for cvname in host.custom_views:
            %cvconf = 'default'
            %if '/' in cvname:
               %cvconf = cvname.split('/')[1]
               %cvname = cvname.split('/')[0]
            %end
            <li class="{{_go_active}} cv_pane" data-name="{{cvname}}" data-conf="{{cvconf}}" data-element='{{host.get_full_name()}}' id='tab-cv-{{cvname}}-{{cvconf}}'><a href="#cv{{cvname}}_{{cvconf}}" data-toggle="tab">{{cvname.capitalize()}}{{'/'+cvconf.capitalize() if cvconf!='default' else ''}}</a></li>
            %_go_active = ''
         %end

         <li class="{{_go_active}}">
            <a href="#information" data-toggle="tab">{{_('Information')}}</a>
         </li>
         <li>
            <a href="#impacts" data-toggle="tab">{{_('Services')}}</a>
         </li>
         %if current_user.is_administrator() and host.customs:
         <li>
            <a href="#configuration" data-toggle="tab">{{_('Configuration')}}</a>
         </li>
         %end
         <li>
            <a href="#comments" data-toggle="tab">{{_('Comments')}}</a>
         </li>
         <li>
            <a href="#downtimes" data-toggle="tab">{{_('Downtimes')}}</a>
         </li>
         <!--<li class="timeline_pane"><a href="#timeline" data-toggle="tab">Timeline</a></li>-->
         <li>
            <a href="#metrics" data-toggle="tab">{{_('Metrics')}}</a>
         </li>
         <li>
            <a href="#graphs" data-toggle="tab">{{_('Graphs')}}</a>
         </li>
         <li>
            <a href="#depgraph" data-toggle="tab">{{_('Impact graph')}}</a>
         </li>
         <li>
            <a href="#history" data-toggle="tab">{{_('History')}}</a>
         </li>
         <li>
            <a href="#availability" data-toggle="tab">{{_('Availability')}}</a>
         </li>
         <li>
            <a href="#helpdesk" data-toggle="tab">{{_('Helpdesk')}}</a>
         </li>
      </ul>

      <div class="tab-content">
         <!-- Tab custom views -->
         %_go_active = 'active'
         %_go_fadein = 'in'
         %cvs = []
         %[cvs.append(item) for item in host.custom_views if item not in cvs]
         %for cvname in cvs:
            %cvconf = 'default'
            %if '/' in cvname:
               %cvconf = cvname.split('/')[1]
               %cvname = cvname.split('/')[0]
            %end
            <div class="tab-pane fade {{_go_active}} {{_go_fadein}}" data-name="{{cvname}}" data-conf="{{cvconf}}" data-element="{{host.get_full_name()}}" id="cv{{cvname}}_{{cvconf}}">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <!--<span class="alert alert-error">Sorry, I cannot load the {{cvname}}/{{cvconf}} view!</span>-->
                  </div>
               </div>
            </div>
            %_go_active = ''
            %_go_fadein = ''
         %end
         <!-- Tab custom views end -->

            <!-- Tab Information start-->
            <div class="tab-pane fade {{_go_active}} {{_go_fadein}}" id="information">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div class="col-lg-6">
                        <table class="table table-condensed">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">Status:</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              <tr>
                                 <td><strong>{{_('Status:')}}</strong></td>
                                 <td>
                                    {{! host.get_html_state()}}
                                 </td>
                              </tr>
                              <tr>
                                 <td><strong>{{_('Since:')}}</strong></td>
                                 <td class="popover-dismiss"
                                       data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                       data-title="{{host.get_name()}}{{_('}} last state change date')}}"
                                       data-content="{{! Helper.print_duration(host.last_state_change, duration_only=True, x_elts=0)}}"
                                       >
                                    {{! Helper.print_duration(host.last_state_change, duration_only=True, x_elts=0)}}
                                 </td>
                              </tr>
                           </tbody>
                        </table>

                        <table class="table table-condensed table-nowrap">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">{{_('Last check:')}}</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              <tr>
                                 <td><strong>{{_('Last Check:')}}</strong></td>
                                 <td><span class="popover-dismiss" data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Last check was at {{time.asctime(time.localtime(host.last_chk))}}">was {{Helper.print_duration(host.last_chk)}}</span></td>
                              </tr>
                              <tr>
                                 <td><strong>Output:</strong></td>
                                 <td class="popover-dismiss popover-large"
                                       data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                       data-title="{{host.get_full_name()}} check output"
                                       data-content=" {{host.output}}{{'<br/>'+host.long_output.replace('\n', '<br/>') if host.long_output else ''}}"
                                       >
                                  {{!helper.strip_html_output(host.output) if app.allow_html_output else host.output}}
                                 </td>
                              </tr>
                              <tr>
                                 <td><strong>Performance data:</strong></td>
                                 <td class="popover-dismiss popover-large ellipsis"
                                       data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                       data-title="{{host.get_full_name()}} performance data"
                                       data-content=" {{host.perf_data if host.perf_data else '(none)'}}"
                                       >
                                  {{host.perf_data if host.perf_data else '(none)'}}
                                 </td>
                              </tr>
                              <tr>
                                 <td><strong>Check latency / duration:</strong></td>
                                 <td>
                                    {{'%.2f' % host.latency}} / {{'%.2f' % host.execution_time}} seconds
                                 </td>
                              </tr>

                              <tr>
                                 <td><strong>Last State Change:</strong></td>
                                 <td><span class="popover-dismiss" data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Last state change at {{time.asctime(time.localtime(host.last_state_change))}}">{{helper.print_duration(host.last_state_change)}}</span></td>
                              </tr>
                              <tr>
                                 <td><strong>Current Attempt:</strong></td>
                                 <td>{{host.attempt}}/{{host.max_check_attempts}} ({{host.state_type}} state)</td>
                              </tr>
                              <tr>
                                 <td><strong>Next Active Check:</strong></td>
                                 <td><span class="popover-dismiss" data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="Next active check at {{time.asctime(time.localtime(host.next_chk))}}">{{helper.print_duration(host.next_chk)}}</span></td>
                              </tr>
                           </tbody>
                        </table>

                        <table class="table table-condensed">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">Checks configuration:</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              %if hasattr(elt, "check_period") and hasattr(host.check_period, "get_name"):
                              <tr>
                                 <td><strong>Check period:</strong></td>
                                 %tp=app.datamgr.get_timeperiod(host.check_period.get_name())
                                 <td name="check_period" class="popover-dismiss"
                                       data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                                       data-title='{{tp.alias if hasattr(tp, "alias") else tp.timeperiod_name}}'
                                       data-content='{{!helper.get_timeperiod_html(tp)}}'
                                       >
                                 {{! helper.get_on_off(host.check_period.is_time_valid(now), 'Is element check period currently active?')}}
                                 <a href="/timeperiods">{{host.check_period.alias}}</a>
                                 </td>
                              </tr>
                              %else:
                              <tr>
                                 <td><strong>No defined check period!</strong></td>
                                 <td></td>
                              </tr>
                              %end
                              %if host.maintenance_period is not None:
                              <tr>
                                 <td><strong>Maintenance period:</strong></td>
                                 <td name="maintenance_period" class="popover-dismiss"
                                       data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                                       data-title='{{tp.alias if hasattr(tp, "alias") else tp.timeperiod_name}}'
                                       data-content='{{!helper.get_timeperiod_html(tp)}}'
                                       >
                                 {{! helper.get_on_off(host.maintenance_period.is_time_valid(now), 'Is element maintenance period currently active?')}}
                                 <a href="/timeperiods">{{host.maintenance_period.alias}}</a>
                                 </td>
                              </tr>
                              %end
                              <tr>
                                 <td><strong>Check command:</strong></td>
                                 <td>
                                    <a href="/commands#{{host.get_check_command()}}">{{host.get_check_command()}}</a>
                                 </td>
                                 <td>
                                 </td>
                              </tr>
                              <tr>
                                 <td><strong>Active checks:</strong></td>
                                 <td>
                                    <input type="checkbox" {{'checked' if host.active_checks_enabled else ''}}
                                          class="switch" data-size="mini" data-on-color="success" data-off-color="danger"
                                          data-type="action" action="toggle-active-checks"
                                          data-element="{{helper.get_uri_name(elt)}}" data-value="{{host.active_checks_enabled}}"
                                          >
                                 </td>
                              </tr>
                              %if (host.active_checks_enabled):
                              <tr>
                                 <td><strong>Check interval:</strong></td>
                                 <td>{{host.check_interval}} seconds</td>
                              </tr>
                              <tr>
                                 <td><strong>Retry interval:</strong></td>
                                 <td>{{host.retry_interval}} seconds</td>
                              </tr>
                              <tr>
                                 <td><strong>Max check attempts:</strong></td>
                                 <td>{{host.max_check_attempts}}</td>
                              </tr>
                              %end
                              <tr>
                                 <td><strong>Passive checks:</strong></td>
                                 <td>
                                    <input type="checkbox" {{'checked' if host.passive_checks_enabled else ''}}
                                          class="switch" data-size="mini" data-on-color="success" data-off-color="danger"
                                          data-type="action" action="toggle-passive-checks"
                                          data-element="{{helper.get_uri_name(elt)}}" data-value="{{host.passive_checks_enabled}}"
                                          >
                                 </td>
                              </tr>
                              %if (host.passive_checks_enabled):
                              <tr>
                                 <td><strong>Freshness check:</strong></td>
                                 <td>{{! helper.get_on_off(host.check_freshness, 'Is freshness check enabled?')}}</td>
                              </tr>
                              %if (host.check_freshness):
                              <tr>
                                 <td><strong>Freshness threshold:</strong></td>
                                 <td>{{host.freshness_threshold}} seconds</td>
                              </tr>
                              %end
                              %end
                              <tr>
                                 <td><strong>Process performance data:</strong></td>
                                 <td>{{! helper.get_on_off(host.process_perf_data, 'Is perfdata process enabled?')}}</td>
                              </tr>
                           </tbody>
                        </table>
                        <table class="table table-condensed">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">Event handler:</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              <tr>
                                 <td><strong>Event handler enabled:</strong></td>
                                 <td>
                                    <input type="checkbox" {{'checked' if host.event_handler_enabled else ''}}
                                          class="switch" data-size="mini" data-on-color="success" data-off-color="danger"
                                          data-type="action" action="toggle-event-handler"
                                          data-element="{{helper.get_uri_name(elt)}}" data-value="{{host.event_handler_enabled}}"
                                          >
                                 </td>
                              </tr>
                              %if host.event_handler_enabled and host.event_handler:
                              <tr>
                                 <td><strong>Event handler:</strong></td>
                                 <td>
                                    <a href="/commands#{{host.event_handler.get_name()}}">{{ host.event_handler.get_name() }}</a>
                                 </td>
                              </tr>
                              %end
                              %if host.event_handler_enabled and not host.event_handler:
                              <tr>
                                 <td></td>
                                 <td><strong>No event handler defined!</strong></td>
                              </tr>
                              %end
                           </tbody>
                        </table>
                     </div>
                     <div class="col-lg-6">
                        <table class="table table-condensed">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">Flapping detection:</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              <tr>
                                 <td><strong>Flapping detection:</strong></td>
                                 <td>
                                    <input type="checkbox" {{'checked' if host.flap_detection_enabled else ''}}
                                          class="switch" data-size="mini" data-on-color="success" data-off-color="danger"
                                          data-type="action" action="toggle-flap-detection"
                                          data-element="{{helper.get_uri_name(elt)}}" data-value="{{host.flap_detection_enabled}}"
                                          >
                                 </td>
                              </tr>
                              %if host.flap_detection_enabled:
                              <tr>
                                 <td><strong>Options:</strong></td>
                                 <td>{{', '.join(host.flap_detection_options)}}</td>
                              </tr>
                              <tr>
                                 <td><strong>Low threshold:</strong></td>
                                 <td>{{host.low_flap_threshold}}</td>
                              </tr>
                              <tr>
                                 <td><strong>High threshold:</strong></td>
                                 <td>{{host.high_flap_threshold}}</td>
                              </tr>
                              %end
                           </tbody>
                        </table>

                        %if host.stalking_options and host.stalking_options[0]:
                        <table class="table table-condensed">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">Stalking options:</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              <tr>
                                 <td><strong>Options:</strong></td>
                                 <td>{{', '.join(host.stalking_options)}}</td>
                              </tr>
                           </tbody>
                        </table>
                        %end

                        <table class="table table-condensed">
                           <colgroup>
                              <col style="width: 40%" />
                              <col style="width: 60%" />
                           </colgroup>
                           <thead>
                              <tr>
                                 <th colspan="2">Notifications:</th>
                              </tr>
                           </thead>
                           <tbody style="font-size:x-small;">
                              <tr>
                                 <td><strong>Notifications:</strong></td>
                                 <td>
                                    <input type="checkbox" {{'checked' if host.notifications_enabled else ''}}
                                          class="switch" data-size="mini" data-on-color="success" data-off-color="danger"
                                          data-type="action" action="toggle-notifications"
                                          data-element="{{helper.get_uri_name(elt)}}" data-value="{{host.notifications_enabled}}"
                                          >
                                 </td>
                              </tr>
                              %if host.notifications_enabled and host.notification_period:
                              <tr>
                                 <td><strong>Notification period:</strong></td>
                                 %tp=app.datamgr.get_timeperiod(host.notification_period.get_name())
                                 <td name="notification_period" class="popover-dismiss" data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                                       data-title='{{tp.alias if hasattr(tp, "alias") else tp.timeperiod_name}}'
                                       data-content='{{!helper.get_timeperiod_html(tp)}}'>
                                    {{! helper.get_on_off(host.notification_period.is_time_valid(now), 'Is element notification period currently active?')}}
                                    <a href="/timeperiods">{{host.notification_period.alias}}</a>
                                 </td>
                              </tr>
                              <tr>
                                 %if elt_type=='host':
                                    %message = {}
                                    %# [d,u,r,f,s,n]
                                    %message['d'] = 'Down'
                                    %message['u'] = 'Unreachable'
                                    %message['r'] = 'Recovery'
                                    %message['f'] = 'Flapping'
                                    %message['s'] = 'Downtimes'
                                    %message['n'] = 'None'
                                 %else:
                                    %message = {}
                                    %# [w,u,c,r,f,s,n]
                                    %message['w'] = 'Warning'
                                    %message['u'] = 'Unknown'
                                    %message['c'] = 'Critical'
                                    %message['r'] = 'Recovery'
                                    %message['f'] = 'Flapping'
                                    %message['s'] = 'Downtimes'
                                    %message['n'] = 'None'
                                 %end
                                 <td><strong>Notification options:</strong></td>
                                 <td>
                                 %for m in message:
                                    {{! helper.get_on_off(m in host.notification_options, '', message[m]+'&nbsp;')}}
                                 %end
                                 </td>
                              </tr>
                              <tr>
                                 <td><strong>Last notification:</strong></td>
                                 <td>{{helper.print_date(host.last_notification)}} (notification {{host.current_notification_number}})</td>
                              </tr>
                              <tr>
                                 <td><strong>Notification interval:</strong></td>
                                 <td>{{host.notification_interval}} mn</td>
                              </tr>
                              <tr>
                                 <td><strong>Contacts:</strong></td>
                                 <td>
                                   %contacts = [c for c in host.contacts if app.datamgr.get_contact(name=c.contact_name, user=user)]
                                   %for c in contacts:
                                   <a href="/contact/{{c.contact_name}}">{{ c.alias if c.alias and c.alias != 'none' else c.contact_name }}</a>,
                                   %end
                                 </td>
                              </tr>
                              <tr>
                                 <td><strong>Contacts groups:</strong></td>
                                 <td>
                                   %contact_groups = [c for c in host.contact_groups if app.datamgr.get_contactgroup(c, user)]
                                   {{!', '.join(contact_groups)}}
                                 </td>
                              </tr>
                              %end
                           </tbody>
                        </table>
                     </div>
                  </div>
               </div>
            </div>
            <!-- Tab Information end -->

             <!-- Tab Impacts start -->
            <div class="tab-pane fade" id="impacts">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div class="{{'col-lg-6'}} if elt_type =='host' else 'col-lg-12'">
                        %displayed_services=False
                        <!-- Show our father dependencies if we got some -->
                        %if host.parent_dependencies:
                        <h4>Root cause:</h4>
                        {{!helper.print_business_rules(app.datamgr.get_business_parents(user, elt), source_problems=host.source_problems)}}
                        %end

                        <!-- If we are an host and not a problem, show our services -->
                        %if elt_type=='host' and not host.is_problem:
                        %if host.services:
                        %displayed_services=True
                        <h4>My services:</h4>
                        <div class="services-tree">
                          {{!helper.print_aggregation_tree(helper.get_host_service_aggregation_tree(elt, app), helper.get_html_id(elt), expanded=False, max_sons=3)}}
                        </div>
                        %elif not host.parent_dependencies:
                        <h4>No services!</h4>
                        %end
                        %end #of the only host part

                        <!-- If we are a root problem and got real impacts, show them! -->
                        %if host.is_problem and host.impacts:
                        <h4>My impacts:</h4>
                        <div class='host-services'>
                           %s = ""
                           <ul>
                           %for svc in helper.get_impacts_sorted(elt):
                              %s += "<li>"
                              %s += helper.get_fa_icon_state(svc)
                              %s += helper.get_link(svc, short=True)
                              %s += "(" + Helper.get_html_business_impact(host.business_impact) + ")"
                              %s += """ is <span class="font-%s"><strong>%s</strong></span>""" % (svc.state.lower(), svc.state)
                              %s += " since %s" % helper.print_duration(svc.last_state_change, just_duration=True, x_elts=2)
                              %s += "</li>"
                           %end
                           {{!s}}
                           </ul>
                        </div>
                        %# end of the 'is problem' if
                        %end
                     </div>
                     %if elt_type=='host':
                     <div class="col-lg-6">
                        %if not displayed_services:
                        <!-- Show our own services  -->
                        <h4>My services:</h4>
                        <div>
                          {{!helper.print_aggregation_tree(helper.get_host_service_aggregation_tree(elt, app), helper.get_html_id(elt))}}
                        </div>
                        %end
                     </div>
                     %end
                  </div>
               </div>
            </div>
            <!-- Tab Impacts end -->

           <!-- Tab Configuration start -->
            %if current_user.is_administrator() and host.customs:
            <div class="tab-pane fade" id="configuration">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <table class="table table-condensed table-bordered">
                        <colgroup>
                           %if app.can_action():
                           <col style="width: 30%" />
                           <col style="width: 60%" />
                           <col style="width: 10%" />
                           %else:
                           <col style="width: 40%" />
                           <col style="width: 60%" />
                           %end
                        </colgroup>
                        <thead>
                           <tr>
                              <th colspan="3">Customs:</th>
                           </tr>
                        </thead>
                        <tbody style="font-size:x-small;">
                        %for var in sorted(host.customs):
                           <tr>
                              <td>{{var}}</td>
                              <td>{{host.customs[var]}}</td>
                              %# ************
                              %# Remove the Change button because Shinken does not take care of the external command!
                              %# Issue #224
                              %# ************
                              %if app.can_action() and False:
                              <td>
                                 <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                                       data-type="action" action="change-variable"
                                       data-toggle="tooltip" data-placement="bottom" title="Change a custom variable for this {{elt_type}}"
                                       data-element="{{helper.get_uri_name(elt)}}" data-variable="{{var}}" data-value="{{host.customs[var]}}"
                                       >
                                    <i class="fa fa-gears"></i> Change
                                 </button>
                              </td>
                              %end
                           </tr>
                        %end
                        </tbody>
                     </table>
                  </div>
               </div>
            </div>
            %end
            <!-- Tab Configuration end -->

            <!-- Tab Comments start -->
            <div class="tab-pane fade" id="comments">
               <div class="panel panel-default">
                  <div class="panel-body">
                     %if host.comments:
                     <table class="table table-condensed table-hover">
                        <thead>
                           <tr>
                              <th>Author</th>
                              <th>Comment</th>
                              <th>Date</th>
                              <th></th>
                           </tr>
                        </thead>
                        <tbody>
                        %for c in sorted(host.comments, key=lambda x: x.entry_time, reverse=True):
                           <tr>
                              <td>{{c.author}}</td>
                              <td>{{c.comment}}</td>
                              <td>{{helper.print_date(c.entry_time)}}</td>
                              <td>
                                 <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                                       data-type="action" action="delete-comment"
                                       data-toggle="tooltip" data-placement="bottom" title="Delete this comment"
                                       data-element="{{helper.get_uri_name(elt)}}" data-comment="{{c.id}}"
                                       >
                                    <i class="fa fa-trash-o"></i>
                                 </button>
                              </td>
                           </tr>
                        %end
                        </tbody>
                     </table>

                     %else:
                     <div class="alert alert-info">
                        <p class="font-blue">No comments available.</p>
                     </div>
                     %end

                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                           data-type="action" action="add-comment"
                           data-toggle="tooltip" data-placement="bottom" title="Add a comment for this {{elt_type}}"
                           data-element="{{helper.get_uri_name(elt)}}"
                           >
                        <i class="fa fa-plus"></i> Add a comment
                     </button>
                     %if host.comments:
                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                           data-type="action" action="delete-comments"
                           data-toggle="tooltip" data-placement="bottom" title="Delete all the comments of this {{elt_type}}"
                           data-element="{{helper.get_uri_name(elt)}}"
                           >
                        <i class="fa fa-minus"></i> Delete all comments
                     </button>
                     %end
                     %if elt_type=='host' and host.services:
                         <br/><br/>
                         <h4>Current host services comments:</h4>
                         <table class="table table-condensed table-hover">
                            <thead>
                               <tr>
                                  <th>Service</th>
                                  <th>Author</th>
                                  <th>Comment</th>
                                  <th>Date</th>
                                  <th></th>
                               </tr>
                            </thead>
                            <tbody>
                            %for s in host.services:
                            %for c in sorted(s.comments, key=lambda x: x.entry_time, reverse=True):
                               <tr>
                                  <td>{{s.get_name()}}</td>
                                  <td>{{c.author}}</td>
                                  <td>{{c.comment}}</td>
                                  <td>{{helper.print_date(c.entry_time)}}</td>
                                  <td>
                                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                                           data-type="action" action="delete-comment"
                                           data-toggle="tooltip" data-placement="bottom" title="Delete this comment"
                                           data-element="{{helper.get_uri_name(elt)}}" data-comment="{{c.id}}"
                                           >
                                        <i class="fa fa-trash-o"></i>
                                     </button>
                                  </td>
                               </tr>
                            %end
                            %end
                            </tbody>
                         </table>
                     %end
                  </div>

               </div>
            </div>
            <!-- Tab Comments end -->

            <!-- Tab Downtimes start -->
            <div class="tab-pane fade" id="downtimes">
               <div class="panel panel-default">
                  <div class="panel-body">
                     %if host.downtimes:
                     <table class="table table-condensed table-hover">
                        <thead>
                           <tr>
                              <th>Author</th>
                              <th>Reason</th>
                              <th>Period</th>
                              <th></th>
                           </tr>
                        </thead>
                        <tbody>
                        %for dt in sorted(host.downtimes, key=lambda dt: dt.entry_time, reverse=True):
                           <tr>
                              <td>{{dt.author}}</td>
                              <td>{{dt.comment}}</td>
                              <td>{{helper.print_date(dt.start_time)}} - {{helper.print_date(dt.end_time)}}</td>
                              <td>
                                 <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                                       data-type="action" action="delete-downtime"
                                       data-toggle="tooltip" data-placement="bottom" title="Delete the downtime '{{dt.id}}' for this {{elt_type}}"
                                       data-element="{{helper.get_uri_name(elt)}}" data-downtime="{{dt.id}}"
                                       >
                                    <i class="fa fa-trash-o"></i>
                                 </button>
                              </td>
                           </tr>
                        %end
                        </tbody>
                     </table>
                     %else:
                     <div class="alert alert-info">
                        <p class="font-blue">No downtimes available.</p>
                     </div>
                     %end

                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                           data-type="action" action="schedule-downtime"
                           data-toggle="tooltip" data-placement="bottom" title="Schedule a downtime for this {{elt_type}}"
                           data-element="{{helper.get_uri_name(elt)}}"
                           >
                        <i class="fa fa-plus"></i> Schedule a downtime
                     </button>
                     %if host.downtimes:
                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                           data-type="action" action="delete-downtimes"
                           data-toggle="tooltip" data-placement="bottom" title="Delete all the downtimes of this {{elt_type}}"
                           data-element="{{helper.get_uri_name(elt)}}"
                           >
                        <i class="fa fa-minus"></i> Delete all downtimes
                     </button>
                     %end

                     %if elt_type=='host' and host.services:
                         <br/><br/>
                         <h4>Current host services downtimes:</h4>
                         <table class="table table-condensed table-hover">
                            <thead>
                               <tr>
                                  <th>Service</th>
                                  <th>Author</th>
                                  <th>Reason</th>
                                  <th>Period</th>
                                  <th></th>
                               </tr>
                            </thead>
                            <tbody>
                            %for s in host.services:
                            %for dt in sorted(s.downtimes, key=lambda dt: dt.entry_time, reverse=True):
                               <tr>
                                  <td>{{s.get_name()}}</td>
                                  <td>{{dt.author}}</td>
                                  <td>{{dt.comment}}</td>
                                  <td>{{helper.print_date(dt.start_time)}} - {{helper.print_date(dt.end_time)}}</td>
                                  <td>
                                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                                           data-type="action" action="delete-downtime"
                                           data-toggle="tooltip" data-placement="bottom" title="Delete this downtime"
                                           data-element="{{helper.get_uri_name(s)}}" data-downtime="{{dt.id}}"
                                           >
                                        <i class="fa fa-trash-o"></i>
                                     </button>
                                  </td>
                               </tr>
                            %end
                            %end
                            </tbody>
                         </table>
                     %end
                  </div>
               </div>
            </div>
            <!-- Tab Downtimes end -->

            <!-- Tab Timeline start -->
            <!--
            <div class="tab-pane fade" id="timeline">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div id="inner_timeline" data-element='{{host.get_full_name()}}'>
                        <span class="alert alert-error">Sorry, I cannot load the timeline graph!</span>
                     </div>
                  </div>
               </div>
            </div>
            -->
            <!-- Tab Timeline end -->

            <!-- Tab Metrics start -->
            %from shinken.misc.perfdata import PerfDatas
            <div class="tab-pane fade" id="metrics">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <table class="table table-condensed">
                        <thead>
                           <tr>
                              %if elt_type=='host':
                              <th>Service</th>
                              %end
                              <th>Metric</th>
                              <th>Value</th>
                              <th>Warning</th>
                              <th>Critical</th>
                              <th>Min</th>
                              <th>Max</th>
                              <th>UOM</th>
                              <th></th>
                           </tr>
                        </thead>
                        <tbody style="font-size:x-small;">
                        %# Host check metrics ...
                        %if elt_type=='host' or elt_type=='service':
                           %host_line = True
                           %perfdatas = PerfDatas(host.perf_data)
                           %if perfdatas:
                           %for metric in sorted(perfdatas, key=lambda metric: metric.name):
                           %if metric.name:
                           <tr>
                              %if elt_type=='host':
                              <td><strong>{{'Host check' if host_line else ''}}</strong></td>
                              %host_line = False
                              %end
                              <td><strong>{{metric.name}}</strong></td>
                              <td>{{metric.value}}</td>
                              <td>{{metric.warning if metric.warning!=None else ''}}</td>
                              <td>{{metric.critical if metric.critical!=None else ''}}</td>
                              <td>{{metric.min if metric.min!=None else ''}}</td>
                              <td>{{metric.max if metric.max!=None else ''}}</td>
                              <td>{{metric.uom if metric.uom else ''}}</td>

                              %if app.graphs_module.is_available():
                              <td>
                                 %graphs = app.graphs_module.get_graph_uris(elt, duration=12*3600)
                                 %for graph in graphs:
                                    %if re.findall('\\b'+metric.name+'\\b', graph['img_src']):
                                       <a role="button" tabindex="0"
                                          data-toggle="popover" title="{{ host.get_full_name() }}"
                                          data-html="true"
                                          data-content="<img src='{{ graph['img_src'] }}' width='600px' height='200px'>"
                                          data-trigger="hover" data-placement="left">{{!helper.get_perfometer(elt, metric.name)}}</a>
                                    %end
                                 %end
                              </td>
                              %else:
                              <td>
                                 <a role="button" tabindex="0" >{{!helper.get_perfometer(elt, metric.name)}}</a>
                              </td>
                              %end
                           </tr>
                           %end
                           %end
                           %end
                        %end
                        %# Host services metrics ...
                        %if elt_type=='host' and host.services:
                        %for s in host.services:
                           %service_line = True
                           %perfdatas = PerfDatas(s.perf_data)
                           %if perfdatas:
                           %for metric in sorted(perfdatas, key=lambda metric: metric.name):
                           %if metric.name and metric.value:
                           <tr>
                              <td>{{!helper.get_link(s, short=True) if service_line else ''}}</td>
                              %service_line = False
                              <td><strong>{{metric.name}}</strong></td>
                              <td>{{metric.value}}</td>
                              <td>{{metric.warning if metric.warning!=None else ''}}</td>
                              <td>{{metric.critical if metric.critical!=None else ''}}</td>
                              <td>{{metric.min if metric.min!=None else ''}}</td>
                              <td>{{metric.max if metric.max!=None else ''}}</td>
                              <td>{{metric.uom if metric.uom else ''}}</td>

                              %if app.graphs_module.is_available():
                              <td>
                                 %graphs = app.graphs_module.get_graph_uris(s, duration=12*3600)
                                 %for graph in graphs:
                                    %if re.findall('\\b'+metric.name+'\\b', graph['img_src']):
                                       <a role="button" tabindex="0"
                                          data-toggle="popover" title="{{ s.get_full_name() }}"
                                          data-html="true"
                                          data-content="<img src='{{ graph['img_src'] }}' width='600px' height='200px'>"
                                          data-trigger="hover" data-placement="left">{{!helper.get_perfometer(s, metric.name)}}</a>
                                    %end
                                 %end
                              </td>
                              %else:
                              <td>
                                 <a role="button" tabindex="0" >{{!helper.get_perfometer(s, metric.name)}}</a>
                              </td>
                              %end
                           </tr>
                           %end
                           %end
                           %end
                        %end
                        %end
                        </tbody>
                     </table>
                  </div>
               </div>
            </div>
            <!-- Tab Metrics end -->

            <!-- Tab Graph start -->
            %if app.graphs_module.is_available():
            <script>
            var html_graphes = [];
            var current_graph = '';
            var graphstart={{graphstart}};
            var graphend={{graphend}};
            </script>
            <div class="tab-pane fade" id="graphs">
               <div class="panel panel-default">
                  <div class="panel-body">
                     %# Set source as '' or module ui-graphite will try to fetch templates from default 'detail'
                     %uris = app.graphs_module.get_graph_uris(elt, graphstart, graphend)
                     %if uris:
                     <div class='well'>
                        <!-- 5 standard time ranges to display ...  -->
                        <ul id="graph_periods" class="nav nav-pills nav-justified">
                          <li><a data-type="graph" data-period="4h" > 4 hours</a></li>
                          <li><a data-type="graph" data-period="1d" > 1 day</a></li>
                          <li><a data-type="graph" data-period="1w" > 1 week</a></li>
                          <li><a data-type="graph" data-period="1m" > 1 month</a></li>
                          <li><a data-type="graph" data-period="1y" > 1 year</a></li>
                        </ul>
                     </div>

                     <div class='well'>
                        <div id='real_graphs'>
                        </div>
                     </div>

                     <script>
                     $('a[href="#graphs"]').on('shown.bs.tab', function (e) {
                        %uris = dict()
                        %uris['4h'] = app.graphs_module.get_graph_uris(elt, duration=     4*3600)
                        %uris['1d'] = app.graphs_module.get_graph_uris(elt, duration=    24*3600)
                        %uris['1w'] = app.graphs_module.get_graph_uris(elt, duration=  7*24*3600)
                        %uris['1m'] = app.graphs_module.get_graph_uris(elt, duration= 31*24*3600)
                        %uris['1y'] = app.graphs_module.get_graph_uris(elt, duration=365*24*3600)

                        // let's create the html content for each time range
                        var element='/{{elt_type}}/{{host.get_full_name()}}';
                        %for period in ['4h', '1d', '1w', '1m', '1y']:

                        html_graphes['{{period}}'] = '<p>';
                        %for g in uris[period]:
                        html_graphes['{{period}}'] +=  '<img src="{{g['img_src']}}" class="jcropelt"/> <p></p>';
                        %end
                        html_graphes['{{period}}'] += '</p>';

                        %end

                        // Set first graph
                        current_graph = '4h';
                        $('a[data-type="graph"][data-period="'+current_graph+'"]').trigger('click');
                     });
                     </script>
                     %else:
                     <div class="alert alert-info">
                         <div class="font-blue"><strong>No graphs available for this {{elt_type}}!</strong></div>
                     </div>
                     %end
                  </div>
               </div>
            </div>
            %end
            <!-- Tab Graph end -->

            <!-- Tab Dependency graph Start -->
            <div class="tab-pane fade" id="depgraph">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div class="btn-group btn-group-sm pull-right">
                        <button data-type="action" action="fullscreen-request" data-element="inner_depgraph" class="btn btn-primary"><i class="fa fa-desktop"></i> Fullscreen</button>
                     </div>
                     <div id="inner_depgraph" data-element='{{host.get_full_name()}}'>
                     </div>
                  </div>
               </div>
            </div>
            <!-- Tab Dependency graph End -->

            <!-- Tab History start -->
            %if app.logs_module.is_available():
            <div class="tab-pane fade" id="history">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div id="inner_history" data-element='{{host.get_full_name()}}'>
                     </div>
                  </div>
               </div>
            </div>
            %end
            <!-- Tab History end -->

            <!-- Tab Availability start -->
            %if app.logs_module.is_available():
            <div class="tab-pane fade" id="availability">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div id="inner_availability" data-element='{{host.get_full_name()}}'>
                     </div>
                  </div>
               </div>
            </div>
            %end
            <!-- Tab Availability end -->

            <!-- Tab Helpdesk start -->
            %if app.helpdesk_module.is_available():
            <div class="tab-pane fade" id="helpdesk">
               <div class="panel panel-default">
                  <div class="panel-body">
                     <div id="inner_helpdesk" data-element='{{host.get_full_name()}}'>
                     </div>

                     <button class="{{'disabled' if not app.can_action() else ''}} btn btn-primary btn-sm"
                           data-type="action" action="create-ticket"
                           data-toggle="tooltip" data-placement="bottom" title="Create a ticket for this {{elt_type}}"
                           data-element="{{helper.get_uri_name(elt)}}"
                           >
                        <i class="fa fa-medkit"></i> Create a ticket
                     </button>
                  </div>
               </div>
            </div>
            %end
            <!-- Tab Helpdesk end -->
         </div>
      <!-- Detail info box end -->
   </div>

   <div class="panel panel-default">
      <div class="panel-body">
         <h3>
            {{! host.get_html_state()}}
         </h3>

         <h3>
            <small>{{host.name}}</small>
         </h3>

         <h3>
            <small>{{host.alias}}</small>
         </h3>

         <h3>
            <small>{{host.display_name}}</small>
         </h3>

         <h3>
            <small>{{host.address}}</small>
         </h3>

         <h3>
            %command=Command(host.check_command)
            <small>{{! command.get_html_state(label=command.get_name())}}</small>
         </h3>

         <h3>
            <small>{{! Helper.get_on_off(host.active_checks_enabled)}}</small>
         </h3>

         <h3>
            <small>{{! Helper.get_on_off(host.passive_checks_enabled)}}</small>
         </h3>

         <h3>
            <small>{{host.business_impact}}</small>
         </h3>
      </div>
   </div>
 </div>
