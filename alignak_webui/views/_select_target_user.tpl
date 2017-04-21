
%# If more than one user declared ...
%if (current_user.is_super_administrator() or current_user.is_administrator()) and datamgr.get_objects_count('user') > 1:
   <div class="navbar" role="toolbar" aria-label="{{_('Select a user to change dashboard layout')}}">
      <form>
         %# No target user is defined ...
         %if target_user.is_anonymous() or current_user.get_username() == target_user.get_username():
               <!-- List existing users, except current and target users -->
               <select id="users_list" class="form-control" >
               %for user in datamgr.get_users():
                  %if user.id != current_user.id and user.id != target_user.id:
                  <option value="{{user.get_username()}}" selected={{'selected' if target_user and target_user.get_username() == user.get_username() else ''}}>{{user.name}}&nbsp;({{user.get_username()}})</option>
                  %end
               %end
               </select>
               <a id="change_user" class="btn btn-default navbar-btn">
                  <i class="fa fa-user"></i> {{_('Target')}}
               </a>
         %else:
            %if current_user.get_username() != target_user.get_username():
            <!-- A target user is currently defined -->
            <a id="reset_user" class="btn btn-default navbar-btn">
               <i class="fa fa-remove"></i> {{_('Unset')}}
               <span class="label label-warning" style="position:relative; left: 0px">{{target_user.get_username()}}</span>
            </a>
            %end
         %end
      </form>
   </div>

   %if datamgr.get_objects_count('user') > 1:
   <script>
      $(document).ready(function(){
         $("#users_list").change(function() {
            $( "select option:selected" ).each(function() {
               if ($(this).text() != '{{current_user.get_username()}}') {
                  $('#change_user').data('target', $(this).val());
                  $('#change_user').html('<i class="fa fa-user"></i> {{_('Target')}}: ' + '<span class="label label-primary">'+$(this).val()+'</span>');
               } else {
                  queryDict['target_user'] = "";
                  $('#change_user').attr('href', "&target_user=");
                  $('#change_user').html('<i class="fa fa-user"></i> {{_('Target')}}');
               }
            });
         });
         $("#users_list").trigger('change');

         // Select target user
         $('body').on("click", '#change_user', function () {
            // Parse current page parameters
            var queryDict = {};
            window.location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]});
            queryDict['target_user'] = $(this).data('target');
            window.location.search = $.param(queryDict);
         });

         // Cancel target user
         $('body').on("click", '#reset_user', function () {
            // Parse current page parameters
            var queryDict = {};
            window.location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]});
            queryDict.target_user = "";
            window.location.search = $.param(queryDict);
         });
      });
   </script>
   %end
%end
