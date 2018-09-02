%# Default values
%setdefault('title', _('Untitled...'))

%from alignak_webui.utils.helper import Helper

%setdefault('widget_name', 'widget')

%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('options', None)

%setdefault('widget_id', 'widget')
%setdefault('widget_icon', 'leaf')

%# only use typeahead if not embedded
%setdefault('bloodhound', not embedded)

<div id="wd_panel_{{widget_id}}" class="panel panel-default alignak_webui_widget {{'embedded' if embedded else ''}}">
   %if title is not None:
   <div class="panel-heading clearfix">
      <span class="fa fa-{{widget_icon}}"></span>
      &nbsp;{{title}}

      %if options or not embedded:
      <div class="btn-group btn-group-xs pull-right" role="group" style="margin: 1px">
         %if options:
         <button data-widget="{{widget_id}}" data-action="widget-options" type="button" class="btn">
            <span class="fa fa-gear fa-fw"></span>
            <span class="hidden-sm">&nbsp;{{_('Options')}}&nbsp;</span>
         </button>
         %end

         %if not embedded:
         <button data-widget="{{widget_id}}" data-action="remove-widget" type="button" class="btn">
            <span class="fa fa-close fa-fw"></span>
            <span class="hidden-sm">&nbsp;{{_('Remove')}}&nbsp;</span>
         </button>
         %end
      </div>
      %end
   </div>
   %end
   <div class="panel-body">
      %include(widget_name, **locals())
   </div>

   %if options:
   <form class="hidden" role="form" data-widget="{{widget_id}}" data-action="save-options" method="post" action="{{widget_uri}}" style="font-size: 0.9em">
      <input type="hidden" name='widget_id' value='{{widget_id}}'/>
      <input type="hidden" name='widget_template' value='{{widget_template}}'/>
      <input type="hidden" name='title' value='{{title}}'/>

      %for (key, v) in options.iteritems():
         %value = v.get('value', '')
         %label = v.get('label', key)
         %type = v.get('type', 'text')

         %# """ Manage the different types of values"""
         %if type == 'hidden':
            <input type="hidden" name='{{key}}' value='{{value}}'/>
            %continue
         %end

         %if type in ['text', 'int', 'hst_srv']:
            <div class="form-group">
               <label for = "{{key}}">{{label}}</label>
               %if type == 'hst_srv' and bloodhound:
               <input type="text" class="form-control input-sm typeahead" placeholder="{{_('Search by name ...')}}" name="{{key}}" value="{{value}}">
               <script>
                  // On page loaded ...
                  $(function() {
                     // Typeahead: builds suggestion engine
                     var hosts = new Bloodhound({
                        datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
                        queryTokenizer: Bloodhound.tokenizers.whitespace,
                        remote: {
                           url: '/lookup?query=%QUERY',
                           filter: function (hosts) {
                              return $.map(hosts, function (host) { return { value: host }; });
                           }
                        }
                     });
                     hosts.initialize();

                     // Typeahead: activation
                     var typeahead = $('#input-{{widget_id}}-{{key}}').typeahead({
                        hint: true,
                        highlight: true,
                        minLength: 3
                     },
                     {
                        name: 'hosts',
                        displayKey: 'value',
                        source: hosts.ttAdapter(),
                     });

                     typeahead.on('typeahead:selected', function (eventObject, suggestionObject, suggestionDataset) {
                        $('#input-{{widget_id}}-{{key}}').val(suggestionObject.value).html(suggestionObject.value);
                        hostSubmittable = true;
                     });
                  });
               </script>
               %else:
               <input type="{{'number' if type=='int' else 'text'}}" class="form-control input-sm" placeholder="{{ value }}" name="{{key}}" value="{{value}}">
               %end
            </div>
            %continue
         %end

         %if type in ['select']:
            <div class="form-group">
               <label for = "{{key}}">{{label}}</label>
               %values = v.get('values', {})
               %value = v.get('value', '')
               <select name='{{k}}'>
               %for sub_val,sub_name in values.iteritems():
                  %selected = ''
                  %if value == sub_val:
                      %selected = 'selected'
                  %end
                  <option value="{{sub_val}}" {{selected}}>{{sub_name}}</option>
               %end
               </select>
            </div>
            %continue
         %end

         %if type == 'bool':
            %checked = ''
            %if value:
               %checked = 'checked'
            %end
            <div class="form-group">
               <label for = "{{key}}">{{label}}</label>
               <input name='{{key}}' type="checkbox" {{checked}}/>
            </div>
            %continue
         %end
      %end
   </form>
   <script>
      $('form[data-widget="{{widget_id}}"]').on("submit", function (evt) {
         // Do not automatically submit ...
         evt.preventDefault();

         $('#widgets_loading').show();

         var widget_id = $(this).data("widget");
         $.ajax({
            url: $(this).attr('action'),
            type: $(this).attr('method'),
            data: $(this).serialize()
         })
         .done(function( data, textStatus, jqXHR ) {
            if (jqXHR.status != 200) {
               console.error(jqXHR.status, data);
            } else {
               %if not embedded:
               $('#wd_panel_{{widget_id}}').remove();
               var elt = $(data).find('div.alignak_webui_widget');
               /*$('#{{widget_id}} div.grid-stack-item-content')
                  .append(elt)
                  .delay(100)
                  .slideDown('slow');*/

               $("#" + widget_id + " div.grid-stack-item-content").html(data);
               %else:
               $("#" + widget_id).hide();
               %end
            }
         })
         .fail(function( jqXHR, textStatus, errorThrown ) {
            console.error(errorThrown, textStatus);
         })
        .always(function() {
            $('#widgets_loading').hide();
         });
      });

      %if options:
      alertify.widgetDialog || alertify.dialog('widgetDialog',function(){
         return {
            main:function(content){
               this.setContent(content);
            },
            setup:function(){
               return {
                  buttons: [
                     {
                        /* button label */
                        text: '<i class="fa fa-save"></i>&nbsp;{{_('Save changes')}}',

                        /* bind a keyboard key to the button */
                        key: 13,

                        /* indicate if closing the dialog should trigger this button action */
                        invokeOnClose: false,

                        /* custom button class name */
                        className: 'btn btn-success',

                        /* custom button attributes  */
                        attrs:{
                           submit: true
                        },

                        /* Defines the button scope, either primary (default) or auxiliary */
                        scope:'primary',
                     },
                     {
                        text: '<i class="fa fa-close"></i>&nbsp;{{_('Cancel')}}',
                        key: 27,
                        invokeOnClose: true,
                        className: 'btn btn-danger',
                        scope:'auxiliary',
                     }
                  ],
                  options:{
                     maximizable:false,
                     resizable:false,
                     padding:true,
                     title:'{{_('Widget options:')}}'
                  }
               };
            },
            // This will be called each time an action button is clicked.
            callback:function(closeEvent){
               // The closeEvent has the following properties:
               // - index: The index of the button triggering the event.
               // - button: The button definition object.
               // - cancel: When set true, prevent the dialog from closing.
               if (closeEvent.button.attrs && closeEvent.button.attrs.submit) {
                  // Submit the widget options form
                  $('form[data-widget="{{widget_id}}"]').trigger('submit');
               }
            }
         };
      });
      $('button[data-widget="{{widget_id}}"][data-action="widget-options"]').on("click", function (evt) {
         // Un-hide the initially hidden form.
         $('form[data-widget="{{widget_id}}"]').removeClass('hidden');
         // Display the form dialog box
         alertify.widgetDialog ($('form[data-widget="{{widget_id}}"]')[0]);
      });
      %end

      %if not embedded:
      $('button[data-widget="{{widget_id}}"][data-action="remove-widget"]').on("click", function (evt) {
         var grid = $('.grid-stack').data('gridstack');
         grid.removeWidget('#' + $(this).data("widget"));
      });
      %end
   </script>
   %end
</div>
