%setdefault('debug', False)
%setdefault('title', _('Users group view'))

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], page="/usergroup/{{element.name}}")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<div class="usergroup" id="usergroup_{{element.id}}">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{element.id}}"><i class="fa fa-bug"></i> usergroup as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{element.id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(element.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Group members as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for elt in element.members:
               %if isinstance(elt, basestring):
               %continue
               %end
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#collapse_{{elt.id}}"><i class="fa fa-bug"></i> {{elt.name}}</a>
                     </h4>
                  </div>
                  <div id="collapse_{{elt.id}}" class="panel-collapse collapse">
                     <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                        %for k,v in sorted(elt.__dict__.items()):
                           <dt>{{k}}</dt>
                           <dd>{{v}}</dd>
                        %end
                     </dl>
                  </div>
               </div>
               %end
            </ul>
            <div class="panel-footer">{{len(element.members)}} members</div>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse2"><i class="fa fa-bug"></i> Group groups as dictionaries</a>
            </h4>
         </div>
         <div id="collapse2" class="panel-collapse collapse">
            <ul class="list-group">
               %for elt in groups:
               %if isinstance(elt, basestring):
               %continue
               %end
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#collapse_{{elt.id}}"><i class="fa fa-bug"></i> {{elt.name}}</a>
                     </h4>
                  </div>
                  <div id="collapse_{{elt.id}}" class="panel-collapse collapse">
                     <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                        %for k,v in sorted(elt.__dict__.items()):
                           <dt>{{k}}</dt>
                           <dd>{{v}}</dd>
                        %end
                     </dl>
                  </div>
               </div>
               %end
            </ul>
            <div class="panel-footer">{{len(element.members)}} groups</div>
         </div>
      </div>
   </div>
   %end

   %if element._parent and element._parent is not None and element._parent != 'usergroup':
   <div class="usergroup-parent btn-group" role="group" aria-label="{{_('Group navigation')}}">
      <a class="btn btn-default btn-raised" href="{{element._parent.endpoint}}" role="button">
         <span class="fa fa-arrow-up"></span>
         {{_('Parent group')}}
      </a>
   </div>
   %end

   <div class="usergroup-members panel panel-default">
      <div class="panel-body">
         <div class="col-xs-6 col-sm-2 text-center">
            {{! element.get_html_state(text=None, size="fa-3x")}}
            <legend><strong>{{element.alias}}</strong></legend>

            <div class="actions">
               %if current_user.is_power():
                  {{! Helper.get_html_commands_buttons(element, _('Actions'))}}
               %end
            </div>
         </div>
         <div class="col-xs-6 col-sm-10">
         %if not element.members or isinstance(element.members, basestring):
            <div class="text-center alert alert-warning">
               <h4>{{_('No users found in this group.')}}</h4>
            </div>
         %else:
            <table class="table table-condensed">
               <thead><tr>
                  <th style="width: 40px"></th>
                  <th>{{_('User')}}</th>
                  <th>{{_('Realm')}}</th>
                  <th>{{_('Administrator')}}</th>
                  <th>{{_('Commands')}}</th>
                  <th>{{_('Email')}}</th>
               </tr></thead>

               <tbody>
               %for elt in element.members:
                  <tr id="#{{elt.id}}">
                     <td title="{{elt.alias}}">
                        {{! elt.get_html_state(text=None)}}
                     </td>

                     <td title="{{elt.alias}}">
                        <small>{{!elt.get_html_link()}}</small>
                     </td>

                     <td>
                        <small>{{! elt._realm.get_html_link()}}</small>
                     </td>

                     <td>
                        <small>{{! webui.helper.get_on_off(status=elt.is_administrator())}}</small>
                     </td>

                     <td>
                        <small>{{! webui.helper.get_on_off(elt.is_power())}}</small>
                     </td>

                     <td>
                        {{! elt.email}}
                     </td>
                  </tr>
               %end
               </tbody>
            </table>
         %end
            </div>
      </div>
   </div>

   <div class="panel panel-default">
      %if not groups or groups == 'usergroup':
         <!--
         <div class="text-center alert alert-warning">
            <h4>{{_('No groups found in this group.')}}</h4>
         </div>
         -->
      %else:
      <div class="panel-body">
         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               <th>{{_('Group')}}</th>
               <th>{{_('Notes')}}</th>
               <th>{{_('Parent')}}</th>
            </tr></thead>

            <tbody>
            %plugin = webui.find_plugin('Users groups')
            %for elt in groups:
               %if isinstance(elt, basestring):
               %continue
               %end
               <tr id="usergroup_{{elt.id}}">
                  <td title="{{elt.alias}}">
                     {{! elt.get_html_state(text=None)}}
                  </td>

                  <td>
                     {{! elt.get_html_link()}}
                  </td>

                  <td>
                     {{elt.notes}}
                  </td>

                  <td>
                     %if elt._parent and elt._parent != 'usergroup':
                     {{elt._parent.alias}}
                     %end
                  </td>
               </tr>
            %end
            </tbody>
         </table>
      </div>
      %end
   </div>
 </div>
