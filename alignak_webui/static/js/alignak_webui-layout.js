/*
 * Copyright (c) 2015-2017:
 *   Frederic Mohier, frederic.mohier@alignak.net
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
      'background': '#1b7942',
      'label': 'Up'
   },
   'unreachable': {
      'color': '#9b59b6',
      'background': '#6d3e7f',
      'label': 'Unreachable'
   },
   'down': {
      'color': '#e74c3c',
      'background': '#a1352a',
      'label': 'Down'
   },
   'unknown': {
      'color': '#2980b9',
      'background': '#1c5981',
      'label': 'Unknown'
   },
   'acknowledged': {
      'color': '#f39c12',
      'background': '#aa6d0c',
      'label': 'Acknowledged'
   },
   'in_downtime': {
      'color': '#f1c40f',
      'background': '#a8890a',
      'label': 'Downtime'
   }
};
var g_services_states = {
   'ok': {
      'color': '#27ae60',
      'background': '#1b7942',
      'label': 'Ok'
   },
   'warning': {
      'color': '#e67e22',
      'background': '#a15817',
      'label': 'Warning'
   },
   'critical': {
      'color': '#e74c3c',
      'background': '#a1352a',
      'label': 'Critical'
   },
   'unknown': {
      'color': '#2980b9',
      'background': '#1c5981',
      'label': 'Unknown'
   },
   'unreachable': {
      'color': '#9b59b6',
      'background': '#6d3e7f',
      'label': 'Unreachable'
   },
   'acknowledged': {
      'color': '#f39c12',
      'background': '#aa6d0c',
      'label': 'Acknowledged'
   },
   'in_downtime': {
      'color': '#f1c40f',
      'background': '#a8890a',
      'label': 'Downtime'
   }
};
var g_hoverBackgroundColor = "#669999";
var g_hoverBorderColor = "#669999";

/*
 * Play alerting sound ...
 */
function playAlertSound() {
   var audio = document.getElementById('alert-sound');
   var canPlay = audio && !!audio.canPlayType && audio.canPlayType('audio/wav') != "";
   if (canPlay) {
      audio.play();
      sessionStorage.setItem("sound_play", "1");
      //$('#sound_alerting i.fa-ban').addClass('hidden');
      $('#sound_alerting').removeClass('disabled text-muted');
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
            if (! $('link[href="' + url + '"]').length) {
               if (nocache) url += '?_ts=' + new Date().getTime(); // refresh?
               $.get(url, function(){
                  $('<link>', {rel:'stylesheet', type:'text/css', 'href':url}).appendTo('head');
               });
            }
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
 * - load its content from the inner_url parameter
 */
function display_modal(inner_url, hidden) {
   var show = true;
   if (hidden !== undefined) {
      show = false;
   }

   window.setTimeout(function() {
      if (log_layout) console.debug('Display modal, loading...', inner_url, show);

      $("#mainModal").find('.modal-content').load(inner_url, function() {
          stop_refresh();
          $('#mainModal').modal({
             backdrop: true,
             keyboard: true,
             show: show
          });
         if (log_layout) console.debug('Display modal, loaded');
      });
   }, 10);
}


$(document).ready(function(){
   // Activate all tooltips on the page ...
   if (window.matchMedia && (window.matchMedia("(min-width: 768px)").matches)) {
      if (log_layout) console.debug('Activate tooltips');
      // ... except when on small devices!
      $('[data-toggle="tooltip"]').tooltip();
   }

   // When modal box is displayed...
   $('#mainModal').on('shown.bs.modal', function () {
      if (log_layout) console.debug('Modal shown');
   });

   // When modal box is hidden...
   $('#mainModal').on('hidden.bs.modal', function () {
      if (log_layout) console.debug('Modal hidden');

      /*
      // Clean modal box content ...
      $(this).removeData('bs.modal');

      // Page refresh required
      refresh_required = true;
      */
   });
});
