%setdefault('debug', False)
%setdefault('host', None)
%setdefault('service', None)
%setdefault('parents', None)
%setdefault('children', None)
%setdefault('history', None)
%setdefault('events', None)
%setdefault('timeline_pagination', None)
%setdefault('types', None)
%setdefault('selected_types', None)
%setdefault('title', "{{_('Service view')")

%rebase("layout", title=title, js=[], css=[], page="/service")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_service import Service

<!-- Service view -->
<div class="service" id="service-{{service.id}}">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{service.id}}"><i class="fa fa-bug"></i> Service as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{service.id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(service.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
      %if children:
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{service.id}}_children"><i class="fa fa-bug"></i> Service children as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{service.id}}_children" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
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
               <a data-toggle="collapse" href="#collapse_{{service.id}}_parents"><i class="fa fa-bug"></i> Service parents as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{service.id}}_parents" class="panel-collapse collapse" style="height: 200px; margin-left:20px;">
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

   <!-- First row : service overview ... -->
   <div class="service-overview panel panel-default">
      %groups = datamgr.get_servicegroups({'where': {'services': service.id}})
      %tags = service.tags
      %templates = service._templates
      %if groups:
      <div class="service-groups btn-group pull-right">
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <span class="fa fa-sitemap"></span>&nbsp;{{_('Groups')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
         %for group in groups:
            <li><a href="/servicegroup/{{group.id}}"><span class="fa fa-tag"></span>&nbsp;{{group.alias}}</a></li>
         %end
         </ul>
      </div>
      %end
      %if service.action_url != '':
      <div class="btn-group pull-right">
         %action_urls = service.action_url.split('|')
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-external-link"></i> {{_('Action') if len(action_urls) == 1 else _('Actions')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
            %for action_url in Helper.get_element_actions_url(service, default_title="Url", default_icon="globe"):
            <li>{{!action_url}}</li>
            %end
         </ul>
      </div>
      %end
      %if tags:
      <div class="btn-group pull-right">
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <span class="fa fa-tag"></span>&nbsp;{{_('Tags')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
            %for tag in sorted(tags):
            <li><button class="btn btn-default btn-xs"><span class="fa fa-tag"></span> {{tag}}</button></li>
            %end
         </ul>
      </div>
      %end
      %if templates:
      <div class="service-templates btn-group pull-right">
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <span class="fa fa-clone"></span>&nbsp;{{_('Templates')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
            %for template in sorted(templates):
            <li><a href="/service/{{template.id}}"><span class="fa fa-clone"></span>&nbsp;{{template.alias}}</a></li>
            %end
         </ul>
      </div>
      %end

      <div class="panel-heading">
         <h4 class="panel-title" class="collapsed" data-toggle="collapse" href="#collapseServiceOverview" aria-expanded="false" aria-controls="collapseHostOverview">
            <span class="caret"></span>
               {{_('Overview for %s / %s') % (service.host.name, service.name)}} {{! Helper.get_html_business_impact(service.business_impact, icon=True, text=False)}}
         </h4>
      </div>

      <div id="collapseServiceOverview" class="panel-body panel-collapse collapse">
         %if service.customs and ('_DETAILLEDESC' in service.customs or '_IMPACT' in service.customs or '_FIXACTIONS' in service.customs):
         <div class="panel panel-default">
            <div class="panel-body">
               <dl class="col-sm-12 dl-horizontal">
                  %if '_DETAILLEDESC' in service.customs:
                  <dt>{{_('Description:')}}</dt>
                  <dd>{{service.customs['_DETAILLEDESC']}}</dd>
                  %end
                  %if '_IMPACT' in service.customs:
                  <dt>{{_('Impact:')}}</dt>
                  <dd>{{service.customs['_IMPACT']}}</dd>
                  %end
                  %if '_FIXACTIONS' in service.customs:
                  <dt>{{_('Fix actions:')}}</dt>
                  <dd>{{service.customs['_FIXACTIONS']}}</dd>
                  %end
               </dl>
            </div>
         </div>
         %end

         <div class="row">
            <dl class="col-sm-6 col-md-4">
               <dt>{{_('Host:')}}</dt>
               <dd>{{! host.html_state_link if host else ''}}</dd>

               <dt>{{_('Alias:')}}</dt>
               <dd>{{service.alias}}</dd>

               %if service.notes:
               <dt>{{_('Notes:')}}</dt>
               <dd>
               %for note_url in Helper.get_element_notes_url(service, default_title="Note", default_icon="tag"):
                  <button class="btn btn-default btn-xs">{{! note_url}}</button>
               %end
               </dd>
               %end

               <dt>{{_('Importance:')}}</dt>
               <dd>{{!Helper.get_html_business_impact(service.business_impact, icon=True, text=True)}}</dd>
            </dl>

            <dl class="col-sm-6 col-md-4">
               <dt>{{_('Parents:')}}</dt>
               %if parents:
               %for parent in parents:
               %for parent_service in parent.services:
               <dd>
               {{! parent_service.html_state_link}}
               </dd>
               %end
               %end
               %else:
               <dd>{{_('Do not depend upon any service')}}</dd>
               %end

               <dt>{{_('Children:')}}</dt>
               %if children:
               %for child in children:
               %for dependent_service in child.dependent_services:
               <dd>
               {{! dependent_service.html_state_link}}
               </dd>
               %end
               %end
               %else:
               <dd>{{_('No service depends upon me')}}</dd>
               %end
            </dl>
         </div>
      </div>
   </div>

   <!-- Third row : business impact alerting ... -->
   %if current_user.is_power():
      %if service and service.is_problem and service.business_impact > 2 and not service.acknowledged:
      <div class="panel panel-default">
         <div class="panel-heading" style="padding-bottom: -10">
            <div class="aroundpulse pull-left" style="padding: 8px;">
               <span class="big-pulse pulse"></span>
               <i class="fa fa-3x fa-spin fa-gear"></i>
            </div>
            <div style="margin-left: 60px;">
            %disabled_ack = '' if service.is_problem and not service.acknowledged else 'disabled'
            %disabled_fix = '' if service.is_problem and service.event_handler_enabled and service.event_handler else 'disabled'
            <p class="alert alert-danger" style="margin-bottom:0">
               {{_('This element has an important impact on your business, you may acknowledge it or try to fix it.')}}
            </p>
            </div>
         </div>
      </div>
      %end
   %end

   <!-- Fourth row : service widgets ... -->
   <div>
      <ul class="nav nav-tabs">
         %first=True
         %for widget in webui.get_widgets_for('service'):
            %if widget['id'] in ['grafana']:
               %plugin = webui.find_plugin('Grafana')
               %if not plugin or not plugin.is_enabled():
                  % continue
               %end
            %end
            %if 'level' in widget and widget['level'] > current_user.skill_level:
            % continue
            %end
            <li {{'class="active"' if first else ''}}>
               <a href="#service_{{widget['id']}}"
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
         %for widget in webui.get_widgets_for('service'):
            %if widget['id'] in ['grafana']:
               %plugin = webui.find_plugin('Grafana')
               %if not plugin or not plugin.is_enabled():
                  % continue
               %end
            %end
            %if 'level' in widget and widget['level'] > current_user.skill_level:
            % continue
            %end
            <div id="service_{{widget['id']}}" class="tab-pane fade {{'active in' if first else ''}}" role="tabpanel">
            </div>
            %first=False
         %end
      </div>
   </div>
</div>

<script>
   $(function () {
      bootstrap_tab_bookmark();
   })

   $(document).ready(function() {
      // Tabs management
      $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
         // Changed tab
         var $url = window.location.href.replace(window.location.search,'');
         $url = $url.split('#');
         if (($url[1] == undefined) || ($url[1] == '')) {
            $url = 'service_view';
         } else {
            $url = $url[1];
         }
         var loading='<div class="alert alert-info text-center"><span class="fa fa-spin fa-spinner"></span>&nbsp;{{_("Fetching data...")}}&nbsp;<span class="fa fa-spin fa-spinner"></span></div>';
         $('#'+$url).html(loading);
         $.ajax({
            url: '/'+$url+'/{{service.id}}'
         })
         .done(function(content, textStatus, jqXHR) {
            $('#'+$url).html(content);
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            console.error('get service tab, error: ', jqXHR, textStatus, errorThrown);
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