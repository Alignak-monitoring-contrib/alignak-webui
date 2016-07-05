/*
 * Copyright (c) 2015-2016:
 *   Frederic Mohier, frederic.mohier@gmail.com
 *
 * This file is part of (WebUI).
 *
 * (WebUI) is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * (WebUI) is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with (WebUI).  If not, see <http://www.gnu.org/licenses/>.
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
 * Global variables for host/service states
 */
var g_hosts_states = {
   'up': {
      'color': '#27ae60',
      'label': 'Up'
   },
   'unreachable': {
      'color': '#e67e22',
      'label': 'Unreachable'
   },
   'down': {
      'color': '#e74c3c',
      'label': 'Down'
   },
   'unknown': {
      'color': '#2980b9',
      'label': 'Unknown'
   },
   'acknowledged': {
      'color': '#95a5a6',
      'label': 'Ack'
   },
   'in_downtime': {
      'color': '#9b59b6',
      'label': 'Downtime'
   }
};
var g_services_states = {
   'ok': {
      'color': '#27ae60',
      'label': 'Ok'
   },
   'warning': {
      'color': '#e67e22',
      'label': 'Warning'
   },
   'critical': {
      'color': '#e74c3c',
      'label': 'Critical'
   },
   'unknown': {
      'color': '#2980b9',
      'label': 'Unknown'
   },
   'acknowledged': {
      'color': '#95a5a6',
      'label': 'Ack'
   },
   'in_downtime': {
      'color': '#9b59b6',
      'label': 'Downtime'
   }
};
var g_hoverBackgroundColor = "rgba(255,99,132,0.4)";
var g_hoverBorderColor = "rgba(255,99,132,1)";

/*
 * Play alerting sound ...
 */
function playAlertSound() {
   var audio = document.getElementById('alert-sound');
   var canPlay = audio && !!audio.canPlayType && audio.canPlayType('audio/wav') != "";
   if (canPlay) {
      audio.play();
      sessionStorage.setItem("sound_play", "1");
      $('#sound_alerting i.fa-ban').addClass('hidden');
   }
}

/*
 * To load on run some additional js or css files.
 * (Widgets template uses this function)
 */
$.extend({
   getCssFiles: function(urls, callback, nocache){
      if (typeof nocache=='undefined') nocache=false; // default don't refresh
      $.when(
         $.each(urls, function(i, url){
            if (nocache) url += '?_ts=' + new Date().getTime(); // refresh?
            $.get(url, function(){
               $('<link>', {rel:'stylesheet', type:'text/css', 'href':url}).appendTo('head');
            });
         })
      ).then(function(){
         if (typeof callback=='function') callback();
      });
   },
});

function loadjscssfile(filename, filetype){
   if (log_layout) console.debug("loadjscssfile: ", filename, filetype)
   if (filetype=="js") {
      if (log_layout) console.debug('Loading Js file: ', filename);
      $.ajax({
         url: filename,
         dataType: "script",
         error: function () {
            console.error('Script loading error, not loaded: ', filename);
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

   window.setTimeout(function() {
      if (log_layout) console.debug('Display modal: ', inner_url, show);
      // stop_refresh();
      $('#mainModal').modal({
         backdrop: true,
         keyboard: true,
         show: show,
         // remote: inner_url
      });

      $("#mainModal .modal-content").load(inner_url);
   }, 100);
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
