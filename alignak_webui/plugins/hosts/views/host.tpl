%setdefault('debug', False)
%setdefault('services', None)
%setdefault('livestate', None)
%setdefault('history', None)

%rebase("layout", title=title, js=[], css=[], page="/host")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Command, Service

<!-- Host view -->
<div id="host">
   %host_id = host.id

   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host_id}}"><i class="fa fa-bug"></i> Host as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host_id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(host.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host_id}}_services"><i class="fa fa-bug"></i> Host services as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host_id}}_services" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
            %for service in services:
            <div class="panel panel-default">
               <div class="panel-heading">
                  <h4 class="panel-title">
                     <a data-toggle="collapse" href="#collapse{{service.id}}"><i class="fa fa-bug"></i> Service: {{service.name}}</a>
                  </h4>
               </div>
               <div id="collapse{{service.id}}" class="panel-collapse collapse" style="height: 200px;">
                  <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                     %for k,v in sorted(service.__dict__.items()):
                        <dt>{{k}}</dt>
                        <dd>{{v}}</dd>
                     %end
                  </dl>
               </div>
            </div>
            %end
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
            %for action_url in Helper.get_element_actions_url(host, default_title="Url", default_icon="globe", popover=True):
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
            {{_('Overview for %s') % host.name}} {{! Helper.get_html_business_impact(host.business_impact, icon=True, text=False)}}
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

               <dt>{{_('Notes:')}}</dt>
               <dd>
               %for note_url in Helper.get_element_notes_url(host, default_title="Note", default_icon="tag", popover=True):
                  <button class="btn btn-default btn-xs">{{! note_url}}</button>
               %end
               </dd>
               <dt>{{_('Address:')}}</dt>
               <dd>{{host.address}}</dd>

               <dt>{{_('Importance:')}}</dt>
               <dd>{{!Helper.get_html_business_impact(host.business_impact, icon=True, text=True)}}</dd>
            </dl>

            <dl class="col-sm-6 col-md-4 dl-horizontal">
               <dt>{{_('Depends upon:')}}</dt>
               %if hasattr(host, 'parent_dependencies'):
               <dd>
               %parents=['<a href="/host/'+parent.host+'" class="link">'+parent.display_name+'</a>' for parent in sorted(host.parent_dependencies,key=lambda x:x.display_name)]
               {{!','.join(parents)}}
               </dd>
               %else:
               <dd>{{_('Depends upon nothing')}}</d>
               %end

               <dt>{{_('Parents:')}}</dt>
               %if host.parents:
               <dd>
               %parents=['<a href="/host/'+parent.id+'" class="link">'+parent.alias+'</a>' for parent in host.parents if isinstance(parent, type)]
               {{!','.join(parents)}}
               </dd>
               %else:
               <dd>{{_('No parents')}}</dd>
               %end

               <dt>{{_('Depends upon me:')}}</dt>
               %if hasattr(host, 'child_dependencies'):
               <dd>
               %children=['<a href="/host/'+child.host+'" class="link">'+child.display_name+'</a>' for child in sorted(host.child_dependencies,key=lambda x:x.display_name) if child.__class__.my_type=='host']
               {{!','.join(children)}}
               </dd>
               %else:
               <dd>{{_('Nothing depends upon me')}}</dd>
               %end

               <dt>{{_('Children:')}}</dt>
               %if hasattr(host, 'childs'):
               <dd>
               %children=['<a href="/host/'+child.host+'" class="link">'+child.display_name+'</a>' for child in sorted(host.childs,key=lambda x:x.display_name)]
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
               <a href="/hosts-group/{{hg.name}}" class="link">{{hg.alias if hg.alias else hg.name}}</a>
               %end
               </dd>
               %else:
               <dd>{{_('Not member of any group')}}</dd>
               %end
            </dl>
         </div>
      </div>
   </div>

   <!-- Third row : business impact alerting ... -->
   %if current_user.is_power():
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

   %synthesis = datamgr.get_services_synthesis(services)
   <!-- Fourth row : services synthesis ... -->
   <div class="panel panel-default">
     <div class="panel-body">
       <table class="table table-invisible table-condensed">
         <tbody>
           <tr>
             <td>
               <a role="menuitem" href="/all?search=type:service {{host.name}}">
                  <b>{{synthesis['nb_elts']}} services:&nbsp;</b>
               </a>
             </td>

             %for state in 'ok', 'warning', 'critical', 'unknown', 'ack', 'downtime':
             <td>
               %if synthesis['nb_' + state]>0:
               <a role="menuitem" href="/all?search=type:service is:{{state}} {{host.name}}">
               %end
                 %label = "%s <i>(%s%%)</i>" % (synthesis["nb_" + state], synthesis["pct_" + state])
                 {{! Service({'status':state}).get_html_state(text=label, title=label, disabled=(not synthesis["nb_" + state]))}}

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
      <ul class="nav nav-tabs">
         %_go_active = 'active'
         %for cvname in host.custom_views:
            %cvconf = 'default'
            %if '/' in cvname:
               %cvconf = cvname.split('/')[1]
               %cvname = cvname.split('/')[0]
            %end
            <li class="{{_go_active}} cv_pane" data-name="{{cvname}}" data-conf="{{cvconf}}" data-element='{{host.name}}' id='tab-cv-{{cvname}}-{{cvconf}}'><a href="#cv{{cvname}}_{{cvconf}}" data-toggle="tab">{{cvname.capitalize()}}{{'/'+cvconf.capitalize() if cvconf!='default' else ''}}</a></li>
            %_go_active = ''
         %end

         <li class="{{_go_active}}">
            <a href="#information" data-toggle="tab">{{_('Information')}}</a>
         </li>
         <li>
            <a href="#services" data-toggle="tab">{{_('Services')}}</a>
         </li>
         %if current_user.is_administrator() and host.customs:
         <li>
            <a href="#configuration" data-toggle="tab">{{_('Configuration')}}</a>
         </li>
         %end
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
            <a href="#timeline" data-toggle="tab">{{_('Timeline')}}</a>
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
            <div class="tab-pane fade {{_go_active}} {{_go_fadein}}" data-name="{{cvname}}" data-conf="{{cvconf}}" data-element="{{host.name}}" id="cv{{cvname}}_{{cvconf}}">
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
                              <th colspan="2">{{_('Status:')}}</th>
                           </tr>
                        </thead>
                        %if livestate:
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Status:')}}</strong></td>
                              <td>
                                 %extra=''
                                 %if livestate.acknowledged:
                                 %extra += _(' and acknowledged')
                                 %end
                                 %if livestate.acknowledged:
                                 %extra += _(' and in scheduled downtime')
                                 %end
                                 {{! livestate.get_html_state(extra=extra)}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Since:')}}</strong></td>
                              <td>
                                 {{! Helper.print_duration(livestate.last_state_changed, duration_only=True, x_elts=0)}}
                              </td>
                           </tr>
                        </tbody>
                        %else:
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Status:')}}</strong></td>
                              <td class="alert alert-danger">
                                 {{_('Livestate not found for this host!')}}
                              </td>
                           </tr>
                        </tbody>
                        %end
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
                        %if livestate:
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Last check:')}}</strong></td>
                              <td>
                                 {{_('was ')}}{{Helper.print_duration(livestate.last_check, duration_only=False, x_elts=0)}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Output:')}}</strong></td>
                              <td class="popover-dismiss popover-large"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{_('%s check output') % livestate.output}}"
                                    data-content="{{_('%s<br/>%s') % (livestate.output, livestate.long_output.replace('\n', '<br/>') if livestate.long_output else '')}}"
                                    >
                                 {{! livestate.output}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Performance data:')}}</strong></td>
                              <td class="popover-dismiss popover-large ellipsis"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{_('%s performance data') % livestate.output}}"
                                    data-content=" {{livestate.perf_data if livestate.perf_data else '(none)'}}"
                                    >
                               {{livestate.perf_data if livestate.perf_data else '(none)'}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Check duration (latency):')}}</strong></td>
                              <td>
                                 {{_('%.2f seconds (%.2f)') % (livestate.execution_time, livestate.latency) }}
                              </td>
                           </tr>

                           <tr>
                              <td><strong>{{_('Last state change:')}}</strong></td>
                              <td class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{host.name}}{{_('}} last state change date')}}"
                                    data-content="{{! Helper.print_duration(host.last_state_change, duration_only=True, x_elts=0)}}"
                                    >
                                 {{! Helper.print_duration(host.last_state_change, duration_only=True, x_elts=0)}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Current attempt:')}}</strong></td>
                              <td>
                                 {{_('%s / %s %s state') % (host.attempt, livestate.max_attempts, livestate.state_type) }}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Next active check:')}}</strong></td>
                              <td class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{host.name}}{{_('}} last state change date')}}"
                                    data-content="{{! Helper.print_duration(host.next_check, duration_only=True, x_elts=0)}}"
                                    >
                                 {{! Helper.print_duration(livestate.next_check, duration_only=True, x_elts=0)}}
                              </td>
                           </tr>
                        </tbody>
                        %else:
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Status:')}}</strong></td>
                              <td class="alert alert-danger">
                                 {{_('Livestate not found for this host!')}}
                              </td>
                           </tr>
                        </tbody>
                        %end
                     </table>

                     <table class="table table-condensed">
                        <colgroup>
                           <col style="width: 40%" />
                           <col style="width: 60%" />
                        </colgroup>
                        <thead>
                           <tr>
                              <th colspan="2">{{_('Checks configuration:')}}</th>
                           </tr>
                        </thead>
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Check period:')}}</strong></td>
                              <td name="check_period" class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                                    data-title='{{host.check_period}}'
                                    data-content='{{host.check_period}}'
                                    >
                                 {{! host.check_period.get_html_state_link()}}
                              </td>
                           </tr>

                           %if host.maintenance_period is not None:
                           <tr>
                              <td><strong>{{_('Maintenance period:')}}</strong></td>
                              <td name="maintenance_period" class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="left"
                                    data-title='{{host.maintenance_period}}'
                                    data-content='{{host.maintenance_period}}'
                                    >
                                 {{! host.maintenance_period.get_html_state_link()}}
                              </td>
                           </tr>
                           %end

                           <tr>
                              <td><strong>{{_('Check command:')}}</strong></td>
                              <td>
                                 {{! host.check_command.get_html_state_link()}}
                              </td>
                              <td>
                              </td>
                           </tr>

                           <tr>
                              <td><strong>{{_('Process performance data:')}}</strong></td>
                              <td>
                                 {{! Helper.get_on_off(host.process_perf_data)}}
                              </td>
                           </tr>

                           <tr>
                              <td><strong>{{_('Active checks:')}}</strong></td>
                              <td>
                                 {{! Helper.get_on_off(host.active_checks_enabled)}}
                              </td>
                           </tr>
                           %if (host.active_checks_enabled):
                           <tr>
                              <td><strong>{{_('Check interval:')}}</strong></td>
                              <td>{{host.check_interval}} minutes</td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Retry interval:')}}</strong></td>
                              <td>{{host.retry_interval}} minutes</td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Max check attempts:')}}</strong></td>
                              <td>{{host.max_check_attempts}}</td>
                           </tr>
                           %end
                           <tr>
                              <td><strong>{{_('Passive checks:')}}</strong></td>
                              <td>
                                 {{! Helper.get_on_off(host.passive_checks_enabled)}}
                              </td>
                           </tr>
                           %if (host.passive_checks_enabled):
                           <tr>
                              <td><strong>{{_('Freshness check:')}}</strong></td>
                              <td>
                                 {{! Helper.get_on_off(host.check_freshness)}}
                              </td>
                           </tr>
                           %if (host.check_freshness):
                           <tr>
                              <td><strong>{{_('Freshness threshold:')}}</strong></td>
                              <td>{{host.freshness_threshold}} seconds</td>
                           </tr>
                           %end
                           %end
                        </tbody>
                     </table>

                     <table class="table table-condensed">
                        <colgroup>
                           <col style="width: 40%" />
                           <col style="width: 60%" />
                        </colgroup>
                        <thead>
                           <tr>
                              <th colspan="2">{{_('Event handler:')}}</th>
                           </tr>
                        </thead>
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Event handler enabled:')}}</strong></td>
                              <td>
                                 {{! Helper.get_on_off(host.event_handler_enabled)}}
                              </td>
                           </tr>
                           %if host.event_handler_enabled and host.event_handler:
                           <tr>
                              <td><strong>{{_('Event handler:')}}</strong></td>
                              <td>
                                 <a href="/commands#{{host.event_handler.name}}">{{ host.event_handler.name() }}</a>
                              </td>
                           </tr>
                           %end
                           %if host.event_handler_enabled and not host.event_handler:
                           <tr>
                              <td></td>
                              <td><strong>{{_('No event handler defined.')}}</strong></td>
                           </tr>
                           %end
                        </tbody>
                     </table>
                  </div>
                  <div class="col-lg-6">
                  </div>
               </div>
            </div>
         </div>
         <!-- Tab Information end -->

          <!-- Tab services start -->
         <div class="tab-pane fade" id="services">
            <div class="panel panel-default">
               <div class="panel-body">
                  %include("services.tpl", services=services, layout=False, pagination=Helper.get_pagination_control('service', len(services), 0, len(services)))
               </div>
            </div>
         </div>
         <!-- Tab services end -->

        <!-- Tab Configuration start -->
         %if current_user.is_administrator() and host.customs:
         <div class="tab-pane fade" id="configuration">
            <div class="panel panel-default">
               <div class="panel-body">
                  <table class="table table-condensed table-bordered">
                     <colgroup>
                        <col style="width: 40%" />
                        <col style="width: 60%" />
                     </colgroup>
                     <thead>
                        <tr>
                           <th colspan="3">{{_('Customs:')}}</th>
                        </tr>
                     </thead>
                     <tbody style="font-size:x-small;">
                     %for var in sorted(host.customs):
                        <tr>
                           <td>{{var}}</td>
                           <td>{{host.customs[var]}}</td>
                        </tr>
                     %end
                     </tbody>
                  </table>
               </div>
            </div>
         </div>
         %end
         <!-- Tab Configuration end -->

         <!-- Tab Metrics start -->
         <div class="tab-pane fade" id="metrics">
            %include("_widget.tpl", widget_name='host_metrics_widget', perf_data=livestate.perf_data, options=None, embedded=True, title=None)
         </div>
         <!-- Tab Metrics end -->

         <!-- Tab Graph start -->
         <div class="tab-pane fade" id="graphs">
            <div class="panel panel-default">
               <div class="panel-body">
                  %grafana = False
                  %if grafana:
                  <iframe src="http://94.76.229.155:92/dashboard-solo/db/my-dashboard?panelId=2&from=1466373600000&to=1466414828717" width="100%" height="200" frameborder="0"></iframe>
                  %else:
                  <div class="alert alert-info">
                      <div class="font-blue"><strong>{{_('No graphs are available.')}}</strong></div>
                  </div>
                  %end
               </div>
            </div>
         </div>
         <!-- Tab Graph end -->

         <!-- Tab Dependency graph Start -->
         <div class="tab-pane fade" id="depgraph">
            <div class="panel panel-default">
               <div class="panel-body">
                  <div class="btn-group btn-group-sm pull-right">
                     <button data-type="action" action="fullscreen-request" data-element="inner_depgraph" class="btn btn-primary"><i class="fa fa-desktop"></i> Fullscreen</button>
                  </div>
                  <div id="inner_depgraph" data-element='{{host.name}}'>
                     <div class="alert alert-info">
                        <p class="font-blue">{{_('Sorry, I cannot load the dependencies graph!')}}</p>
                     </div>
                  </div>
               </div>
            </div>
         </div>
         <!-- Tab Dependency graph End -->

         <!-- Tab Timeline start -->
         <div class="tab-pane fade" id="timeline">
            <div class="panel panel-default">
               <div class="panel-body">
                  %include("_timeline.tpl", object_type='host', timeline_host=host, items=history, title=_('Checks, acknowledges, downtimes history for %s') % host.alias, layout=False, timeline_pagination=timeline_pagination)
               </div>
            </div>
         </div>
         <!-- Tab Timeline end -->

         <!-- Tab History start -->
         <div class="tab-pane fade" id="history">
            <div class="panel panel-default">
               <div class="panel-body">
                  %if history:
                     %include("histories.tpl", histories=history, layout=False, pagination=Helper.get_pagination_control('history', len(history), 0, len(history)))
                  %else:
                     <div class="alert alert-info">
                        <p class="font-blue">{{_('No history logs available.')}}</p>
                     </div>
                  %end
               </div>
            </div>
         </div>
         <!-- Tab History end -->

         <!-- Tab Availability start -->
         <div class="tab-pane fade" id="availability">
            <div class="panel panel-default">
               <div class="panel-body">
                  <div id="inner_availability" data-element='{{host.name}}'>
                     <div class="alert alert-info">
                        <p class="font-blue">{{_('No availability information are available.')}}</p>
                     </div>
                  </div>
               </div>
            </div>
         </div>
         <!-- Tab Availability end -->
      </div>
   </div>
 </div>

 <script>
   function bootstrap_tab_bookmark (selector) {
      if (selector == undefined) {
         selector = "";
      }

      var bookmark_switch = function () {
         url = document.location.href.split('#');
         if (url[1] != undefined) {
            $(selector + '[href="#'+url[1]+'"]').tab('show');
         }
      }

      /* Automagically jump on good tab based on anchor */
      $(document).ready(bookmark_switch);
      $(window).bind('hashchange', bookmark_switch);

      var update_location = function (event) {
         document.location.hash = this.getAttribute("href");
      }

      /* Update hash based on tab */
      $(selector + "[data-toggle=pill]").click(update_location);
      $(selector + "[data-toggle=tab]").click(update_location);
   }

   $(function () {
      // Activate the popover for the notes and actions urls
      $('[data-toggle="popover urls"]').popover()

      bootstrap_tab_bookmark();
   })
 </script>