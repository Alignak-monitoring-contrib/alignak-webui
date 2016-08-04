%import json

%# Default values
%setdefault('debug', False)
%setdefault('edition', True)
%setdefault('title', '%s %s' % (object_type.title(), element.name))

%rebase("layout", title=title, page="/{{object_type}}/edit/{{element.id}}")

<div id="form_{{object_type}}">
   <form role="form"
         data-widget="{{element.id}}" data-action="save-options"
         method="post" action="/{{object_type}}/edit/{{element.id}}"
         style="padding: 20px;">

      <input type="hidden" name='element.id' value='{{element.id}}'/>

      <fieldset>
      <legend>{{title}}</legend>

      %for field in dt.table_columns:
         %#if not field.get('editable'):
         %#continue
         %#end

         %name = field.get('data', '')
         %if name[0] in ['#', '_']:
            %if debug:
            <i class="fa fa-bug"></i>Ignored '{{name}}' field<br>
            %end
            %continue
         %end

         %value = element[name]
         %field_id=element.id
         %field_value=value

         %from alignak_webui.objects.element import BackendElement
         %# Field value is a list
         %if isinstance(value, list):
         %  list_value = []
         %  for v in value:
         %     if isinstance(v, BackendElement):
         %        list_value.append(v.name)
         %     elif isinstance(v, basestring):
         %        list_value.append(v)
         %     elif isinstance(v, tuple):
         %        list_value.append(v)
         %     else:
         %        list_value.append(v._id)
         %     end
         %  end
         %  field_value=','.join(list_value)
         %end

         %# Field value is a dict
         %if isinstance(value, dict):
         %  list_value = []
         %  for k,v in value.items():
         %     list_value.append('%s=%s' % (k, v))
         %  end
         %  field_value=','.join(list_value)
         %end

         %label = field.get('title', '')
         %field_type = field.get('type', 'string')
         %content_type = field.get('content_type', 'string')
         %placeholder = field.get('placeholder', label)
         %allowed = field.get('allowed').split(',')
         %format = field.get('format')
         %format_parameters = field.get('format_parameters')
         %required = field.get('required')

         %is_list = False
         %if field_type=='list':
         %  is_list = True
         %  field_type = content_type
         %end

         %if field_type.startswith('objectid'):
         %# ----------------------------------------------------------------------------------------
         %# Fred's awful hack for Bottle issue #869: https://github.com/bottlepy/bottle/issues/869
         %# ----------------------------------------------------------------------------------------
         %if not is_list:
         %  linked_object = element[name]
         %  for method in dir(linked_object):
         %     if not callable(getattr(linked_object, method)) and method=='__dict__':
         %        get_dict = getattr(linked_object, method)
         %     end
         %  end
         %  field_id=get_dict['_id']
         %  field_value=get_dict['_name']
         %end
         %# ----------------------------------------------------------------------------------------
         %end

         %if debug:
            <i class="fa fa-bug"></i>
            {{'%s (%s) -> %s%s=%s' % (name, field_id, field_type, content_type if field_type=='list' else '', field_value)}}<br/>
            <i class="fa fa-bug"></i>
            {{field}}
         %end

         %# Manage the different types of values
         %# ----------------------------------------------------------------------------------------
         %if field_type == 'hidden':
            <input type="hidden" name='{{name}}' value='{{value}}'/>
            %continue
         %end

         %if field_type.startswith('objectid'):
            %linked_object_type = content_type.replace('objectid:', '')
            %icon=''
            %if linked_object_type:
            %  from alignak_webui.objects.element_state import ElementState
            %  icon = ElementState().get_icon_state(linked_object_type, 'unknown')
            %  icon=icon['icon'] if icon else ''
            %end
            <div class="form-group">
               <label for="{{name}}" class="col-md-2 control-label">{{label}} {{icon}}</label>
               <div class="col-md-10">
                  <input id="{{name}}" name="{{name}}"
                     class="form-control"
                     type="{{'number' if field_type=='integer' else 'text'}}"
                     placeholder="{{placeholder}}"
                     value="{{field_value}}"
                     >
                  %if field.get('hint'):
                  <p class="help-block">
                     {{field.get('hint')}}
                     %if field.get('unique', False):
                     <br>This field must be unique!
                     %end
                  </p>
                  %end
               </div>
            </div>
            <script>
               $('#{{name}}').selectize({
                  plugins: ['remove_button'],

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
                        console.log('Render: ', item, escape)
                        return '<div>' +
                           %if icon:
                           '<i class="fa fa-{{icon}}"></i>&nbsp;' +
                           %end
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                        '</div>';
                     }
                  },

                  %if allowed:
                  %# List of allowed values
                  %if allowed[0].startswith('inner://'):
                  preload: true,
                  load: function(query, callback) {
                     if (!query.length) return callback();
                     $.ajax({
                        url: "{{allowed[0].replace('inner://', '/')}}",
                        type: 'GET',
                        error: function() {
                           callback();
                        },
                        success: function(res) {
                           // 10 first items...
                           callback(res.slice(0, 10));
                        }
                     });
                  },
                  %else:
                     options: [
                     %if is_list:
                        %for option in allowed:
                        {
                           'id': '{{option}}', 'name': '{{option}}'
                        },
                        %end
                     %else:
                        { 'id': '{{field_id}}', 'name': '{{field_value}}' }
                     %end
                     ],
                  %end
                  %else:
                  %# No list of allowed values
                     options: [
                        { 'id': '{{field_id}}', 'name': '{{field_value}}' }
                     ],
                  %end

                  maxItems: {{'1' if format == 'select' else 'null'}},
                  closeAfterSelect: {{'true' if format == 'select' else 'false'}},

                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  %if not required:
                  allowEmptyOption: true
                  %end
               });
            </script>
            %continue
         %end

         %if field_type in ['boolean']:
            <div class="form-group">
               <div class="col-md-offset-2 col-md-10">
                  <div class="togglebutton">
                     <label>
                        <input type="checkbox" {{'checked="checked"' if value else ''}}> {{label}}
                     </label>
                  </div>
               </div>
            </div>
            %continue
         %end

         %if field_type in ['dict', 'string', 'integer']:
            <div class="form-group">
               <label for="{{name}}" class="col-md-2 control-label">{{label}}</label>
               <div class="col-md-10">
                  <input id="{{name}}" name="{{name}}"
                     class="form-control"
                     type="{{'number' if field_type=='integer' else 'text'}}"
                     placeholder="{{placeholder}}"
                     value="{{field_value}}"
                     >
                  %if field.get('hint'):
                  <p class="help-block">
                     {{field.get('hint')}}
                     %if field.get('unique', False):
                     <br>This field must be unique!
                     %end
                  </p>
                  %end
               </div>
            </div>
            %if is_list:
            <script>
               $('#{{name}}').selectize({
                  plugins: ['remove_button'],
                  delimiter: ',',
                  persist: false,

                  valueField: 'id',
                  labelField: 'name',
                  searchField: 'name',
                  create: false,

                  render: {
                     option: function(item, escape) {
                        return '<div>' +
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                           (item.alias ? '<small><em><span class="alias"> (' + escape(item.alias) + ')</span></em></small>' : '') +
                        '</div>';
                     },
                     item: function(item, escape) {
                        return '<div>' +
                           (item.id ? '' : '***') +
                           (item.name ? '<span class="name">' + escape(item.name) + '</span>' : '') +
                        '</div>';
                     }
                  },

                  %if allowed:
                  %if allowed[0].startswith('inner://'):
                  preload: true,
                  load: function(query, callback) {
                     if (!query.length) return callback();
                     $.ajax({
                        url: "{{allowed[0].replace('inner://', '/')}}",
                        type: 'GET',
                        error: function() {
                           callback();
                        },
                        success: function(res) {
                           // 10 first items...
                           callback(res.slice(0, 10));
                        }
                     });
                  },
                  %else:
                  items: [
                  %for option in allowed:
                  {
                     'id': '{{option}}', 'name': '{{option}}'
                  },
                  %end
                  ],
                  %end
                  %end

                  maxItems: {{'1' if format == 'select' else 'null'}},
                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  %if not required:
                  allowEmptyOption: true
                  %end
               });
            </script>
            %end
            %continue
         %end

         %if debug:
         <i class="fa fa-bug"></i><i class="fa fa-bug"></i>{{field}} -> {{name}}='{{field_value}}' <br>
         %end
      %end
      </fieldset>
   </form>
</div>

<script>
   $('form[data-widget="{{element.id}}"]').on("submit", function (evt) {
      // Do not automatically submit ...
      evt.preventDefault();

      $('#widgets_loading').show();

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize()
      })
      .done(function( data, textStatus, jqXHR ) {
         if (jqXHR.status != 200) {
            console.error(jqXHR.status, data);
         } else {
            console.log('Posted !');
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         console.error(errorThrown, textStatus);
      })
     .always(function() {
         $('#widgets_loading').hide();
      });
   });
</script>