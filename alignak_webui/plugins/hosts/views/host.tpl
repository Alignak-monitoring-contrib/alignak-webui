%setdefault('debug', False)
%setdefault('host', None)
%setdefault('services', None)
%setdefault('parents', None)
%setdefault('children', None)
%setdefault('history', None)
%setdefault('events', None)
%setdefault('timeline_pagination', None)
%setdefault('types', None)
%setdefault('selected_types', None)
%setdefault('title', _('Host view'))

%rebase("layout", title=title, js=[], css=[], page="/host/{{host.id}}")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_service import Service

<!-- Host view -->
<div id="host-{{host.id}}">
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
               <a data-toggle="collapse" href="#collapse_{{host.id}}_services"><i class="fa fa-bug"></i> Host services as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}_services" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
            %for service in services:
            <div class="panel panel-default">
               <div class="panel-heading">
                  <h4 class="panel-title">
                     <a data-toggle="collapse" href="#collapse{{service.id}}_services"><i class="fa fa-bug"></i> Service: {{service.name}}</a>
                  </h4>
               </div>
               <div id="collapse{{service.id}}_services" class="panel-collapse collapse" style="height: 200px;">
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
      %if children:
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}_children"><i class="fa fa-bug"></i> Host children as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}_children" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
            %for child in children:
            <div class="panel panel-default">
               <div class="panel-heading">
                  <h4 class="panel-title">
                     <a data-toggle="collapse" href="#collapse{{child.id}}_children"><i class="fa fa-bug"></i> Child: {{child.name}}</a>
                  </h4>
               </div>
               <div id="collapse{{child.id}}_children" class="panel-collapse collapse" style="height: 200px;">
                  <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                     %for k,v in sorted(child.__dict__.items()):
                        <dt>{{k}}</dt>
                        <dd>{{v}}</dd>
                     %end
                  </dl>
               </div>
            </div>
            %end
         </div>
      </div>
      %end
      %if parents:
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{host.id}}_parents"><i class="fa fa-bug"></i> Host parents as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{host.id}}_parents" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
            %for parent in parents:
            <div class="panel panel-default">
               <div class="panel-heading">
                  <h4 class="panel-title">
                     <a data-toggle="collapse" href="#collapse{{parent.id}}_parents"><i class="fa fa-bug"></i> Parent: {{parent.name}}</a>
                  </h4>
               </div>
               <div id="collapse{{parent.id}}_parents" class="panel-collapse collapse" style="height: 200px;">
                  <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                     %for k,v in sorted(parent.__dict__.items()):
                        <dt>{{k}}</dt>
                        <dd>{{v}}</dd>
                     %end
                  </dl>
               </div>
            </div>
            %end
         </div>
      </div>
      %end
   </div>
   %end

   <!-- First row : tags and actions ... -->
   %groups = datamgr.get_hostgroups({'where': {'hosts': host.id}})
   %tags = host.tags
   %templates = host._templates
   %if host.action_url or tags or groups:
   <div>
      %if groups:
      <div class="host-groups btn-group pull-right">
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <span class="fa fa-sitemap"></span>&nbsp;{{_('Groups')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
         %for group in groups:
            <li>
            <a href="/hostgroup/{{group.id}}">{{group.alias}}</a>
            </li>
         %end
         </ul>
      </div>
      <div class="pull-right">&nbsp;&nbsp;</div>
      %end
      %if host.action_url != '':
      <div class="host-action-url btn-group pull-right">
         %action_urls = host.action_url.split('|')
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-external-link"></i> {{_('Actions') if len(action_urls) == 1 else _('Actions')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
            %for action_url in Helper.get_element_actions_url(host, default_title="Url", default_icon="globe", popover=True):
            <li>{{! action_url}}</li>
            %end
         </ul>
      </div>
      <div class="pull-right">&nbsp;&nbsp;</div>
      %end
      %if tags:
      <div class="host-tags btn-group pull-right">
         %if len(tags) > 2:
            <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
               <i class="fa fa-tag"></i>&nbsp;{{_('Tags')}}&nbsp;<span class="caret"></span>
            </button>
            <ul class="dropdown-menu pull-right">
               %for tag in sorted(tags):
               <li><button class="btn btn-default btn-xs"><span class="fa fa-tag"></span> {{tag}}</button></li>
               %end
            </ul>
         %else:
            %for tag in sorted(tags):
               <a href="{{ webui.get_url('Hosts table') }}?search=tags:{{tag}}">
                  <span class="fa fa-tag"></span> {{tag}}
               </a>
            %end
         %end
      </div>
      %end
      %#todo: edit the host templates!
      %if False:
      <div class="host-templates btn-group pull-right">
         %if len(templates) > 2:
            <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
               <i class="fa fa-edit"></i>&nbsp;{{_('Templates')}}&nbsp;<span class="caret"></span>
            </button>
            <ul class="dropdown-menu pull-right">
               %for template in sorted(templates):
               <li><button class="btn btn-default btn-xs"><span class="fa fa-tag"></span> {{template.name}}</button></li>
               %end
            </ul>
         %else:
            %for template in sorted(templates):
               <a href="{{ webui.get_url('Hosts table') }}?search=tags:{{tag}}">
                  <span class="fa edit"></span> {{template.name}}
               </a>
            %end
         %end
      </div>
      %end
   </div>
   %end

   <!-- Second row : host/service overview ... -->
   <div class="panel panel-default">
      <div class="panel-heading">
         <h4 class="panel-title">
            <a class="collapsed" role="button" data-toggle="collapse" href="#collapseHostOverview" aria-expanded="false" aria-controls="collapseHostOverview">
               <span class="caret"></span>
               {{_('Overview for %s') % host.name}} {{! Helper.get_html_business_impact(host.business_impact, icon=True, text=False)}}
            </a>
         </h4>
      </div>

      <div id="collapseHostOverview" class="panel-body panel-collapse collapse">
         %if host.customs and ('_DETAILLEDESC' in host.customs or '_IMPACT' in host.customs or '_FIXACTIONS' in host.customs):
         <div class="panel panel-default">
            <div class="panel-body">
               <dl class="col-sm-12 dl-horizontal">
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
         </div>
         %end

         <div class="row">
            <dl class="col-sm-6 col-md-4">
               <dt>{{_('Alias:')}}</dt>
               <dd>{{host.alias}}</dd>

               %if host.notes:
               <dt>{{_('Notes:')}}</dt>
               <dd>
               %for note_url in Helper.get_element_notes_url(host, default_title="Note", default_icon="tag", popover=True):
                  {{! note_url}}
               %end
               </dd>
               %end

               <dt>{{_('Address:')}}</dt>
               <dd>{{host.address}}</dd>

               <dt>{{_('Importance:')}}</dt>
               <dd>{{!Helper.get_html_business_impact(host.business_impact, icon=True, text=True)}}</dd>
            </dl>

            <dl class="col-sm-6 col-md-4">
               <dt>{{_('Parents:')}}</dt>
               %if parents:
               %for parent in parents:
               %for parent_host in parent.hosts:
               <dd>
               {{! parent_host.html_state_link}}
               </dd>
               %end
               %end
               %else:
               <dd>{{_('Do not depend upon any host')}}</dd>
               %end

               <dt>{{_('Children:')}}</dt>
               %if children:
               %for child in children:
               %for dependent_host in child.dependent_hosts:
               <dd>
               {{! dependent_host.html_state_link}}
               </dd>
               %end
               %end
               %else:
               <dd>{{_('No host depends upon me')}}</dd>
               %end
            </dl>
         </div>
      </div>
   </div>

   <!-- Third row : business impact alerting ... -->
   %if current_user.is_power():
      %if host.is_problem and host.business_impact > 2 and not host.acknowledged:
      <div class="panel panel-default">
         <div class="panel-body">
            <i class="fa fa-2x fa-spin fa-gear"></i>
            <span class="alert alert-danger">
               {{_('This element has an important impact on your business, you may acknowledge it or try to fix it.')}}
            </span>
         </div>
      </div>
      %end
   %end

   %if services:
   %synthesis = datamgr.get_services_synthesis(services)
   <!-- Fourth row : services synthesis ... -->
   <div class="panel panel-default">
     <div class="panel-body">
       <table class="table table-invisible table-condensed" style="margin-bottom: 0px;"><tbody><tr>
          <td><a role="menuitem" href="/services/table?search=host:{{host.id}}">
               <strong>{{synthesis['nb_elts']}} services:&nbsp;</strong>
          </a></td>

          %for state in 'ok', 'warning', 'critical', 'unknown', 'acknowledged', 'in_downtime':
          <td>
            %label = "%s <em>(%s%%)</em>" % (synthesis["nb_" + state], synthesis["pct_" + state])
            {{! Service({'ls_state': state}).get_html_state(text=label, title=label, disabled=(not synthesis["nb_" + state]))}}
          </td>
          %end
       </tr></tbody></table>
     </div>
   </div>
   %end

   <!-- Fifth row : host widgets ... -->
   <div>
      <ul class="nav nav-tabs">
         %first=True
         %for widget in webui.get_widgets_for('host'):
            <li {{'class="active"' if first else ''}}>
               <a href="#host_{{widget['id']}}"
                  role="tab" data-toggle="tab" aria-controls="{{widget['id']}}"
                  title="{{! widget['description']}}">
                  <span class="fa fa-{{widget['icon']}}"></span>
                  <span class="hidden-sm hidden-xs">{{widget['name']}}</span>
               </a>
            </li>
            %first=False
         %end
      </ul>

      <div class="tab-content">
         %first=True
         %for widget in webui.get_widgets_for('host'):
            <div id="host_{{widget['id']}}" class="tab-pane fade {{'active in' if first else ''}}" role="tabpanel"></div>
            %first=False
         %end
      </div>
   </div>
</div>

<script>
   $(document).ready(function() {
      bootstrap_tab_bookmark();

      // Activate the popover for the notes and actions urls
      $('[data-toggle="popover urls"]').popover({
         placement: 'bottom',
         animation: true,
         template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
         content: function() {
             return $('#hosts-states-popover-content').html();
         }
      });

      // Tabs management
      $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
         // Changed tab
         var $url = window.location.href.replace(window.location.search,'');
         $url = $url.split('#');
         if (($url[1] == undefined) || ($url[1] == '')) {
            $url = 'host_view';
         } else {
            $url = $url[1];
         }
         var loading='<div class="alert alert-info text-center"><span class="fa fa-spin fa-spinner"></span>&nbsp;{{_("Fetching data...")}}&nbsp;<span class="fa fa-spin fa-spinner"></span></div>';
         $('#'+$url).html(loading);
         $.ajax({
            url: '/'+$url+'/{{host.id}}'
         })
         .done(function(content, textStatus, jqXHR) {
            $('#'+$url).html(content);
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            console.error('get host tab, error: ', jqXHR, textStatus, errorThrown);
            // raise_message_ko(errorThrown + ': '+ textStatus);
         });
      })

      // If the requested URL does not contain an anchor, show the first page tab...
      var url = window.location.href.replace(window.location.search,'');
      url = url.split('#');
      if ((url[1] == undefined) || (url[1] == '')) {
         $('a[data-toggle="tab"]:first').trigger("shown.bs.tab");
      } else {
         $('a[href="#'+url[1]+'"]').trigger("shown.bs.tab");
      }
   });
</script>