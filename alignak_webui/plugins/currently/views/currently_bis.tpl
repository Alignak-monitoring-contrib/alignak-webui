%from bottle import request

%setdefault('refresh', True)
%rebase("fullscreen", css=[], js=[], title=title)

%import json

<style>
div.pull-right a, div.pull-right div {
   margin-top: 0px; margin-bottom: 0px;
}
.hosts-count, .services-count {
   font-size: 24px;
}
.hosts-state, .services-state {
   font-size: 12px;
}
</style>

<div id="currently">
    <script type="text/javascript">
        // Application globals
        dashboard_currently = true;

        // Panels user's preferences
        currently_panels = {{ ! json.dumps(currently_panels) }};
    </script>

    <nav id="topbar" class="navbar navbar-fixed-top">
       <div id="one-eye-toolbar" class="col-xs-12">
          <ul class="nav navbar-nav navbar-left">
             <li>
                <a tabindex="0" role="button"
                   data-toggle="tooltip" data-placement="bottom"
                   title="{{_('Go back to the dashboard')}}" href="/dashboard">
                   <span class="fa fa-home"></span>
                   <span class="sr-only">{{_('Go back to the main dashboard')}}</span>
                </a>
             </li>
             <li>
                <a tabindex="0" role="button"
                   data-action="fullscreen-request"
                   data-toggle="tooltip" data-placement="bottom"
                   title="{{_('Fullscreen page')}}" href="#">
                   <span class="fa fa-desktop"></span>
                   <span class="sr-only">{{_('Fullscreen page')}}</span>
                </a>
             </li>
             %if request.app.config.get('play_sound', 'no') == 'yes':
             <li id="sound_alerting">
                <a tabindex="0" role="button"
                   data-action="toggle-sound-alert"
                   data-toggle="tooltip" data-placement="bottom"
                   title="{{_('Sound alert on/off')}}" href="#">
                   <span class="fa fa-music"></span>
                   <span class="sr-only">{{_('Change sound playing state')}}</span>
                </a>
             </li>
             %end
          </ul>

          <ul class="nav navbar-nav navbar-right">
             <li>
                <p class="navbar-text font-darkgrey">
                   <span id="date"></span>&nbsp;&hyphen;&nbsp;<span id="clock"></span>
                </p>
             </li>
          </ul>
       </div>
    </nav>

    %if request.app.config.get('play_sound', 'no') == 'yes':
       %include("_sound_play.tpl")
    %end

    <div class="row" style="margin-top:60px;">
        <div id="one-eye-hosts-counters" class="col-xs-12 col-md-6">
          {{! panel_counters_hosts }}
        </div>
        <div id="one-eye-services-counters" class="col-xs-12 col-md-6">
          {{! panel_counters_services }}
        </div>

        <div id="one-eye-hosts-percentages" class="col-xs-12 col-md-6">
          {{! panel_percentage_hosts }}
        </div>
        <div id="one-eye-services-percentages" class="col-xs-12 col-md-6">
          {{! panel_percentage_services }}
        </div>
    </div>

    <div class="row" style="margin-top:60px;">
        <div id="livestate-graphs" class="col-xs-12">
        </div>
    </div>

    <script type="text/javascript">
        // Function called on each page refresh ... update graphs!
        function on_page_refresh(forced) {
        };

        $(document).ready(function(){
            on_page_refresh();

            // Date / time
            $('#clock').jclock({ format: '%H:%M:%S' });
            $('#date').jclock({ format: '%A, %B %d' });

            // Fullscreen management
            if (screenfull.enabled) {
                $('a[data-action="fullscreen-request"]').on('click', function() {
                    screenfull.request();
                });

                // Fullscreen changed event
                document.addEventListener(screenfull.raw.fullscreenchange, function () {
                    if (screenfull.isFullscreen) {
                        $('a[data-action="fullscreen-request"]').hide();
                    } else {
                        $('a[data-action="fullscreen-request"]').show();
                    }
                });
            }
        });

        // Panels collapse state
        $('.panel').on('hidden.bs.collapse', function () {
            wait_message('{{_('Saving configuration...')}}', true)

            console.log($(this).parent().attr('id'));
            currently_panels[$(this).parent().attr('id')].collapsed = true;
            $(this).find('.fa-minus-square').removeClass('fa-minus-square').addClass('fa-plus-square');
            save_user_preference('currently_panels', JSON.stringify(currently_panels), function() {
                wait_message('', false)
                // Page refresh required
                refresh_required = true;
            });
        });
        $('.panel').on('shown.bs.collapse', function () {
            wait_message('{{_('Saving configuration...')}}', true)

            currently_panels[$(this).parent().attr('id')].collapsed = false;
            $(this).find('.fa-plus-square').removeClass('fa-plus-square').addClass('fa-minus-square');
            save_user_preference('currently_panels', JSON.stringify(currently_panels), function() {
                wait_message('', false)
                // Page refresh required
                refresh_required = true;
            });
        });
    </script>
</div>