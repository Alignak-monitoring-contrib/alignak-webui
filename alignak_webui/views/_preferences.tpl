%import json

%rebase("layout", css=['user/htdocs/css/user.css'], breadcrumb=[ ['User preferences', '/user/pref'] ], title='User preferences')

<div id="user-preferences">
   <div class="col-sm-12">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h2 class="panel-title">User</h2>
         </div>
         <div class="panel-body">
            <!-- User image -->
            <div class="user-header bg-light-blue">
               <img src="{{current_user.picture}}" class="img-circle user-logo" alt="Photo: {{current_user.name}}" title="Photo: {{current_user.name}}">
               <p class="username">
                 {{current_user.get_username()}}
               </p>
               <p class="usercategory">
                  <small>{{current_user.get_role(display=True)}}</small>
               </p>
            </div>

            <div class="user-body">
               <table class="table table-condensed col-sm-12" style="table-layout: fixed; word-wrap: break-word;">
                  <colgroup>
                     <col style="width: 30%" />
                     <col style="width: 70%" />
                  </colgroup>
                  <thead>
                     <tr><th colspan="2"></td></tr>
                  </thead>
                  <tbody style="font-size:x-small;">
                     <tr>
                        <td><strong>{{_('User identification:')</strong></td>
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

               <table class="table table-condensed col-sm-12" style="table-layout: fixed; word-wrap: break-word;">
                  <colgroup>
                     <col style="width: 30%" />
                     <col style="width: 70%" />
                  </colgroup>
                  <thead>
                     <tr><th colspan="2"></td></tr>
                  </thead>
                  <tbody style="font-size:x-small;">
                     %for attr, value in current_user.__dict__.iteritems():
                     <tr>
                        <td><strong>{{attr}}:</strong></td>
                        <td>{{value}}</td>
                     </tr>
                     %end
                  </tbody>
               </table>

               <table class="table table-condensed col-sm-12" style="table-layout: fixed; word-wrap: break-word;">
                  <colgroup>
                     <col style="width: 30%" />
                     <col style="width: 70%" />
                  </colgroup>
                  <thead>
                     <tr>
                        <th colspan="2">Preferences:</td>
                     </tr>
                  </thead>
                  <tbody style="font-size:x-small;">
                  %if webui.prefs_module:
                     %preferences = webui.prefs_module.get_ui_user_preference(current_user.get_username())
                     %if preferences:
                     %for preference in sorted(preferences.keys()):
                        %if preference in ['_id']:
                        %continue
                        %end
                        <tr>
                           <td>{{preference}}</td>
                           <td>{{webui.prefs_module.get_ui_user_preference(current_user.get_username(), preference)}}</td>
                        </tr>
                     %end
                     %else:
                        <tr>
                           <td colspan="2">{{_('No user preferences')}}</td>
                        </tr>
                     %end
                  %else:
                     <tr>
                        <td>bookmarks</td>
                        <td>{{webui.prefs_module.get_ui_user_preference(current_user.get_username(), 'bookmarks')}}</td>
                     </tr>
                     <tr>
                        <td>elts_per_page</td>
                        <td>{{webui.prefs_module.get_ui_user_preference(current_user.get_username(), 'elts_per_page')}}</td>
                     </tr>
                  %end
                  </tbody>
               </table>
            </div>
         </div>
      </div>
   </div>
</div>
