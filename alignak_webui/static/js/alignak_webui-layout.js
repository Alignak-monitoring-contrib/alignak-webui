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
      $('#sound_alerting').removeClass('disabled text-warning');
   }
}

/*
 * To load on run some additional js or css files.
 * (Widgets template uses this function)
 * ---
 * The nocache parameter allows to force the reloading of a file. It appends a random
 * element to the url, thus forcing the browser to reload the url.
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

jQuery.cachedScript = function( url, options ) {
    // Allow user to set any option except for dataType, cache, and url
    options = $.extend( options || {}, {
        dataType: "script",
        cache: true,
        url: url
    });

    // Use $.ajax() since it is more flexible than $.getScript
    // Return the jqXHR object so we can chain callbacks
    return jQuery.ajax( options );
};
$.extend({
   getJsFiles: function(urls, callback, nocache){
      if (typeof nocache=='undefined') nocache=false; // default don't refresh
      $.when(
         $.each(urls, function(i, url){
            if (! $('link[href="' + url + '"]').length) {
               if (nocache) {
                  $.getScript(url)
                  .done(function(data, textStatus, jqxhr) {
                     //console.log("'Loaded:", url, textStatus)
                  });
               } else {
                  $.cachedScript(url)
                  .done(function(data, textStatus, jqxhr) {
                     //console.log("'Loaded:", url, textStatus)
                  });
               }
            } else {
                console.warning("Script is already included: "+url)
            }
         })
      ).then(function(){
         if (typeof callback=='function') {
            callback();
         }
      });
   },
});


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
 * - if the parameter size is present, the modal dialog is shown in the large or small mode
 * according to the parameter value (large, small or normal (default))
 * - if the hidden parameter is present the
 */
function display_modal(inner_url, size, hidden) {
   var show = true;
   if (hidden !== undefined) {
      show = false;
   }

   window.setTimeout(function() {
      if (log_layout) console.debug('Display modal, loading...', inner_url, show);

       if ((size !== undefined) && (size == 'large')) {
          $("#mainModal .modal-dialog").addClass('modal-lg');
       } else if ((size !== undefined) && (size == 'small')) {
          $("#mainModal .modal-dialog").addClass('modal-sm');
       } else {
          $("#mainModal .modal-dialog").removeClass('modal-lg').removeClass('modal-sm');
       }

      $("#mainModal").find('.modal-content').load(inner_url, function() {
         $('#mainModal').modal({
             backdrop: true,
             keyboard: true,
             show: show
         });
         if (log_layout) console.debug('Display modal, loaded');
      });
   }, 10);
}


// Automatically navigate to the desired tab if an # exists in the URL
function bootstrap_tab_bookmark(selector) {
    if (selector == undefined) {
        selector = "";
    }

    var bookmark_switch = function () {
        url = document.location.href.split('#');
        if (url[1] != undefined) {
            $(selector + '[href="#'+url[1]+'"]').tab('show');
        }
    }

    /* Automatically jump on good tab based on anchor */
    $(document).ready(bookmark_switch);
    $(window).bind('hashchange', bookmark_switch);

    var update_location = function (event) {
        document.location.hash = this.getAttribute("href");
    }

    /* Update hash based on tab */
    $(selector + "[data-toggle=pill]").click(update_location);
    $(selector + "[data-toggle=tab]").click(update_location);
}

$(document).ready(function() {
   // Activate all tooltips on the page ...
   if (window.matchMedia && (window.matchMedia("(min-width: 768px)").matches)) {
      if (log_layout) console.debug('Activate tooltips');
      // ... except when on small devices!
      $('[data-toggle="tooltip"]').tooltip();
   }

   // When modal box is displayed...
   $('#mainModal').on('shown.bs.modal', function () {
      if (log_layout) console.debug('Modal shown');
         // Pause the page refresh
         refresh_pause();
   });

   // When modal box is hidden...
   $('#mainModal').on('hidden.bs.modal', function () {
      if (log_layout) console.debug('Modal hidden');
         // Un-pause the page refresh
         refresh_play();
   });
});
