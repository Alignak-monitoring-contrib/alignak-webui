/*
* Copyright (C) 2015-2016 F. Mohier pour IPM France:
*/

var log_layout=false;

/*
 * For IE missing window.console ...
*/
(function () {
    var f = function () {};
    if (!window.console) {
        window.console = {
            log:f, info:f, warn:f, debug:f, error:f
        };
    }
}());

/*
 * To load on run some additional js or css files.
 * (Widgets template uses this function)
 */
function loadjscssfile(filename, filetype){
   if (log_layout) console.debug("loadjscssfile: ", filename, filetype)
   if (filetype=="js") {
      if (log_layout) console.debug('Loading Js file: ', filename);
      $.ajax({
         url: filename,
         dataType: "script",
         error: function () {
            console.error('Shinken script error, not loaded: ', filename);
         }
      });
   } else if (filetype=="css") {
      if (log_layout) console.debug('Loading Css file: ', filename);
       if (!$('link[href="' + filename + '"]').length)
           $('head').append('<link rel="stylesheet" type="text/css" href="' + filename + '">');
   }
}


/**
 *  Menu related code
 */
function set_current_page(url){
   if (log_layout) console.debug('Set current page', url);

   $('a[href="'+url+'"]').parent().addClass('active');
}


/**
 * Display the layout modal form
 */
function display_modal(inner_url, hidden) {
   var show = true;
   if (hidden !== undefined) {
      show = false;
   }

   if (log_layout) console.debug('Display modal: ', inner_url, show);
   // stop_refresh();
   $('#mainModal').modal({
      backdrop: true,
      keyboard: true,
      show: show,
      // remote: inner_url
   });

   $("#mainModal .modal-content").load(inner_url);
}


$(document).ready(function(){
/* For a future version ... control navigation bar navigation.
   // Manage navigation bars selection ...
   $('body').on("click", '.nav a', function (evt) {
      if (log_layout) console.debug('Selected a navigation bar element', $(this));

      // Do not automatically navigate...
      evt.preventDefault();

      if (log_layout) console.debug('Request navigation to', $(this).attr('href'));

      $(".nav").find(".active").removeClass("active");
      $(this).parent().addClass("active");
      $(this).css({'color':'red'});
   });
*/

   // Activate all tooltips on the page ...
   if (log_layout) console.debug('Activate tooltips');
   $('[data-toggle="tooltip"]').tooltip();

   // When modal box is displayed ...
   $('#mainModal').on('shown.bs.modal', function () {
      if (log_layout) console.debug('Modal shown');
   });

   // When modal box content is loaded ...
   $('#mainModal').on('loaded.bs.modal', function () {
      if (log_layout) console.debug('Modal content loaded');
   });

   // When modal box is hidden ...
   $('#mainModal').on('hidden.bs.modal', function () {
      if (log_layout) console.debug('Modal hidden');

      // Clean modal box content ...
      $(this).removeData('bs.modal');

      // Page refresh required
      refresh_required = true;
   });
});
