%setdefault('debug', False)

<script type="text/javascript">
   // Check header refresh period (seconds)
   var header_refresh_period = {{request.app.config.get('header_refresh_period', '30')}};

   // Periodical header refresh ... this function is called by the global refresh handler.
   function header_refresh() {
      $.ajax({
         url: "/ping?action=refresh&template=_header_hosts_state"
      })
      .done(function(content, textStatus, jqXHR) {
         $('#overall-hosts-states').html(content);
      });

      $.ajax({
         url: "/ping?action=refresh&template=_header_services_state"
      })
      .done(function(content, textStatus, jqXHR) {
         $('#overall-services-states').html(content);
      });
   }

   $(document).ready(function(){
      // Start refresh periodical check ... every header_refresh_period second
      if (header_refresh_period != 0) {
         setInterval("header_refresh();", header_refresh_period*1000);
      } else {
         console.log('Automatic header refresh disabled.');
      }
   });
</script>


<!-- Page header -->
<header>
   <nav id="topbar" class="navbar navbar-fixed-top">
      <div class="navbar-header">
         <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar-collapsible-part">
            <span class="sr-only">{{_('Toggle navigation')}}</span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
            <span class="icon-bar"></span>
         </button>
         <a class="navbar-brand" href="/" style="float: left">
            <img src="/static/images/{{request.app.config.get('company_logo', 'default_company.png')}}" alt="{{_('Company logo')}}" />
         </a>

         <ul class="nav navbar-nav navbar-left">
            <li id="overall-hosts-states" class="pull-left">
               %include("_header_hosts_state.tpl")
            </li>

            <li id="overall-services-states" class="pull-left">
               %include("_header_services_state.tpl")
            </li>
         </ul>
      </div>

      <!-- Right part ... -->
      <div id="navbar-collapsible-part" class="collapse navbar-collapse">
         <ul class="nav navbar-nav navbar-left">
            <!-- Page filtering ... -->
            %include("_filters.tpl")

            <li class="hidden-xs" id="loading" style="display: none;">
               <a href="#">
                  <span class="fa fa-spinner fa-pulse fa-1x"></span>
                  <span class="sr-only">{{_('Loading...')}}</span>
               </a>
            </li>
         </ul>

         %include("_menubar.tpl", action_bar=True, in_sidebar=True)

         <ul class="nav navbar-nav navbar-right">
            <li>
               <a data-action="display-currently"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Display fullscreen one-eye view.')}}"
                  href="/currently">
                  <span class="fa fa-eye"></span>
               </a>
            </li>

            %if request.app.config.get('play_sound', 'no') == 'yes':
            <li id="sound_alerting">
               <a data-action="toggle-sound-alert"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Sound alert on/off')}}"
                  href="#">
                  <span class="fa fa-music"></span>
                  <span class="sr-only">{{_('Change sound playing state')}}</span>
               </a>
            </li>
            %end

            %if refresh:
            <li id="refresh_active">
               <a data-action="toggle-page-refresh"
                  data-toggle="tooltip" data-placement="bottom"
                  title="{{_('Refresh page every %d seconds.') % (int(request.app.config.get('refresh_period', '60')))}}"
                  href="#">
                  <span class="fa fa-refresh"></span>
                  <span class="sr-only">{{_('Change page refresh state')}}</span>
               </a>
            </li>
            %end

            %include("_header_user.tpl")
         </ul>
      </div>
   </nav>
</header>

%if request.app.config.get('play_sound', 'no') == 'yes':
   %include("_sound_play.tpl")
%end
