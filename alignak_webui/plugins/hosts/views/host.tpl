%setdefault('debug', False)
%setdefault('services', None)
%setdefault('livestate', None)
%setdefault('history', None)

%rebase("layout", title=title, js=[], css=[], page="/host")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_service import Service

<!-- Host view -->
<div id="host">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}"><i class="fa fa-bug"></i> Host as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}" class="panel-collapse collapse">
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
               <a data-toggle="collapse" href="#collapse_livestate_{{host.id}}"><i class="fa fa-bug"></i> Host livestate as dictionary</a>
            </h4>
         </div>
         <div id="collapse_livestate_{{host.id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(livestate.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}_services"><i class="fa fa-bug"></i> Host services as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}_services" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
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
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}_services_livestate"><i class="fa fa-bug"></i> Host services livestate as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}_services_livestate" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
            %for service in livestate_services:
            <div class="panel panel-default">
               <div class="panel-heading">
                  <h4 class="panel-title">
                     <a data-toggle="collapse" href="#collapse{{service.id}}"><i class="fa fa-bug"></i> Service livestate: {{service.name}}</a>
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
   %groups = datamgr.get_hostgroups({'where': {'hosts': host.id}})
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
      %if host.is_problem and host.business_impact > 2 and not host.acknowledged:
      <div class="panel panel-default">
         <div class="panel-heading" style="padding-bottom: -10">
            <div class="aroundpulse pull-left" style="padding: 8px;">
               <span class="big-pulse pulse"></span>
               <i class="fa fa-3x fa-spin fa-gear"></i>
            </div>
            <div style="margin-left: 60px;">
            %disabled_ack = '' if host.is_problem and not host.acknowledged else 'disabled'
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

             %for state in 'ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime':
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

   <!-- Fifth row : host widgets -->
   <div>
      <ul class="nav nav-tabs">
         <li class="active">
            <a href="#host_view" data-toggle="tab"
               title="{{_('Host synthesis view')}}"
               >
               <span class="fa fa-server"></span>
               {{_('Host view')}}
            </a>
         </li>

         %for widget in webui.widgets['host']:
            <li>
               <a href="#{{widget['id']}}" data-toggle="tab"
                  title="{{widget['description']}}"
                  >
                  <span class="fa fa-{{widget['icon']}}"></span>
                  {{widget['name']}}
               </a>
            </li>
         %end
      </ul>

      <div class="tab-content">
         <div class="tab-pane fade active in" id="host_view">
            %include("_widget.tpl", widget_name='host_custom_host_default', options=None, embedded=True, title=None)
         </div>

         %for widget in webui.widgets['host']:
            <div class="tab-pane fade" id="{{widget['id']}}">
               %include("_widget.tpl", widget_name=widget['template'], options=widget['options'], embedded=True, title=None)
            </div>
         %end
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