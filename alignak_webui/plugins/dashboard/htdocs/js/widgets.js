/**
* Copyright (C) 2015-2016 F. Mohier pour IPM France:
*
**/


var widgets_logs=false;
var widgets_error_remove=false;

// where we stock all current widgets loaded, and their options
var widgets = [];

var id_widget = 0;
var nb_widgets_loading = 0;
var new_widget = false;

// Now try to load widgets in a dynamic way
function AddWidget(url, options, placeId, replace){
   if (replace === undefined) {
      replace = false;
   }
   if (widgets_logs) console.debug('Loading widget: ', url, options, placeId, replace);

   var widgetId = '';
   var parameters = url.split('&');
   for (var i = 0; i < parameters.length; i++) {
      var sParameterName = parameters[i].split('=');
      if (sParameterName[0] == "wid") {
         widgetId = sParameterName[1];
      }
   }
   if (options) {
      widgetId = options['wid'];
   }

   // We are saying to the user that we are loading a widget with
   // a spinner
   nb_widgets_loading += 1;
   // Loading indicator ...
   $("#widgets_loading").html('<i class="fa fa-spinner fa-spin fa-3x"></i> <span class="lead">Loading widgets ... </span>').show();

   // We also hide the widgets proposal area ...
   $('#propose-widgets').hide();

   //If we replace the widget like in reload,
   //the container already exists and is passed as a parameter.
   if (replace == true) {
      container_object = placeId;
   } else {
      // We create a container before the AJAX request to display the widgets in the right order.
      id_widget += 1;
      container_object = $('<div id="widget-cell-' + id_widget + '"></div>').appendTo('#' + placeId);
   }

   $.ajax({
      url: url,
      data: options,
      method: "GET",
      context: container_object
   })
   .done(function(data, textStatus, jqXHR) {
      if (widgets_logs) console.debug('Widget loaded: ', url, options);
      $.fn.AddEasyWidget(data, this.attr('id'), {});
   })
   .fail(function(jqXHR, textStatus, errorThrown) {
      if (widgets_logs) console.debug('Widget loading error: ', textStatus, errorThrown, jqXHR);
      $(this).html('Error loading this widget: ', url, options);
      if (widgets_error_remove) {
         $('#' + widgetId).remove();
         saveWidgets();
      }
   })
   .always(function() {
      nb_widgets_loading -= 1;
      // Maybe we are the last widget to load, if so,
      // remove the spinner
      if (nb_widgets_loading==0){
         $('#widgets_loading').hide();
      }
   });
}

// when we add a new widget, we also save the current widgets
// configuration for this user
function AddNewWidget(url, options, placeId){
   if (widgets_logs) console.debug("Adding a new widget: ", placeId, url, options);

   AddWidget(url, options, placeId);
   new_widget = true;
}

// Reload only widget
function reloadWidget(name){
   if (widgets_logs) console.debug("Reloading a widget: ", name);

   var widget = search_widget(name);
   if (widget == -1) {
      if (widgets_logs) console.error("Widget not found: ", name);
      return;
   }

   // Update widget options for reloading
   widget.options['wid'] = widget.id;
   widget.options['collapsed'] = widget.collapsed ? "True": "False";

   container = $('#' + widget.id).parent();

   // Do not delete the container to keep the correct widget order.
   $('#' + widget.id).remove();

   AddWidget(widget.base_url, widget.options, container, true);
}

function search_widget(name){
   if (widgets_logs) console.debug("Searching a widget: ", name);

   res = -1;
   w = $.each(widgets, function(idx, w){
      if (name == w.id){
         res = w;
      }
   });

   return res;
}

