%debug=False
%# Fetch elements per page preference for user, default is 25
%elts_per_page = datamgr.get_user_preferences(current_user.get_username(), 'elts_per_page', 25)

%# Fetch sound preference for user, default is 'no'
%sound_pref = datamgr.get_user_preferences(current_user.get_username(), 'sound', None)
%if not sound_pref:
%datamgr.set_user_preferences(current_user.get_username(), 'sound', {'sound': request.app.config.get('play_sound', 'no')})
%end


<script type="text/javascript">
   // Periodical header refresh ... this function is called by the global refresh handler.
   function header_refresh() {
      $.ajax({
         url: "/ping?action=header",
         method: "get",
         dataType: "html"
      })
      .done(function(html, textStatus, jqXHR) {
         if (refresh_logs) console.debug("Update header - hosts state");
         $('#overall-hosts-states').html(html);
         // Activate the popover ...
         $('#hosts-states-popover').popover({
            placement: 'bottom',
            animation: true,
            template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>',
            content: function() {
               return $('#hosts-states-popover-content').html();
            }
         });
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         console.error('header_refresh, hosts failed: ', jqXHR, textStatus, errorThrown);
      });

      /*
      $.ajax({
         url: "/header_services",
         method: "get",
         dataType: "html"
      })
      .done(function(html, textStatus, jqXHR) {
         if (refresh_logs) console.debug("Update header services state");
         $('#overall-services-states').html(html);
         // Activate the popover ...
         $('#hosts-services-popover').popover({
            placement: 'bottom',
            animation: true,
            template: '<div class="popover"><div class="arrow"></div><div class="popover-inner"><h3 class="popover-title"></h3><div class="popover-content"><p></p></div></div></div>',
            content: function() {
               return $('#hosts-services-popover-content').html();
            }
         });
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         console.error('header_refresh, services failed: ', jqXHR, textStatus, errorThrown);
      });
      */
   }

   $(document).ready(function(){
      header_refresh();
   });

</script>


