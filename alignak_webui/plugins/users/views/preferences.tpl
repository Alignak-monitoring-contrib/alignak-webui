%import json

%rebase("layout", css=['users/static/css/users.css'], title=_('User preferences'))

<div id="user-preferences">
   <div class="panel">
      <div class="panel-body">
         <!-- User picture -->
         <div class="user-header bg-light-blue">
            <img src="{{current_user.picture}}" class="img-circle user-logo" alt="Photo: {{current_user.name}}" title="Photo: {{current_user.name}}">
            <p class="username">
              {{current_user.alias}}
            </p>
            <p class="usercategory">
               <small>{{current_user.get_role(display=True)}}</small>
            </p>
         </div>

         <div class="user-body">
            <table class="table table-condensed table-user-identification col-sm-12" style="table-layout: fixed; word-wrap: break-word;">
               <colgroup>
                  <col style="width: 40%" />
                  <col style="width: 60%" />
               </colgroup>
               <thead>
                  <tr><th colspan="2"></th></tr>
               </thead>
               <tbody style="font-size:x-small;">
                  <tr>
                     <td><strong>{{_('User identification:')}}</strong></td>
                     <td>{{"%s (%s)" % (current_user.name, current_user.get_username()) if current_user.name != 'none' else current_user.get_username()}}</td>
                  </tr>
                  <tr>
                     <td><strong>{{_('User is allowed to run commands')}}</strong></td>
                     <td>{{! webui.helper.get_on_off(current_user.is_power(), _('Is this user allowed to launch commands from Web UI?'))}}</td>
                  </tr>
                  <tr>
                     <td><strong>{{_('User can change dashboard widgets')}}</strong></td>
                     <td>{{! webui.helper.get_on_off(current_user.can_change_dashboard(), _('Is this user allowed to configure dashboard widgets?'))}}</td>
                  </tr>
               </tbody>
            </table>

            <table class="table table-condensed table-user-preferences col-sm-12" style="table-layout: fixed; word-wrap: break-word;">
               <colgroup>
                  <col class="col-sm-1">
                  <col class="col-sm-3">
                  <col class="col-sm-8">
               </colgroup>
               <thead>
                  <tr>
                     <th colspan="3">{{_('User preferences:')}}</th>
                  </tr>
               </thead>
               <tbody style="font-size:x-small;">
                  %preferences = datamgr.get_user_preferences(current_user, None)
                  %if preferences:
                  %for key in sorted(preferences):
                     <tr>
                        <td>
                        %if current_user.is_power():
                           <a class="btn btn-default btn-xs btn-raised" href="#"
                              data-action="delete-user-preference"
                              data-element="{{key}}"
                              data-message="{{_('User preference deleted')}}"
                              data-toggle="tooltip" data-placement="top"
                              title="{{_('Delete this user preference')}}">
                              <span class="fa fa-trash"></span>
                           </a>
                        %end
                        </td>
                        <td>{{key}}</td>
                        %value = datamgr.get_user_preferences(current_user, key)
                        <td>
                        %if isinstance(value, dict):
                        <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                           %for k,v in sorted(value.items()):
                              <dt>{{k}}</dt>
                              <dd>{{v}}</dd>
                           %end
                        </dl>
                        %elif isinstance(value, list):
                        <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                           %idx=0
                           %for v in value:
                              <dt>{{idx}}</dt>
                              <dd>{{v}}</dd>
                              %idx += 1
                           %end
                        </dl>
                        %else:
                        {{value}}
                        %end
                        </td>
                     </tr>
                  %  end
                  %else:
                     <tr>
                        <td colspan="2">{{_('No user preferences')}}</td>
                     </tr>
                  %end
               </tbody>
            </table>
         </div>
      </div>
   </div>
</div>
