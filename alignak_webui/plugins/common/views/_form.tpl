%# Default values
%setdefault('debug', False)
%setdefault('edition', True)
%setdefault('title', '%s %s' % (object_type.title(), element.name))

%rebase("layout", title=title, page="/{{object_type}}/edit/{{element.id}}")

<div id="form_{{object_type}}">
   <form role="form" data-widget="{{element.id}}" data-action="save-options" method="post" action="/{{object_type}}/edit/{{element.id}}">
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
         %label = field.get('title', '')
         %field_type = field.get('type', 'string')
         %placeholder = field.get('placeholder', label)
         %allowed = field.get('allowed').split(',')

         %if field_type == 'objectid':
         %# ----------------------------------------------------------------------------------------
         %# Fred's awful hack for Bottle issue #869: https://github.com/bottlepy/bottle/issues/869
         %# ----------------------------------------------------------------------------------------
         %linked_object = element[name]
         %methods = [method for method in dir(linked_object) if callable(getattr(linked_object, method))]
         %attributes = [method for method in dir(linked_object) if not callable(getattr(linked_object, method))]
         %#get_link = linked_object.get_html_link()

         %for method in dir(linked_object):
         %if callable(getattr(linked_object, method)) and method=='get_html_link':
         %get_link = getattr(linked_object, method)
         %end
         %end

         %for method in dir(linked_object):
         %if not callable(getattr(linked_object, method)) and method=='__dict__':
         %get_dict = getattr(linked_object, method)
         %end
         %end
         %# ----------------------------------------------------------------------------------------
         %end

         %# """ Manage the different types of values"""
         %if field_type == 'hidden':
            <input type="hidden" name='{{name}}' value='{{value}}'/>
            %continue
         %end

         %if field_type in ['objectid']:
            %if debug:
            <i class="fa fa-bug"></i>{{field}} -> {{name}}='{{value}}' - {{attributes}}<br>
            <i class="fa fa-bug"></i>{{! get_link()}}<br>
            <i class="fa fa-bug"></i>{{! get_dict['_name']}} - {{! get_dict['_alias']}}<br>
            %end

            %from alignak_webui.objects.element_state import ElementState
            %icon = ElementState().get_icon_state(object_type, 'unknown')
            <div class="form-group">
               <label for="{{name}}" class="control-label">{{label}}</label>

               <select id="{{name}}" class="form-control">
                  <option value="{{get_dict['_id']}}">{{get_dict['_name']}}</option>
               </select>
            </div>
            <script>
               $('#{{name}}').selectize({
                  plugins: ['remove_button'],

                  valueField: 'id',
                  labelField: 'name',
                  searchField: 'name',
                  create: false,

                  options: [ {
                     'id': '{{get_dict['_id']}}', 'name': '{{get_dict['_name']}}'
                  }],

                  render: {
                     option: function(item, escape) {
                        return '<div>' +
                           '<span class="name">' +
                           '<i class="fa fa-{{icon['icon']}}"></i>&nbsp;' +
                           escape(item.name) +
                           '</span>' +
                           ' <em>(<small>' + escape(item.alias) + '</small>)</em>' +
                        '</div>';
                     },
                     item: function(item, escape) {
                        return '<span class="name">' +
                           '<i class="fa fa-{{icon['icon']}}"></i>&nbsp;' +
                           escape(item.name) +
                           '</span>';
                     }
                  },

                  preload: 'focus',
                  // {{allowed}}
                  %if len(allowed) > 0 and allowed[0].startswith('inner://'):
                  load: function(query, callback) {
                     if (!query.length) return callback();
                     $.ajax({
                        url: '{{allowed[0].replace('inner:/', '')}}',
                        type: 'GET',
                        error: function() {
                           console.error('Error!')
                           callback();
                        },
                        success: function(res) {
                           console.log(res)
                           callback(res.slice(0, 10));
                        }
                     });
                  },
                  %end

                  maxItems: 1,      // single selection
                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  allowEmptyOption: true
               });
            </script>
            %continue
         %end

         %if field_type in ['list']:
            %if debug:
            <i class="fa fa-bug"></i>{{field}} -> {{name}}='{{value}}' <br>
            %end
            <div class="form-group">
               <label for="{{name}}" class="control-label">{{label}}</label>

               <select id="{{name}}" multiple="" class="form-control">
                  %for option in value:
                  <option>{{option}}</option>
                  %end
               </select>
            </div>
            <script>
            %allowed = field.get('allowed')
            %if allowed.startswith('inner://'):
               $('#{{name}}').selectize({
                  plugins: ['remove_button'],
                  delimiter: ',',
                  persist: false,
                  %if edition:
                  create: true,     // Allow creation of new values
                  %end
                  %if value:
                  items: [
                  %for option in value:
                  '{{option}}',
                  %end
                  ],                // Initially selected values
                  %end
                  maxItems: null,   // multiselection
                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  allowEmptyOption: true
               });
            %else:
               $('#{{name}}').selectize({
                  %if edition:
                  create: true,     // Allow creation of new values
                  %end
                  %if value:
                  items: [
                  %for option in value:
                  '{{option}}',
                  %end
                  ],                // Initially selected values
                  %end
                  maxItems: null,   // multiselection
                  placeholder: '{{placeholder}}',
                  hideSelected: true,
                  allowEmptyOption: true
               });
            %end
            </script>
            %continue
         %end

         %if field_type in ['boolean']:
            <div class="form-group">
                  <div class="checkbox">
                     <label>
                        <input type="checkbox" {{'checked="checked"' if value else ''}}> {{label}}
                     </label>
                  </div>
            </div>
            %continue
         %end

         %if field_type in ['string', 'integer']:
            <div class="form-group">
               <label for="{{name}}" class="control-label">{{label}}</label>
               <input class="form-control" type="{{'number' if field_type=='integer' else 'text'}}" placeholder="{{ value }}" name="{{name}}" value="{{value}}">
               %if field.get('hint'):
               <p class="help-block">
                  {{field.get('hint')}}
                  %if field.get('unique', False):
                  <br>This field must be unique!
                  %end
               </p>
               %end
            </div>
            %continue
         %end

         %if field_type in ['hst_srv']:
            <div class="form-group">
               <label for="{{name}}">{{label}}</label>
               %if field_type == 'hst_srv' and bloodhound:
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
                     var typeahead = $('#input-{{element.id}}-{{key}}').typeahead({
                        hint: true,
                        highlight: true,
                        minLength: 3
                     },
                     {
                        name: 'hosts',
                        displayKey: 'value',
                        source: hosts.ttAdapter(),
                     });

                     typeahead.on('typeahead:selected', function (eventlinked_object, suggestionlinked_object, suggestionDataset) {
                        $('#input-{{element.id}}-{{key}}').val(suggestionlinked_object.value).html(suggestionlinked_object.value);
                        hostSubmittable = true;
                     });
                  });
               </script>
               %end
            </div>
            %continue
         %end

         %if field_type in ['select']:
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


         %if debug:
         <i class="fa fa-bug"></i>{{field}} -> {{name}}='{{value}}' <br>
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