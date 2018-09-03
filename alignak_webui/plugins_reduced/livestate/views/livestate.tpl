%setdefault('layout',  'table')
%setdefault('view_table',  True)
%setdefault('view_panels',  False)
%setdefault('view_tabs',  False)

%setdefault('ls',  None)
%setdefault('l_events', None)
%from bottle import request
%from alignak_webui.objects.element_state import ElementState
%items_states = ElementState()

%rebase("fullscreen_reduced",  css=[],  js=[],  title=title)

%import json

<script type="text/javascript">
   var loading='<div class="alert alert-info text-center"><span class="fa fa-spin fa-spinner"></span>&nbsp;{{_("Fetching data...")}}&nbsp;<span class="fa fa-spin fa-spinner"></span></div>';

   var lst_events = [];
</script>


<div id="loading">
</div>
<div id="livestate">
   <div id="events_log">
      <ol class="timeline">
      </ol>
   </div>

   %if request.app.config.get('play_sound',  'no') == 'yes':
      %include("_sound_play.tpl")
   %end

   %include("_problems_synthesis_reduced.tpl",  ls=ls)
   %include("_problems_list_reduced.tpl",  l_events=l_events)

   <script type="text/javascript">
      var debug_logs = false;

      // Function called on each page refresh ... update elements!
      function on_page_refresh(forced) {
         if (debug_logs) console.debug("livestate,  on_page_refresh",  forced);

         // If a request is still in progress, return...
         if ($(window).data('ajaxready') == false) return;

         // Set ajaxready to avoid multiple requests...
         $(window).data('ajaxready', false);

         // Update problems synthesis
         $.ajax({
             url: "/ping?action=refresh&template=_problems_synthesis_reduced"
         })
         .done(function(content, textStatus, jqXHR) {
             $('#synthesis').html(content);
         });

         // Update problems list
         $.ajax({
             url: "/ping?action=refresh&template=_problems_list_reduced"
         })
         .done(function(content, textStatus, jqXHR) {
             $('#problems').html(content);
         });

         // Update problems list
         $('#loading').show();

         $('#loading').html(loading);
         $.ajax({
             url: "/events_log"
         })
         .done(function(content, textStatus, jqXHR) {
            console.log(content);
            for (var i = 0; i < content.length; i++) {
               var lcr = content[i];
               var splitted = lcr['message'].split(';');
               var badge = '';
               if (splitted[0].indexOf('HOST') != -1) {
                  badge=''
               }
               var tl_item = ' \
                  <div class="timeline-badge"> \
                     <span class="' + lcr['class'] + ' fa fa-' + lcr['icon'] + '"></span> \
                  </div> \
                  <div class="timeline-panel"> \
                     <div class="timeline-heading"> \
                        <div class="pull-left"> \
                           host \
                        </div> \
                        <div class="pull-right clearfix"> \
                           <small class="text-muted"> \
                              <span class="fa fa-clock-o"></span> \
                              <em title="Temps!"><strong>' + lcr['timestamp'] + '</strong></em> \
                           </small> \
                        </div> \
                        <div class="clearfix"> \
                        </div> \
                     </div> \
                     <div class="timeline-body"> \
                        <p><small> ' + lcr['message'] + '</small></p> \
                     </div> \
                  </div> \
               ';
               var elt = $('<li>' + tl_item + '</li>');
               $(elt)
                  .appendTo('#events_log ol')
                  .delay(300)
                  .slideDown('slow');
            }

            $('#timeline_loading').hide();
         })
         .always(function() {
            $('#loading').hide();
            $(window).data('ajaxready', true);
         });
      };

      $(document).ready(function(){
         // Set ajaxready because no request is ongoing...
         $(window).data('ajaxready', true);

         on_page_refresh();

         // Date / time
         $('#clock').jclock({ format: '%H:%M:%S' });
         $('#date').jclock({ format: '%A,  %B %d' });

         %if message:
            raise_message_{{message.get('status', 'ko')}}("{{! message.get('message')}}");
         %end

         // Fullscreen management
         if (screenfull.enabled) {
            $('a[data-action="fullscreen-request"]').on('click',  function() {
               screenfull.request();
            });

            // Fullscreen changed event
            document.addEventListener(screenfull.raw.fullscreenchange,  function () {
               if (screenfull.isFullscreen) {
                  $('a[data-action="fullscreen-request"]').hide();

                  %if current_user.is_power():
                  $('div[data-type="actions"]').each(function (index,  child) {
                     if (debug_logs) console.debug("Hiding actions buttons...");
                     $(this).hide();
                  });
                  %end
               } else {
                  $('a[data-action="fullscreen-request"]').show();

                  %if current_user.is_power():
                  $('div[data-type="actions"]').each(function (index,  child) {
                     if (debug_logs) console.debug("Hiding actions buttons...");
                     $(this).show();
                  });
                  %end
               }
            });
         }
      });
   </script>
</div>