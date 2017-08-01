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

var actions_logs=false;
var refresh_delay_after_action=1000;
var alert_info_delay=2;
var alert_success_delay=3;
var alert_warning_delay=5;
var alert_error_delay=10;

/**
 * Get current user preference value:
 * - key
 * - callback function called after data are posted
 * - default_value to use if user preference does not exist
**/
function get_user_preference(key, callback, default_value) {
   if (actions_logs) console.debug('Get user preference: ', key);

   $.ajax({
      url: '/preference/user',
      dataType: "json",
      method: "GET",
      data: {
         'key' : key,
         'default': JSON.stringify(default_value)
      }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('Get user preference: ', key, data);

      if (typeof callback !== 'undefined' && $.isFunction(callback)) {
         if (actions_logs) console.debug('Calling callback function ...', data);
         callback(data);
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      console.error('get_user_preference, error: ', jqXHR, textStatus, errorThrown);
      raise_message_ko(errorThrown + ': '+ textStatus);
   });
}

/**
 * Save current user preference value:
 * - key / value
 * - callback function called after data are posted
**/
function save_user_preference(key, value, callback) {
   if (actions_logs) console.debug('Save user preference: ', key, value);

   $.ajax({
      url: '/preference/user',
      dataType: "json",
      method: "POST",
      data: { 'key' : key, 'value' : value }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('User preference saved: ', key, value);

      if (typeof callback !== 'undefined' && $.isFunction(callback)) {
         if (actions_logs) console.debug('Calling callback function ...');
         callback(value);
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      console.error('save_user_preference, error: ', jqXHR, textStatus, errorThrown);
      raise_message_ko(save_user_preference + ': '+ textStatus);
   });
}

/**
 * Delete a user preference:
 * - key
 * - callback function called after data are posted
**/
function delete_user_preference(key, callback) {
   if (actions_logs) console.debug('Delete user preference: ', key);

   $.ajax({
      url: '/preference/user/delete',
      dataType: "json",
      method: "GET",
      data: {
         'key' : key
      }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('Deleted user preference: ', key, data);

      if (typeof callback !== 'undefined' && $.isFunction(callback)) {
         if (actions_logs) console.debug('Calling callback function ...', data);
         callback(data);
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      console.error('delete_user_preference, error: ', jqXHR, textStatus, errorThrown);
      raise_message_ko(errorThrown + ': '+ textStatus);
   });
}

/**
 * Save common preference value
 * - key / value
 * - callback function called after data are posted
**/
function save_common_preference(key, value, callback) {
   if (actions_logs) console.debug('Save common preference: ', key, value);

   $.ajax({
      url: '/common/preference',
      dataType: "json",
      method: "POST",
      data: { 'key' : key, 'value' : value }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('Common preference saved: ', key, value);

      if (typeof callback !== 'undefined' && $.isFunction(callback)) {
         if (actions_logs) console.debug('Calling callback function ...');
         callback(JSON.parse(value));
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      console.error('save_common_preference, error: ', jqXHR, textStatus, errorThrown);
      raise_message_ko(save_user_preference + ': '+ textStatus);
   });
}

/*
 * Waiting box part
 */
function wait_message(text, show) {
    $('#waitingModal').find('.modal-title').text(text);
    if (show) {
        refresh_suspended = true;
        $('#waitingModal').modal('show');
    } else {
        $('#waitingModal').modal('hide');
        refresh_suspended = false;
    }
}

/*
 * Message raise part
 */
function raise_message_info(text){
    alertify.message(text, alert_info_delay, function(){
        console.log('Info:', text);
    });
}

function raise_message_ok(text){
    alertify.success(text, alert_success_delay, function(){
        console.log('Success:', text);
    });
}

function raise_message_warning(text){
    alertify.warning(text, alert_warning_delay, function(){
        console.log('Warning:', text);
    });
}

function raise_message_ko(text){
    alertify.error(text, alert_error_delay, function(){
        console.log('Error:', text);
    });
}


/*
 * Overload jQuery serialize to include checkboxes
 */
(function ($) {

     $.fn.serialize = function (options) {
         return $.param(this.serializeArray(options));
     };

     $.fn.serializeArray = function (options) {
         var o = $.extend({
         checkboxesAsBools: true
     }, options || {});

     var rselectTextarea = /select|textarea/i;
     var rinput = /text|number|email|color|date|datetime|datetime-local|month|range|tel|time|url|week|hidden|password|search/i;

     return this.map(function () {
         return this.elements ? $.makeArray(this.elements) : this;
     })
     .filter(function () {
         return this.name && !this.disabled &&
             (this.checked
             || (o.checkboxesAsBools && this.type === 'checkbox')
             || rselectTextarea.test(this.nodeName)
             || rinput.test(this.type));
         })
         .map(function (i, elem) {
             var val = $(this).val();
             console.log(i, elem, val);
             return val == null ?
             {
                 name: elem.name,
                 value: val
             } :
             $.isArray(val) ?
             $.map(val, function (val, i) {
                 return { name: elem.name, value: val };
             }) :
             {
                 name: elem.name,
                 value: (o.checkboxesAsBools && this.type === 'checkbox') ? //moar ternaries!
                        (this.checked ? 'true' : 'false') :
                        val
             };
         }).get();
     };

})(jQuery);


$(document).ready(function() {
   /*
    * This event handler catches all the submit events for forms that are declared with a
    * data-item attribute.
    */
   $('body').on("submit", 'form[data-item]', function (evt) {
      if (actions_logs) console.debug('Submit form data: ', $(this));
      if (actions_logs) console.debug('Form item/action: ', $(this).data("item"), $(this).data("action"));
      if (actions_logs) console.debug('Form fields: ', $(this).serialize({ checkboxesAsBools: true }));

      // Do not automatically submit ...
      evt.preventDefault();
      if ($(this).data("item")=='document' && $(this).data("action")=='add') {
         if (actions_logs) console.debug('Do not care about document add!');
         return;
      }

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize({ checkboxesAsBools: true })
      })
      .done(function( data, textStatus, jqXHR ) {
         if (actions_logs) console.debug('Submit form result: ', data, textStatus);
         if (jqXHR.status != 200) {
            raise_message_ko(data.message);
         } else {
            raise_message_ok(data.message)
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         raise_message_ko(jqXHR.responseJSON['message']);
      })
     .always(function() {
         window.setTimeout(function() {
            // Hide modal popup
            $('#mainModal').modal('hide');

            // Page refresh required
            refresh_required = true;
         }, refresh_delay_after_action);
      });
   });


   /*
    * Application actions
    */
   // Show application help search box
   $('body').on("click", '[data-action="search-box"]', function () {
      if (actions_logs) console.debug("Help search box")
      display_modal("/modal/search_help", "large");
   });


   /*
    * UI actions
    */
   // Save collapsible state
   $('body').on("click", '[data-action="save-panel"]', function () {
      if (actions_logs) console.debug("Save preferences for a panel")
      var id = $(this).data("target");
      id = id.substring(1, id.length);
      var panel_data = {
        "opened": $(this).hasClass("collapsed")
      };
      console.log(panel_data)
      save_user_preference(id, JSON.stringify(panel_data), function () {
         refresh_bookmarks(search_string);
      });
   });


   /*
    * Dashboard widgets management
    */
   // Add a widget
   $('body').on("click", '[data-action="add-widget"]', function () {
      var widget = {
         id: $(this).data('widget-id') + '_' + Date.now(),
         name: $(this).data('widget-name'),
         template: $(this).data('widget-template'),
         icon: $(this).data('widget-icon'),
         picture: $(this).data('widget-picture'),
         options: $(this).data('widget-options'),
         uri: $(this).data('widget-uri')
      };

      var first=true;
      var options='';
      $.each(widget.options, function(key, value) {
         if (first) {
            widget.uri += '?'; first = false;
         } else {
            widget.uri += '&';
            options += '|';
         }
         widget.uri += key + '=' + value['value'];
         options += key + '=' + value['value'];
      });
      if (actions_logs) console.debug("Adding a widget: ", widget);

      // Get widgets grid...
      grid = $('.grid-stack').data('gridstack');
      // ... and add a widget to the grid
      var added_widget = grid.addWidget(
         $('<div id="'+widget.id+
            '" data-name="'+widget.name+
            '" data-template="'+widget.template+
            '" data-icon="'+widget.icon+
            '" data-picture="'+widget.picture+
            '" data-options="'+options+
            '" data-uri="'+widget.uri+
            '" class="grid-stack-item-content" />'),
         0, 0, 6, 6,       // x, y, width, height
         true,             // autoPosition
         3, 12, 2, 64,     // minWidth, maxWidth, minHeight, maxHeight
         widget.id
      );
      if (actions_logs) console.debug("Added a widget:", added_widget);

      window.setTimeout(function() {
         // Hide modal popup
         $('#mainModal').modal('hide');

         // Page refresh required
         refresh_required = true;
      }, refresh_delay_after_action);
   });

   $('body').on("click", '.dashboard-widget', function () {
      if (actions_logs) console.debug("Show form to display a widget")
      // Display modal dialog box
      $('#mainModal .modal-title').html($(this).data('widget-title'));
      $('#mainModal .modal-body').html($(this).data('widget-description'));
      $('#mainModal').modal({
         keyboard: true,
         show: true,
         backdrop: 'static'
      });
   });


   /*
    * Users management
    */
   // Add a user
   $('body').on("click", '[data-action="add-user"]', function () {
      console.log("test");
      if (actions_logs) console.debug("Add a new user")
      display_modal("/user/form/add");
   });

   // Delete a user
   $('body').on("click", '[data-action="delete-user"]', function () {
      var elt = $(this).data('element');
      if (actions_logs) console.debug("Delete a user", elt)
      if (elt) {
         display_modal("/user/form/delete?user_id="+encodeURIComponent(elt));
      }
   });

   // Delete a user preference
   $('body').on("click", '[data-action="delete-user-preference"]', function () {
      var elt = $(this).data('element');
      var message = $(this).data('message');
      if (actions_logs) console.debug("Delete a user preference", elt)
      if (elt) {
         delete_user_preference(encodeURIComponent(elt), function() {
            raise_message_ok(message);
            window.location.reload(true);
         });
      }
   });

   // Change a user password
   $('body').on("click", '[data-action="change-user-password"]', function () {
      if (actions_logs) console.debug("Required a password change for:", $(this).data('element'));

      var elt_id = $(this).data('element');
      var elt_name = $(this).data('name');
      var elt_type = $(this).data('element_type');
      var url = "/password_change_request?elements_type="+encodeURIComponent(elt_type)+"&element_id="+encodeURIComponent(elt_id)+'&element_name='+encodeURIComponent(elt_name);
      window.setTimeout(function(){
         display_modal(url);
      }, 5);
   });


   /*
    * Livestate actions
    */
   // Acknowledge
   $('body').on("click", '[data-action="acknowledge"]', function () {
      if (actions_logs) console.debug("Required an acknowledge for:", $(this).data('element'));

      var elt_id = $(this).data('element');
      var elt_name = $(this).data('name');
      var elt_type = $(this).data('element_type');
      var url = "/acknowledge/form/add?elements_type="+encodeURIComponent(elt_type)+"&element_id="+encodeURIComponent(elt_id)+'&element_name='+encodeURIComponent(elt_name);
      window.setTimeout(function(){
         display_modal(url);
      }, 5);
   });
   // Recheck
   $('body').on("click", '[data-action="recheck"]', function () {
      if (actions_logs) console.debug("Required a recheck for:", $(this).data('element'));

      var elt_id = $(this).data('element');
      var elt_name = $(this).data('name');
      var elt_type = $(this).data('element_type');
      var url = "/recheck/form/add?elements_type="+encodeURIComponent(elt_type)+"&element_id="+encodeURIComponent(elt_id)+'&element_name='+encodeURIComponent(elt_name);
      window.setTimeout(function(){
         display_modal(url);
      }, 5);
   });
   // Downtime
   $('body').on("click", '[data-action="downtime"]', function () {
      if (actions_logs) console.debug("Required a downtime for:", $(this).data('element'));

      var elt_id = $(this).data('element');
      var elt_name = $(this).data('name');
      var elt_type = $(this).data('element_type');
      var url = "/downtime/form/add?elements_type="+encodeURIComponent(elt_type)+"&element_id="+encodeURIComponent(elt_id)+'&element_name='+encodeURIComponent(elt_name);
      window.setTimeout(function(){
         display_modal(url);
      }, 5);
   });
   // Commands list
   $('body').on("click", '[data-action="global-commands-list"]', function () {
      if (actions_logs) console.debug("Requires the global commands list");

      var url = "/command/global/add";
      window.setTimeout(function(){
         display_modal(url);
      }, 5);
   });
   $('body').on("click", '[data-action="commands-list"]', function () {
      if (actions_logs) console.debug("Requires the commands list for:", $(this).data('element'));

      var elt_id = $(this).data('element');
      var elt_name = $(this).data('name');
      var elt_type = $(this).data('element_type');
      var url = "/command/form/add?elements_type="+encodeURIComponent(elt_type)+"&element_id="+encodeURIComponent(elt_id)+'&element_name='+encodeURIComponent(elt_name);
      window.setTimeout(function(){
         display_modal(url);
      }, 5);
   });
   // Command
   $('body').on("click", '[data-action="command"]', function () {
      if (actions_logs) console.debug("Required a command for:", $(this).data('element'));

      data = {
         //"timestamp": {{int(time.time())}},
         "command": $(this).data('command'),
         "elements_type": $(this).data('type'),
         "element_id": $(this).data('element'),
         "element": $(this).data('name')
      }

      $.ajax({
         url: '/command/add',
         dataType: "json",
         method: "POST",
         data: data
      })
      .done(function( data, textStatus, jqXHR ) {
         if (data.status == "ok") {
            raise_message_ok(data.message);
         } else {
            raise_message_ko(data.message);
         }

         window.setTimeout(function() {
            // Page refresh required
            refresh_required = true;
         }, refresh_delay_after_action);
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         console.error(errorThrown);
         raise_message_ko(textStatus);
      });
   });
});
