%setdefault('debug', True)

%rebase("layout", title=title, js=[], css=[], page="/host")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item import Command, Service

<!-- Host view -->
<div id="host">
   %host_id = host.get_id()
   %host_name = host.get_name()
   %services = datamgr.get_services(search={'where': {'host_name':host_id}})
   %livestate = datamgr.get_livestate(search={'where': {'name':'%s' % host_name}})
   %livestate = livestate[0]

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
                     <a data-toggle="collapse" href="#collapse{{service.get_id()}}"><i class="fa fa-bug"></i> Service: {{service.get_name()}}</a>
                  </h4>
               </div>
               <div id="collapse{{service.get_id()}}" class="panel-collapse collapse" style="height: 200px;">
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
      <ul class="nav nav-tabs">
         %_go_active = 'active'
         %for cvname in host.custom_views:
            %cvconf = 'default'
            %if '/' in cvname:
               %cvconf = cvname.split('/')[1]
               %cvname = cvname.split('/')[0]
            %end
            <li class="{{_go_active}} cv_pane" data-name="{{cvname}}" data-conf="{{cvconf}}" data-element='{{host.get_name()}}' id='tab-cv-{{cvname}}-{{cvconf}}'><a href="#cv{{cvname}}_{{cvconf}}" data-toggle="tab">{{cvname.capitalize()}}{{'/'+cvconf.capitalize() if cvconf!='default' else ''}}</a></li>
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
            <a href="#comments" data-toggle="tab">{{_('Comments')}}</a>
         </li>
         <li>
            <a href="#downtimes" data-toggle="tab">{{_('Downtimes')}}</a>
         </li>
         <li>
            <a href="#timeline" data-toggle="tab">Timeline</a>
         </li>
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
            <div class="tab-pane fade {{_go_active}} {{_go_fadein}}" data-name="{{cvname}}" data-conf="{{cvconf}}" data-element="{{host.get_name()}}" id="cv{{cvname}}_{{cvconf}}">
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
                        <tbody style="font-size:x-small;">
                           <tr>
                              <td><strong>{{_('Status:')}}</strong></td>
                              <td>
                                 {{! livestate.get_html_state(text=True)}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Since:')}}</strong></td>
                              <td class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{host.get_name()}}{{_('}} last state change date')}}"
                                    data-content="{{! Helper.print_duration(livestate.last_state_changed, duration_only=True, x_elts=0)}}"
                                    >
                                 {{! Helper.print_duration(livestate.last_state_changed, duration_only=True, x_elts=0)}}
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
                              <td>
                                 <span class="popover-dismiss" data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom" data-content="{{_('Last check was at %s') % Helper.print_duration(livestate.last_check)}}">was {{Helper.print_duration(livestate.last_check)}}</span></td>
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
                              <td><strong>{{_('Check latency / duration:')}}</strong></td>
                              <td>
                                 {{_('%.2f / %.2f seconds') % (9999, 9999999) }}
                              </td>
                           </tr>

                           <tr>
                              <td><strong>{{_('Last State Change:')}}</strong></td>
                              <td class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{host.get_name()}}{{_('}} last state change date')}}"
                                    data-content="{{! Helper.print_duration(host.last_state_change, duration_only=True, x_elts=0)}}"
                                    >
                                 {{! Helper.print_duration(host.last_state_change, duration_only=True, x_elts=0)}}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Current Attempt:')}}</strong></td>
                              <td>
                                 {{_('%s / %s %s state') % (host.attempt, livestate.max_attempts, livestate.state_type) }}
                              </td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Next Active Check:')}}</strong></td>
                              <td class="popover-dismiss"
                                    data-html="true" data-toggle="popover" data-trigger="hover" data-placement="bottom"
                                    data-title="{{host.get_name()}}{{_('}} last state change date')}}"
                                    data-content="{{! Helper.print_duration(host.next_check, duration_only=True, x_elts=0)}}"
                                    >
                                 {{! Helper.print_duration(livestate.next_check, duration_only=True, x_elts=0)}}
                              </td>
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
                                 %tp = host.check_period
                                 %if not isinstance(tp, basestring):
                                 {{! '<a href="command/%s">%s</a>' % (tp.get_id(), tp.get_html_state(label=command.get_name()))}}
                                 %end
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
                                 %tp = host.maintenance_period
                                 {{! '<a href="command/%s">%s</a>' % (tp.get_id(), tp.get_html_state(label=command.get_name()))}}
                              </td>
                           </tr>
                           %end

                           <tr>
                              <td><strong>{{_('Check command:')}}</strong></td>
                              <td>
                                 %command = host.check_command
                                 {{! '<a href="command/%s">%s</a>' % (command.get_id(), command.get_html_state(label=command.get_name()))}}
                              </td>
                              <td>
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
                              <td>{{host.check_interval}} seconds</td>
                           </tr>
                           <tr>
                              <td><strong>{{_('Retry interval:')}}</strong></td>
                              <td>{{host.retry_interval}} seconds</td>
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
                           <tr>
                              <td><strong>{{_('Process performance data:')}}</strong></td>
                              <td>
                                 {{! Helper.get_on_off(host.process_perf_data)}}
                              </td>
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
                                 <a href="/commands#{{host.event_handler.get_name()}}">{{ host.event_handler.name() }}</a>
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
                        %if current_user.can_submit_commands():
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
                           <th colspan="3">{{_('Customs:')}}</th>
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
                           %if current_user.can_submit_commands() and False:
                           <td>
                              <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                                    data-type="action" action="change-variable"
                                    data-toggle="tooltip" data-placement="bottom" title="{{_('Change a custom variable for this host')}}"
                                    data-element="{{host_id}}" data-variable="{{var}}" data-value="{{host.customs[var]}}"
                                    >
                                 <i class="fa fa-gears"></i>{{_('Change variable')}}
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
                           <th>{{_('Author')}}</th>
                           <th>{{_('Comment')}}</th>
                           <th>{{_('Date')}}</th>
                           <th></th>
                        </tr>
                     </thead>
                     <tbody>
                     %for c in sorted(host.comments, key=lambda x: x.entry_time, reverse=True):
                        <tr>
                           <td>{{c.author}}</td>
                           <td>{{c.comment}}</td>
                           <td>{{Helper.print_date(c.entry_time)}}</td>
                           <td>
                              <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                                    data-type="action" action="delete-comment"
                                    data-toggle="tooltip" data-placement="bottom" title="{{_('Delete this comment')}}"
                                    data-element="{{host_id}}" data-comment="{{c.id}}"
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
                     <p class="font-blue">{{_('No comments available.')}}</p>
                  </div>
                  %end

                  <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                        data-type="action" action="add-comment"
                        data-toggle="tooltip" data-placement="bottom" title="{{_('Add a comment for this host')}}"
                        data-element="host_id"
                        >
                     <i class="fa fa-plus"></i>{{_('Add a comment')}}
                  </button>
                  %if host.comments:
                  <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                        data-type="action" action="delete-comments"
                        data-toggle="tooltip" data-placement="bottom" title="{{_('Delete all the comments for this host')}}"
                        data-element="{{host_id}}"
                        >
                     <i class="fa fa-minus"></i>{{_('Delete all comments')}}
                  </button>
                  %end
                  %if host.services:
                      <br/><br/>
                      <h4>{{_('Current host services comments:')}}</h4>
                      <table class="table table-condensed table-hover">
                         <thead>
                            <tr>
                               <th>{{_('Service')}}</th>
                               <th>{{_('Author')}}</th>
                               <th>{{_('Comment')}}</th>
                               <th>{{_('Date')}}</th>
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
                               <td>{{Helper.print_date(c.entry_time)}}</td>
                               <td>
                                  <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                                        data-type="action" action="delete-comment"
                                        data-toggle="tooltip" data-placement="bottom" title="Delete this comment"
                                        data-element="{{host_id}}" data-comment="{{c.id}}"
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
                           <th>{{_('Author')}}</th>
                           <th>{{_('Reason')}}</th>
                           <th>{{_('Period')}}</th>
                           <th></th>
                        </tr>
                     </thead>
                     <tbody>
                     %for dt in sorted(host.downtimes, key=lambda dt: dt.entry_time, reverse=True):
                        <tr>
                           <td>{{dt.author}}</td>
                           <td>{{dt.comment}}</td>
                           <td>{{Helper.print_date(dt.start_time)}} - {{Helper.print_date(dt.end_time)}}</td>
                           <td>
                              <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                                    data-type="action" action="delete-downtime"
                                    data-toggle="tooltip" data-placement="bottom" title="{{_('Delete the downtime [%s] for this host') % dt.id}}"
                                    data-element="{{host_id}}" data-downtime="{{dt.id}}"
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
                     <p class="font-blue">{{_('No downtimes available.')}}</p>
                  </div>
                  %end

                  <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                        data-type="action" action="schedule-downtime"
                        data-toggle="tooltip" data-placement="bottom" title="{{_('Schedule a downtime for this host')}}"
                        data-element="{{host_id}}"
                        >
                     <i class="fa fa-plus"></i> {{_('Schedule a downtime')}}
                  </button>
                  %if host.downtimes:
                  <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                        data-type="action" action="delete-downtimes"
                        data-toggle="tooltip" data-placement="bottom" title="{{_('Delete all the downtimes of this host')}}"
                        data-element="{{host_id}}"
                        >
                     <i class="fa fa-minus"></i> {{_('Delete all downtimes')}}
                  </button>
                  %end

                  %if host.services:
                      <br/><br/>
                      <h4>{{_('Current host services downtimes:')}}</h4>
                      <table class="table table-condensed table-hover">
                         <thead>
                            <tr>
                               <th>{{_('Service')}}</th>
                               <th>{{_('Author')}}</th>
                               <th>{{_('Reason')}}</th>
                               <th>{{_('Period')}}</th>
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
                               <td>{{Helper.print_date(dt.start_time)}} - {{Helper.print_date(dt.end_time)}}</td>
                               <td>
                                  <button class="{{'disabled' if not current_user.can_submit_commands() else ''}} btn btn-primary btn-sm"
                                        data-type="action" action="delete-downtime"
                                        data-toggle="tooltip" data-placement="bottom" title="{{_('Delete the downtime [%s] for this service') % dt.id}}"
                                        data-element="{{Helper.get_uri_name(s)}}" data-downtime="{{dt.id}}"
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

         <!-- Tab Metrics start -->
         <div class="tab-pane fade" id="metrics">
            <div class="panel panel-default">
               <div class="panel-body">
                  %if host.perfdatas:
                  <table class="table table-condensed">
                     <thead>
                        <tr>
                           <th>{{_('Service')}}</th>
                           <th>{{_('Metric')}}</th>
                           <th>{{_('Value')}}</th>
                           <th>{{_('Warning')}}</th>
                           <th>{{_('Critical')}}</th>
                           <th>{{_('Min')}}</th>
                           <th>{{_('Max')}}</th>
                           <th>{{_('UOM')}}</th>
                           <th></th>
                        </tr>
                     </thead>
                     <tbody style="font-size:x-small;">
                        %host_line = True
                        %for metric in sorted(host.perfdatas, key=lambda metric: metric.name):
                        %if metric.name:
                        <tr>
                           <td><strong>{{'Host check' if host_line else ''}}</strong></td>
                           %host_line = False
                           <td><strong>{{metric.name}}</strong></td>
                           <td>{{metric.value}}</td>
                           <td>{{metric.warning if metric.warning!=None else ''}}</td>
                           <td>{{metric.critical if metric.critical!=None else ''}}</td>
                           <td>{{metric.min if metric.min!=None else ''}}</td>
                           <td>{{metric.max if metric.max!=None else ''}}</td>
                           <td>{{metric.uom if metric.uom else ''}}</td>
                        </tr>
                        %end
                        %end
                     </tbody>
                  </table>
                  %else:
                  <div class="alert alert-info">
                     <p class="font-blue">{{_('No metrics are available.')}}</p>
                  </div>
                  %end
               </div>
            </div>
         </div>
         <!-- Tab Metrics end -->

         <!-- Tab Graph start -->
         <div class="tab-pane fade" id="graphs">
            <div class="panel panel-default">
               <div class="panel-body">
                  %# Set source as '' or module ui-graphite will try to fetch templates from default 'detail'
                  %uris = []
                  %if uris:
                  <div class='well'>
                     <!-- 5 standard time ranges to display ...  -->
                     <ul id="graph_periods" class="nav nav-pills nav-justified">
                       <li><a data-type="graph" data-period="4h" > {{_('4 hours')}}</a></li>
                       <li><a data-type="graph" data-period="1d" > {{_('1 day')}}</a></li>
                       <li><a data-type="graph" data-period="1w" > {{_('1 week')}}</a></li>
                       <li><a data-type="graph" data-period="1m" > {{_('1 month')}}</a></li>
                       <li><a data-type="graph" data-period="1y" > {{_('1 year')}}</a></li>
                     </ul>
                  </div>

                  <div class='well'>
                     <div id='real_graphs'>
                     </div>
                  </div>

                  <script>
                  $('a[href="#graphs"]').on('shown.bs.tab', function (e) {
                     %uris = dict()
                     %uris['4h'] = ""
                     %uris['1d'] = ""
                     %uris['1w'] = ""
                     %uris['1m'] = ""
                     %uris['1y'] = ""

                     // let's create the html content for each time range
                     var element='/host/{{host.get_name()}}';
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
                  <div id="inner_depgraph" data-element='{{host.get_name()}}'>
                     <div class="alert alert-info">
                        <p class="font-blue">{{_('Sorry, I cannot load the dependencies graph!')}}</p>
                     </div>
                  </div>
               </div>
            </div>
         </div>
         <!-- Tab Dependency graph End -->

         <!-- Tab History start -->
         <div class="tab-pane fade" id="history">
            <div class="panel panel-default">
               <div class="panel-body">
                  <div id="inner_history" data-element='{{host.get_name()}}'>
                     <div class="alert alert-info">
                        <p class="font-blue">{{_('No history is available.')}}</p>
                     </div>
                  </div>
               </div>
            </div>
         </div>
         <!-- Tab History end -->

         <!-- Tab Availability start -->
         <div class="tab-pane fade" id="availability">
            <div class="panel panel-default">
               <div class="panel-body">
                  <div id="inner_availability" data-element='{{host.get_name()}}'>
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