// We will look if we need to save the current state and options or not
function saveWidgets(callback){
   if (widgets_logs) console.debug("Saving all widgets ...");

   // First we reupdate the widget-position, to be sure the js objects got the good value
   var pos = $.fn.GetEasyWidgetPositions();
   update_widgets_positions(pos);

   var widgets_ids = [];
   $('.widget').each(function(idx, w){
      // If the widget is closed, don't save it
      if ($(this).data('deleted') === 1) {
         return;
      }

      var widget = search_widget(w.id);
      // Find the widget and check if it was not closed
      // RMQ : widget_context came from a global value set by the page.
      if (widget != -1){
         var o = {'id' : widget.id, 'position' : widget.position, 'base_url' : widget.base_url, 'options' : widget.options, 'collapsed' : widget.collapsed, 'for' : widget_context};
         if (widgets_logs) console.debug('Saving: ', JSON.stringify(widget));
         widgets_ids.push(o);
      }
   });

   if (widgets_logs) console.debug("Saving user preference: ", widgets_ids);
   save_user_preference('widgets', JSON.stringify(widgets_ids), callback);
   // save_user_preference('widgets', widgets_ids, callback);
}

// Function that will look at the current state of the positions,
// and will update the widgets objects from it.
function update_widgets_positions(positions){
   if($.trim(positions) != ''){
      // Get the widgets places IDs and widgets IDs
      var places = positions.split('|');
      // console.log('Places: '+places);
      for(var i = 0; i < places.length; i++){
         // Every part contain a place ID and possible widgets IDs
         var place = places[i].split('=');
         // Validate (more or less) the format of the part that must
         // contain two element: A place ID and one or more widgets IDs
         if (place.length == 2){
            // Subpart one: the place ID
            var place_name = place[0];
            // Subpart two: one or more widgets IDs
            var widgets_list = place[1].split(',');
            // Here we have a place and one or more widgets IDs
            for (var j = 0; j < widgets_list.length; j++){
               if ($.trim(widgets_list[j]) != ''){
                  // So, append every widget in the appropiate place
                  var w = search_widget(widgets_list[j]);
                  if(w != -1){
                     // We finally save the new position
                     w.position = place_name;
                  }
               }
            }
         }
      }
    }
}

$(function(){
   // We hide the loader spinner thing
   $('#widgets_loading').hide()

   // Very basic usage
   var easy_widget_mgr = $.fn.EasyWidgets({
      i18n : {
            editText : '<i class="fa fa-edit font-grey"></i>',
            closeText : '<i class="fa fa-trash-o font-grey"></i>',
            collapseText : '<i class="fa fa-chevron-up font-grey"></i>',
            cancelEditText : '<i class="fa fa-edit font-grey"></i>',
            extendText : '<i class="fa fa-chevron-down font-grey"></i>'
      },
      effects : {
            effectDuration : 100,
            widgetShow : 'slide',
            widgetHide : 'slide',
            widgetClose : 'slide',
            widgetExtend : 'slide',
            widgetCollapse : 'slide',
            widgetOpenEdit : 'slide',
            widgetCloseEdit : 'slide',
            widgetCancelEdit : 'slide'
      },
      callbacks : {
         onCollapse : function(link, widget){
            if (widgets_logs) console.debug("Collapse widget: ", widget);

            var w = search_widget(widget.attr('id'));
            if (w != -1){
               w.collapsed = true;
               saveWidgets();
            }
         },
         onExtend : function(link, widget){
            if (widgets_logs) console.debug("Extend widget: ", widget);

            var w = search_widget(widget.attr('id'));
            if (w != -1){
               w.collapsed = false;
               saveWidgets();
            }
         },
         onClose : function(link, widget){
            if (widgets_logs) console.debug("Close widget: ", widget);

            // On close, save all
            saveWidgets();

            // If we have no more widget, ...
            if (widgets.length == 1){
               // ... so we display the widgets proposal area.
               $('#propose-widgets').show();
            }
         },
         onChangePositions : function(positions){
            if (widgets_logs) console.debug("Changed widgets position");

            saveWidgets();
         },
         onEditQuery : function(link, widget){
            if (widgets_logs) console.debug("Edit widget: ", widget);

            // Stop page refresh
            // stop_refresh();
            return true;
         },
         onCancelEditQuery : function(link, widget){
            if (widgets_logs) console.debug("Cancelled widget edition: ", widget);

            // Start page refresh
            // start_refresh();
            return true;
         }
      }
   });
});
