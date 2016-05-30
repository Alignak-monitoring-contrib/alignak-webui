/*
* Copyright (C) 2015-2016 F. Mohier pour IPM France:
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
function get_user_preference(key, callback) {
   if (actions_logs) console.debug('Get user preference: ', key);

   $.ajax({
      url: '/user/preference',
      dataType: "json",
      method: "GET",
      data: { 'key' : key }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('Get user preference: ', key, data);

      if (typeof callback !== 'undefined' && $.isFunction(callback)) {
         if (actions_logs) console.debug('Calling callback function ...', callback);
         callback(JSON.parse(value));
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
      url: '/user/preference',
      dataType: "json",
      method: "POST",
      data: { 'key' : key, 'value' : value }
   })
   .done(function( data, textStatus, jqXHR ) {
      if (actions_logs) console.debug('User preference saved: ', key, value);

      if (typeof callback !== 'undefined' && $.isFunction(callback)) {
         if (actions_logs) console.debug('Calling callback function ...', callback);
         callback(JSON.parse(value));
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
   $('body').on("click", '.navbar-brand', function () {
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


   /*
    * Services management
    */
   // Create a new service
   $('body').on("click", '[data-action="add-userservice"]', function () {
      if (actions_logs) console.debug("Show form to create a new service")
      display_modal("/userservice/form/add");
   });

   // Delete a service
   $('body').on("click", '[data-action="delete-userservice"]', function () {
      var elt = $(this).data('service_id');
      if (actions_logs) console.debug("Delete a service", elt)
      if (elt) {
         display_modal("/userservice/form/delete?userservice_id="+encodeURIComponent(elt));
      }
   });

   // Link / unlink to a user
   $('body').on("click", '[data-action="link-userservice-user"]', function () {
      var user = $(this).data('user_id');
      var svc = $(this).data('service_id');
      if (actions_logs) console.debug("Link a service to a user", user, svc)
      if (user && svc) {
         $.ajax({
            url: "/userservice_user/link",
            type: "POST",
            data: {
               "user_id": encodeURIComponent(user),
               "service_id": encodeURIComponent(svc)
            }
         })
         .done(function( data, textStatus, jqXHR ) {
            if (jqXHR.status != 200) {
               raise_message_ko(data['message']);
            } else {
               raise_message_ok(data['message'])
            }
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            raise_message_ko(jqXHR.responseJSON['message']);
         });
      }
   });
   $('body').on("click", '[data-action="unlink-userservice-user"]', function () {
      var relation_id = $(this).data('relation_id');
      if (actions_logs) console.debug("Unlink a service and a user", relation_id)
      if (relation_id) {
         $.ajax({
            url: "/userservice_user/unlink",
            type: "POST",
            data: {
               "userservice_user_id": encodeURIComponent(relation_id)
            }
         })
         .done(function( data, textStatus, jqXHR ) {
            if (jqXHR.status != 200) {
               raise_message_ko(data['message']);
            } else {
               raise_message_ok(data['message'])
            }
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            raise_message_ko(jqXHR.responseJSON['message']);
         });
      }
   });


   /*
    * Sessions management
    */
   // Open a session
   $('body').on("click", '[data-action="open-session"]', function () {
      var elt = $(this).data('element');
      var svc = $(this).data('service');
      if (actions_logs) console.debug("Open a new session", elt, svc)
      if (elt && svc) {
         display_modal("/userservice_session/form/open?session_id="+encodeURIComponent(elt)+'&service_name='+encodeURIComponent(svc)+'&read_only=1&auto_post=1');
      }
   });

   // Join a session
   $('body').on("click", '[data-action="join-session"]', function () {
      var elt = $(this).data('element');
      var svc = $(this).data('service');
      if (actions_logs) console.debug("Join a session", elt, svc)
      if (elt && svc) {
         $.ajax({
            url: "/userservice_session/join",
            type: "POST",
            data: {
               "session_id": elt,
               "service_name": svc
            }
         })
         .done(function( data, textStatus, jqXHR ) {
            if (jqXHR.status != 200) {
               raise_message_ko(data['message']);
            } else {
               raise_message_ok(data['message'])
            }
            // Page refresh required
            refresh_required = true;
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            raise_message_ko(jqXHR.responseJSON['message']);
         });
      }
   });

   // Leave a session
   $('body').on("click", '[data-action="leave-session"]', function () {
      var elt = $(this).data('element');
      var svc = $(this).data('service');
      if (actions_logs) console.debug("Leave a session", elt, svc)
      if (elt) {
         $.ajax({
            url: "/userservice_session/leave",
            type: "POST",
            data: {
               "session_id": elt,
               "service_name": svc
            }
         })
         .done(function( data, textStatus, jqXHR ) {
            if (jqXHR.status != 200) {
               raise_message_ko(data['message']);
            } else {
               raise_message_ok(data['message'])
            }
            // Page refresh required
            refresh_required = true;
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            raise_message_ko(jqXHR.responseJSON['message']);
         });
      }
   });

   // Close a session
   $('body').on("click", '[data-action="close-session"]', function () {
      var elt = $(this).data('element');
      var svc = $(this).data('service');
      if (actions_logs) console.debug("Close the session: ", elt, svc)
      if (elt) {
         display_modal("/userservice_session/form/close?session_id="+encodeURIComponent(elt)+'&service_name='+encodeURIComponent(svc));
      }
   });


   /*
    * Sessions actions
    */
   // Post a document ...
   $('body').on("click", '[data-action="send-document"]', function () {
      var elt = $(this).data('element');
      if (elt) {
         if (actions_logs) console.debug("Send a document for: ", elt)
         display_modal("/document/form/post?session_id="+encodeURIComponent(elt));
      }
   });

   // Post an event ... display event form.
   $('body').on("click", '[data-action="post-event"]', function () {
      var elt = $(this).data('element');
      if (elt) {
         if (actions_logs) console.debug("Show form to create an event for: ", elt)
         display_modal("/event/form/post?session_id="+encodeURIComponent(elt));
      }
   });

   // Print a document ...
   $('body').on("click", '[data-action="print-document"]', function () {
      var elt = $(this).data('element');
      var doc = $(this).data('document');
      var command = $(this).data('command');
      var message = $(this).data('message');
      if (elt && doc && command) {
         if (actions_logs) console.debug("Send a document for: ", elt, command, message)
         display_modal("/document/form/post?session_id="+encodeURIComponent(elt)+'&doc_name='+encodeURIComponent(doc)+'&evt_type='+encodeURIComponent(command)+'&evt_comment='+encodeURIComponent(message)+'&read_only=1');
      }
   });

   // Post an event ... which is a command
   $('body').on("click", '[data-action="post-command"]', function () {
      var elt = $(this).data('element');
      var command = $(this).data('command');
      var message = $(this).data('message');
      if (elt && command) {
         if (actions_logs) console.debug("Send a command for: ", elt, command, message)
         // Display modal but hidden ...
         display_modal("/event/form/post?session_id="+encodeURIComponent(elt)+'&evt_type='+encodeURIComponent(command)+'&comment='+encodeURIComponent(message)+'&read_only=1&auto_post=1', true);
      }
   });
});
