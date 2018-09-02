<audio id="alert-sound" volume="1.0">
   <source src="/static/sound/alert.wav" type="audio/wav">
   Your browser does not support the <code>HTML5 Audio</code> element.
   <EMBED src="/static/sound/alert.wav" autostart=true loop=false volume=100 >
</audio>

<script type="text/javascript">
   get_user_preference('sound', function(data) {
      // Toggle sound icon...
      if (data == 'no') {
         sound_activated = false;
         $('#sound_alerting').addClass('disabled text-warning');
      } else {
         sound_activated = true;
         $('#sound_alerting').removeClass('disabled text-warning');
      }
      $('[data-action="toggle-sound-alert"]').on('click', function (e, data) {
         get_user_preference('sound', function(data) {
            if (data == 'no') {
               save_user_preference('sound', JSON.stringify('yes'), function(){
                  sound_activated = true;
                  playAlertSound();
                  $('#sound_alerting').removeClass('disabled text-warning');
               });
            } else {
               save_user_preference('sound', JSON.stringify('no'), function() {
                  sound_activated = false;
                  $('#sound_alerting').addClass('disabled text-warning');
               });
            }
         });
      });
   }, 'yes');
</script>