<!-- Page header -->
<header>
   <nav id="topbar-menu" class="navbar navbar-default navbar-fixed-top">
      <div class="container-fluid">
         <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapsible-part">
               <span class="sr-only">{{_('Toggle navigation')}}</span>
               <span class="icon-bar"></span>
               <span class="icon-bar"></span>
               <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand">
               <img src="/static/logo/{{request.app.config.get('company_logo', 'default_company')}}" alt="{{_('Company logo')}}" />
            </a>
         </div>

         <!-- Right part ... -->
         <div id="navbar-collapsible-part" class="collapse navbar-collapse">
            <div class="hidden-xs">
               <!-- Page filtering ... -->
               %include("_filters.tpl")
            </div>

            <ul class="nav navbar-nav navbar-right">
               <li id="overall-hosts-states">
                  %include("_header_hosts_state.tpl")
               </li>

               %if request.app.config.get('play_sound', 'no') == 'yes':
               <li class="hidden-sm hidden-xs hidden-md">
                  <a data-action="toggle-sound-alert" data-original-title="{{_('Sound alerting')}}" href="#">
                     <span id="sound_alerting" class="fa-stack">
                       <i class="fa fa-music fa-stack-1x"></i>
                       <i class="fa fa-ban fa-stack-2x text-danger"></i>
                     </span>
                  </a>
               </li>
               %end

               %if refresh:
               <li>
                  <a data-action="toggle-page-refresh" data-toggle="tooltip" data-placement="bottom" title="{{_('Refresh page every %d seconds.') % (int(request.app.config.get('refresh_period', '60')))}}" href="#">
                     <i id="header_loading" class="fa fa-refresh"></i>
                  </a>
               </li>
               %end

               %if debug:
               <li class="dropdown">
                  <a href="#" class="dropdown-toggle" data-original-title="Debug" data-toggle="dropdown">
                     <i class="fa fa-bug"></i>
                     <i class="caret"></i>
                  </a>
                  <ul class="dropdown-menu">
                     <li>
                        <div class="panel panel-default">
                           <div class="panel-body">
                              <ul class="list-group">
                                 <li class="list-group-item"><small>Current user: {{current_user}}</small></li>
                                 <li class="list-group-item"><small>Target user: {{target_user}}</small></li>
                              </ul>
                              <div class="panel-footer">Total: {{datamgr.get_objects_count('user')}} users</div>
                           </div>
                        </div>
                     </li>
                  </ul>
               </li>
               %end

               <!-- User info -->
               <li class="dropdown user user-menu hidden-xs">
                  <a href="#" class="dropdown-toggle" data-original-title="{{_('User menu')}}" data-toggle="dropdown">
                     <i class="fa fa-user"></i>
                        %if not target_user.is_anonymous() and current_user.get_username() != target_user.get_username():
                        <span class="label label-warning" style="position:relative; left: 0px">{{target_user.get_username()}}</span>
                        %end
                        <span class="username hidden-sm hidden-xs hidden-md">{{current_user.get_name()}}</span>
                        <i class="caret"></i>
                  </a>

                  <ul class="dropdown-menu">
                     <li class="user-header">
                        %include("_select_target_user")
                     </li>
                     <li class="user-header">
                        <div class="panel panel-info" id="user_info">
                           <div class="panel-body panel-default">
                              <!-- User image / name -->
                              <p class="username">{{current_user.get_name()}}</p>
                              <p class="usercategory">
                                 <small>{{current_user.get_role(display=True)}}</small>
                              </p>
                              <img src="{{current_user.get_picture()}}" photo="{{current_user.get_picture()}}" class="img-circle user-logo" alt="Photo: {{current_user.get_name()}}" title="Photo: {{current_user.get_name()}}">
                           </div>
                           <div class="panel-footer">
                              %if current_user.is_administrator():
                              <div class="btn-group" role="group">
                                 <a href="/user/preferences" class="btn btn-default"><span class="fa fa-pencil"></span> </a>
                              </div>
                              %end
                              <div class="btn-group" role="group">
                                 <a href="/logout" class="btn btn-default btn-flat"><span class="fa fa-sign-out"></span> </a>
                              </div>
                           </div>
                        </div>
                     </li>
                  </ul>
               </li>
               <li class="col-xs-1 hidden-sm hidden-md hidden-lg">
                  <a data-action="logout"
                     data-toggle="tooltip" data-placement="bottom" title="{{_('Sign out')}}"
                     href="/logout">
                     <i class="fa fa-sign-out"></i>
                  </a>
               </li>
            </ul>

            <div class="col-xs-10 col-sm-offset-1 col-sm-10 hidden-md hidden-lg">
               <!-- Sidebar menu is included in the header for small devices -->
               %include("_sidebar.tpl", action_bar=True, in_sidebar=True)
            </div>
         </div>
      </div>
   </nav>
</header>


%if request.app.config.get('play_sound', 'no') == 'yes':
   <audio id="alert-sound" volume="1.0">
      <source src="/static/sound/alert.wav" type="audio/wav">
      Your browser does not support the <code>HTML5 Audio</code> element.
      <EMBED src="/static/sound/alert.wav" autostart=true loop=false volume=100 >
   </audio>

   <script type="text/javascript">
      // Set alerting sound icon ...
      if (! hostStorage.getItem("sound_play")) {
         // Default is to play ...
         hostStorage.setItem("sound_play", '1');
      }

      // Toggle sound ...
      if (hostStorage.getItem("sound_play") == '1') {
         $('#sound_alerting i.fa-ban').addClass('hidden');
      } else {
         $('#sound_alerting i.fa-ban').removeClass('hidden');
      }
      $('[data-action="toggle-sound-alert"]').on('click', function (e, data) {
         if (hostStorage.getItem("sound_play") == '1') {
            hostStorage.setItem("sound_play", "0");
            $('#sound_alerting i.fa-ban').removeClass('hidden');
         } else {
            playAlertSound();
            $('#sound_alerting i.fa-ban').addClass('hidden');
         }
      });
   </script>
%end
