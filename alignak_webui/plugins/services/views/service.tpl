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
<div id="service-{{service.id}}">
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

   <!-- First row : tags and actions ... -->
   %groups = datamgr.get_servicegroups({'where': {'services': service.id}})
   %tags = service.tags
   %templates = service._templates
   %if service.action_url or tags or groups:
   <div>
      %if groups:
      <div class="btn-group pull-right">
         <button class="btn btn-primary btn-xs dropdown-toggle" data-toggle="dropdown">
            <span class="fa fa-sitemap"></span>&nbsp;{{_('Groups')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
         %for group in groups:
            <li>
            <a href="/servicegroup/{{group.id}}">{{group.alias}}</a>
            </li>
         %end
         </ul>
      </div>
      <div class="pull-right">&nbsp;&nbsp;</div>
      %end
      %if service.action_url != '':
      <div class="btn-group pull-right">
         %action_urls = service.action_url.split('|')
         <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
            <i class="fa fa-external-link"></i> {{_('Action') if len(action_urls) == 1 else _('Actions')}}&nbsp;<span class="caret"></span>
         </button>
         <ul class="dropdown-menu pull-right">
            %for action_url in Helper.get_element_actions_url(service, default_title="Url", default_icon="globe", popover=True):
            <li>{{!action_url}}</li>
            %end
         </ul>
      </div>
      <div class="pull-right">&nbsp;&nbsp;</div>
      %end
      %if tags:
      <div class="btn-group pull-right">
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
               <a href="{{ webui.get_url('Services table') }}?search=tags:{{tag}}">
                  <span class="fa fa-tag"></span> {{tag}}
               </a>
            %end
         %end
      </div>
      %end
      %#todo: edit the service templates!
      %if False:
      <div class="btn-group pull-right">
         %if len(templates) > 2:
            <button class="btn btn-info btn-xs dropdown-toggle" data-toggle="dropdown">
               <i class="fa fa-tag"></i>&nbsp;{{_('Templates')}}&nbsp;<span class="caret"></span>
            </button>
            <ul class="dropdown-menu pull-right">
               %for tag in sorted(templates):
               <li><button class="btn btn-default btn-xs"><span class="fa fa-tag"></span> {{tag}}</button></li>
               %end
            </ul>
         %else:
            %for tag in sorted(templates):
               <a href="{{ webui.get_url('Services table') }}?search=tags:{{tag}}">
                  <span class="fa fa-tag"></span> {{tag}}
               </a>
            %end
         %end
      </div>
      %end
   </div>
   %end

   <!-- Second row : service overview ... -->
   <div class="panel panel-default">
      <div class="panel-heading">
         <h4 class="panel-title">
            <a class="collapsed" role="button" data-toggle="collapse" href="#collapseServiceOverview" aria-expanded="false" aria-controls="collapseServiceOverview">
               <span class="caret"></span>
               {{_('Overview for %s / %s') % (service.host.name, service.name)}} {{! Helper.get_html_business_impact(service.business_impact, icon=True, text=False)}}
            </a>
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
               <dd>{{! host.html_state_link}}</dd>

               <dt>{{_('Alias:')}}</dt>
               <dd>{{service.alias}}</dd>

               %if service.notes:
               <dt>{{_('Notes:')}}</dt>
               <dd>
               %for note_url in Helper.get_element_notes_url(service, default_title="Note", default_icon="tag", popover=True):
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
         <li class="active">
            <a href="#service_tab_view"
               role="tab" data-toggle="tab" aria-controls="view"
               title="{{_('Service synthesis view')}}"
               >
               <span class="fa fa-server"></span>
               <span class="hidden-sm hidden-xs">{{_('Service view')}}</span>
            </a>
         </li>

         %for widget in webui.get_widgets_for('service'):
            <li>
               <a href="#service_tab_{{widget['id']}}"
                  role="tab" data-toggle="tab" aria-controls="{{widget['id']}}"
                  title="{{! widget['description']}}"
                  >
                  <span class="fa fa-{{widget['icon']}}"></span>
                  <span class="hidden-sm hidden-xs">{{widget['name']}}</span>
               </a>
            </li>
         %end
      </ul>

      <div class="tab-content">
         <div id="service_tab_view" class="tab-pane fade active in" role="tabpanel">
            %include("_widget.tpl", widget_name='service_view', options=None, embedded=True, title=None)
         </div>

         %for widget in webui.get_widgets_for('service'):
            <div id="service_tab_{{widget['id']}}" class="tab-pane fade" role="tabpanel">
               %include("_widget.tpl", widget_name=widget['template'], options=widget['options'], embedded=True, title=None)
            </div>
         %end
      </div>
   </div>
</div>

<script>
   // Automatically navigate to the desired tab if an # exists in the URL
   function bootstrap_tab_bookmark(selector) {
      if (selector == undefined) {
         selector = "";
      }

      var bookmark_switch = function () {
         url = document.location.href.split('#');
         if (url[1] != undefined) {
            $(selector + '[href="#'+url[1]+'"]').tab('show');
         }
      }

      /* Automatically jump on good tab based on anchor */
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
      bootstrap_tab_bookmark();
   })
   $(document).ready(function() {
      /* Activate the popover for the notes and actions urls
      $('[data-toggle="popover urls"]').popover({
         placement: 'bottom',
         animation: true,
         template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
         content: function() {
            return $('#services-states-popover-content').html();
         }
      });
      */

      // Tabs management
      $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
         // Changed tab
      })
   });
 </script>