%import json

%# Default values
%setdefault('debug', False)
%setdefault('edition', True)
%setdefault('title', '%s %s' % (plugin.backend_endpoint.capitalize(), element.name))

%rebase("layout", title=title, page="/{{plugin.backend_endpoint}}/form/{{element.id}}")

<div id="form_{{plugin.backend_endpoint}}">
   <form role="form"
         data-element="{{element.id}}"
         method="post" action="/{{plugin.backend_endpoint}}/form/{{element.id}}"
         style="padding: 20px;">

      <fieldset>
      <legend>{{! '%s <code>%s</code>' % (plugin.backend_endpoint.capitalize(), element.name)}}</legend>

      %for field, model in plugin.table.iteritems():
         %selectize = False
         %if not model.get('visible', True) or field[0] in ['#', '_']:
            %if debug:
            <i class="fa fa-bug"></i><strong>Ignored</strong> '{{field}}' -> {{model}} field<br>
            %end
            %continue
         %end

         %if debug:
         <i class="fa fa-bug"></i>{{field}} -> {{model}}<br>
         %end

         %field_value=element[field]
         %is_list = False
         %list_values = []

         %label = model.get('title', '')
         %field_type = model.get('type', 'string')
         %content_type = model.get('content_type', field_type)
         %placeholder = model.get('placeholder', label)
         %hint = model.get('hint', label)
         %allowed = model.get('allowed', '').split(',')
         %if allowed[0] == '':
         %  allowed = []
         %end
         %format = model.get('format')
         %format_parameters = model.get('format_parameters')
         %unique = model.get('unique')
         %required = model.get('required')
         %editable = model.get('editable', True)

         %from alignak_webui.objects.element import BackendElement

         %# Field value is a list
         %if isinstance(field_value, list):
         %  for v in field_value:
         %     if isinstance(v, BackendElement):
         %        list_values.append((v.id, v.name))
         %     elif isinstance(v, dict):
         %        for key,value in v.items():
         %           list_values.append(('%s|%s' % (key, value), '%s=%s' % (key, value)))
         %        end
         %     else:
         %        list_values.append((v, model.get("allowed_%s" % v, v)))
         %     end
         %  end
         %  is_list = True
         %  selectize=True

         %# Field value is a dict
         %elif isinstance(field_value, dict):
         %  for k,v in field_value.items():
         %     list_values.append(('%s|%s' % (k, v), '%s=%s' % (k, v)))
         %  end
         %  is_list = True
         %  selectize=True

         %# Field value is simple
         %else:
         %  if isinstance(field_value, BackendElement):
         %     list_values.append((field_value.id, field_value.name))
         %     selectize=True
         %  else:
         %     list_values.append((field_value, model.get("allowed_%s" % field_value, field_value)))
         %     if allowed:
         %        selectize=True
         %     end
         %  end
         %end

         %if debug:
            <i class="fa fa-bug"></i>
            %if is_list:
            {{'%s -> %s (%s) = %s' % (field, field_type, content_type, list_values)}}
            %else:
            {{'%s -> %s = %s' % (field, content_type, field_value)}}
            %end
            <br>
         %end

         %# Manage the different types of values
         %# ----------------------------------------------------------------------------------------
         %if field_type == 'hidden':
            <input type="hidden" name='{{name}}' value='{{value}}'/>
            %continue
         %end

         %if field_type in ['boolean']:
            <div class="form-group">
               <label class="col-md-2 control-label" for="{{field}}">{{label}}</label>
               <div class="col-md-offset-2 col-md-10">
                  <div class="checkbox">
                     <label>
                        <input id="{{field}}" name="{{field}}" type="checkbox"
                           {{'disabled="disabled"' if not edition or not editable else ''}}
                           {{'checked="checked"' if field_value else ''}}
                           >
                     </label>
                  </div>
                  %if hint:
                  <p class="help-block">
                     {{hint}}
                     %if unique:
                     <br>This field must be unique.
                     %end
                     %if required:
                     <br>This field is required.
                     %end
                  </p>
                  %end
               </div>
            </div>
            <script>
               $("#{{field}}").on("change", function() {
                 console.log("Value {{field}}:", $("#{{field}}").prop('checked'));
               })
            </script>
            %continue
         %end

         %linked_object_type = model.get('resource', '')
         %icon=''
         %if linked_object_type:
         %  from alignak_webui.objects.element_state import ElementState
         %  icon = ElementState().get_icon_state(linked_object_type, 'unknown')
         %  icon=icon['icon'] if icon else ''
         %end
         <div class="form-group">
            <label for="{{field}}" class="col-md-2 control-label">{{label}}</label>
            <div class="col-md-10">
               %if is_list:
               <div class="input-group">
                  <span class="input-group-addon"><i class="fa fa-list"></i></span>
                  <select id="{{field}}" name="{{field}}"
                         class="form-control"
                         {{'readonly="readonly"' if not edition or not editable else ''}}>
                  </select>
               </div>
               %else:
               %if format == 'textarea':
               <textarea id="{{field}}" name="{{field}}"
                  class="form-control"
                  rows="3"
                  placeholder="{{placeholder}}"
                  {{'readonly="readonly"' if not edition or not editable else ''}}
                  >{{field_value}}</textarea>
               %else:
               <input id="{{field}}" name="{{field}}"
                  class="form-control"
                  type="{{'number' if field_type=='integer' else 'text'}}"
                  placeholder="{{placeholder}}"
                  value="{{field_value}}"
                  {{'readonly="readonly"' if not edition or not editable else ''}}
                  >
               %end
               %end
               %if hint:
               <p class="help-block">
                  {{hint}}
                  %if unique:
                  <br>This field must be unique.
                  %end
                  %if required:
                  <br>This field is required.
                  %end
               </p>
               %end
            </div>
         </div>
         %if selectize and edition:
         <script>
            $('#{{field}}').selectize({
               %if not required:
               'plugins': ["remove_button"],
               %end

               valueField: 'id',
               labelField: 'name',
               searchField: 'name',
               create: false,

               render: {
                  option: function(item, escape) {
                     return '<div>' +
                        %if icon:
                        '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                        %end
                        (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                        (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
                     '</div>';
                  },
                  item: function(item, escape) {
                     return '<div>' +
                        %if icon:
                        '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                        %end
                        (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                     '</div>';
                  }
               },

               %if allowed:
               %  # List of allowed values
               %  if allowed[0].startswith('inner://'):
                  preload: true,
                  openOnFocus: true,
                  load: function(query, callback) {
                     //if (!query.length) return callback();
                     $.ajax({
                        url: "{{allowed[0].replace('inner://', '/')}}",
                        type: 'GET',
                        error: function() {
                           callback();
                        },
                        success: function(res) {
                           // 10 first items only...
                           // callback(res.slice(0, 10));
                           callback(res);
                        }
                     });
                  },
               %  else:
                  options: [
                  %     for option in allowed:
                     {
                        'id': '{{option}}', 'name': '{{model.get("allowed_%s" % option, option)}}'
                     },
                  %     end
                  ],
               %  end
               %else:
               %# No list of allowed values
                  options: [
                     { 'id': 'XxX', 'name': 'You should define an allowed value...' }
                  ],
               %end

               maxItems: {{'null' if is_list or format == 'multiple' else '1'}},
               closeAfterSelect: {{'true' if format == 'select' else 'false'}},

               placeholder: '{{placeholder}}',
               hideSelected: true,
               %if not required:
               allowEmptyOption: true
               %end
            });
            %# Add selected options / items to the control...
            var $select = $('#{{field}}').selectize();
            var selectize = $select[0].selectize;
            %for field_id, field_value in list_values:
               selectize.addOption({id: "{{field_id}}", name: "{{field_value}}"});
            %end
            %for field_id, field_value in list_values:
               selectize.addItem("{{field_id}}");
            %end
         </script>
         %end
         %continue
      %end
      </fieldset>

      <div class="form-group">
         <div class="col-md-10 col-md-offset-2">
            <button type="button" class="btn btn-default">Cancel</button>
            <button type="submit" class="btn btn-primary">Submit</button>
         </div>
      </div>
   </form>
</div>

<script>
   $('form[data-element="{{element.id}}"]').on("submit", function (evt) {
      // Do not automatically submit ...
      evt.preventDefault();

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize()
      })
      .done(function(data, textStatus, jqXHR) {
         // data is JSON formed with a _message field
         if (jqXHR.status != 200) {
            console.error(jqXHR.status, data);
            raise_message_ko(data._message);
         } else {
            raise_message_info(data._message);
            $.each(data, function(field, value){
               if (field=='_message') return true;
               $('#'+field).parents("div.form-group").addClass("has-success");
               raise_message_ok("Updated " + field);
            })
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         console.error(errorThrown, textStatus);
      })
     .always(function() {
         //$('#widgets_loading').hide();
      });
   });
</script>