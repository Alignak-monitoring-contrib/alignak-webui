%setdefault('debug', False)
%setdefault('user', element)
%setdefault('title', _('User view'))

%rebase("layout", title=title, js=[], css=[], page="/user/{{element.name}}")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_service import Service

<!-- User view -->
<div class="user" id="user_{{element.id}}">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{user.id}}"><i class="fa fa-bug"></i> user as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{user.id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(user.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
   </div>
   %end
   <!-- First row : user/service overview ... -->
   <div class="panel panel-default">
      <div class="panel-heading">
         <h4 class="panel-title">
            <a class="collapsed" role="button" data-toggle="collapse" href="#collapseuserOverview" aria-expanded="false" aria-controls="collapseuserOverview">
               <span class="caret"></span>
               {{_('Overview for %s') % user.name}}
            </a>
         </h4>
      </div>

      <div id="collapseuserOverview" class="panel-body panel-collapse collapse">
         %if user.customs and ('_DETAILLEDESC' in user.customs or '_IMPACT' in user.customs or '_FIXACTIONS' in user.customs):
         <div class="panel panel-default">
            <div class="panel-body">
               <dl class="col-sm-12 dl-horizontal">
                  %if '_DETAILLEDESC' in user.customs:
                  <dt>{{_('Description:')}}</dt>
                  <dd>{{user.customs['_DETAILLEDESC']}}</dd>
                  %end
                  %if '_IMPACT' in user.customs:
                  <dt>{{_('Impact:')}}</dt>
                  <dd>{{user.customs['_IMPACT']}}</dd>
                  %end
                  %if '_FIXACTIONS' in user.customs:
                  <dt>{{_('Fix actions:')}}</dt>
                  <dd>{{user.customs['_FIXACTIONS']}}</dd>
                  %end
               </dl>
            </div>
         </div>
         %end

         <div class="row">
            <dl class="col-sm-6 col-md-4">
               <dt>{{_('Alias:')}}</dt>
               <dd>{{user.alias}}</dd>

               %if user.notes:
               <dt>{{_('Notes:')}}</dt>
               <dd>
               %for note_url in Helper.get_element_notes_url(user, default_title="Note", default_icon="tag", popover=True):
                  <button class="btn btn-default btn-xs">{{! note_url}}</button>
               %end
               </dd>
               %end
            </dl>
         </div>
      </div>
   </div>

   <!-- Second row : user widgets ... -->
   <div>
      <ul class="nav nav-tabs">
         <li class="active">
            <a href="#user_tab_view"
               role="tab" data-toggle="tab" aria-controls="view"
               title="{{_('user synthesis view')}}"
               >
               <span class="fa fa-server"></span>
               <span class="hidden-sm hidden-xs">{{_('user view')}}</span>
            </a>
         </li>

         %for widget in webui.get_widgets_for('user'):
            <li>
               <a href="#user_tab_{{widget['id']}}"
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
         <div id="user_tab_view" class="tab-pane fade active in" role="tabpanel">
            %include("_widget.tpl", widget_name='user_view', options=None, embedded=True, title=None)
         </div>

         %for widget in webui.get_widgets_for('user'):
            <div id="user_tab_{{widget['id']}}" class="tab-pane fade" role="tabpanel">
               %include("_widget.tpl", widget_name=widget['template'], options=widget['options'], embedded=True, title=None)
            </div>
         %end
      </div>
   </div>
</div>

<script>
   $(function () {
      bootstrap_tab_bookmark();
   })
   $(document).ready(function() {
      // Activate the popover for the notes and actions urls
      $('[data-toggle="popover urls"]').popover({
         placement: 'bottom',
         animation: true,
         template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><div class="popover-title"></div><div class="popover-content"></div></div></div>',
         content: function() {
            return $('#users-states-popover-content').html();
         }
      });

      // Tabs management
      $('a[data-toggle="tab"]').on('shown.bs.tab', function (e) {
         // Changed tab
      })
   });
 </script>