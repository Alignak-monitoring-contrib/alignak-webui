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

var actions_logs=false;
var refresh_delay_after_action=1000;
var alert_success_delay=3000;
var alert_error_delay=5000;

/**
 * Get current user preference value:
 * - key
 * - callback function called after data are posted
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
      raise_message_ko(get_user_preference + ': '+ textStatus);
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
         if (actions_logs) console.debug('Calling callback function ...', callback);
         callback(value);
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      console.error('save_user_preference, error: ', jqXHR, textStatus, errorThrown);
      raise_message_ko(save_user_preference + ': '+ textStatus);
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
         if (actions_logs) console.debug('Calling callback function ...', callback);
         callback(JSON.parse(value));
      }
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      console.error('save_common_preference, error: ', jqXHR, textStatus, errorThrown);
      raise_message_ko(save_user_preference + ': '+ textStatus);
   });
}


/*
 * Message raise part
 */
function raise_message_ok(text){
   alertify.log(text, "success", alert_success_delay);
}

function raise_message_ko(text){
   alertify.log(text, "error", alert_error_delay);
}


/*
 * Launch the request
 */
function launch(url, response_message){
   if (actions_logs) console.debug('Launch external command: ', url);

   $.ajax({
      url: url,
      dataType: "jsonp",
      method: "GET",
      data: { response_text: response_message }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('Done: ', url, data, textStatus, jqXHR);
      raise_message_ok(data.text)
   })
   .fail(function( jqXHR, textStatus, errorThrown ) {
      if (actions_logs) console.error('Error: ', url, jqXHR, textStatus, errorThrown);
      raise_message_ko(textStatus);
   })
   .always(function(  ) {
      /*
      window.setTimeout(function() {
         // Refresh the current page after a short delay
         do_refresh();
      }, refresh_delay_after_action);
      */
   });
}


$(document).ready(function() {
   /*
    * This event handler catches all the submit events for forms that are declared with a
    * data-item attribute.
    */
   $('body').on("click", 'a[data-refresh="start"]', function (evt) {
      if (refresh_logs) console.debug('Close form and reactivate refresh');

      // Stop UI refresh
      start_refresh();
   });

   $('body').on("submit", 'form[data-item]', function (evt) {
      if (actions_logs) console.debug('Submit form data: ', $(this));
      if (actions_logs) console.debug('Form item/action: ', $(this).data("item"), $(this).data("action"));

      // Do not automatically submit ...
      evt.preventDefault();
      if ($(this).data("item")=='document' && $(this).data("action")=='add') {
         if (actions_logs) console.debug('Do not care about document add!');
         return;
      }

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize()
      })
      .done(function( data, textStatus, jqXHR ) {
         if (jqXHR.status != 200) {
            raise_message_ko(jqXHR.status);
         } else {
            raise_message_ok(data.status)
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
   // Navigate to home page
   $('body').on("click", '[data-action="navigate-home"]', function () {
      if (actions_logs) console.debug("Navigate home page")
      window.location.href = "/";
   });
   // Show application about box
   $('body').on("click", '[data-action="about-box"]', function () {
      if (actions_logs) console.debug("Application about")
      display_modal("/modal/about");
   });


   /*
    * Dashboard widgets management
    */
   // Add a widget
   $('body').on("click", '[data-action="add-widget"]', function () {
      if (actions_logs) console.debug("Add a widget")
      AddNewWidget($(this).data('wuri'), null, 'widget-place-1');
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
});
