%# Load all css stuff we need
%setdefault('css', [])
%setdefault('js', [])
%setdefault('title', _('Untitled...'))

<script type="text/javascript">
%for p in css:
    loadjscssfile('/static/{{p}}', 'css');
%end

%for p in js:
    loadjscssfile('/static/{{p}}', 'js');
%end
</script>

%collapsed_s = ''
%collapsed_j = 'false'
%if collapsed:
   %collapsed_s = 'collapsed'
   %collapsed_j = 'true'
%end

<script type="text/javascript">
   var w = {'id': '{{wid}}', 'base_url': '{{base_url}}', 'collapsed': {{collapsed_j}}, 'position': 'widget-place-1', 'options': {}};
   %for (k, v) in options.iteritems():
      %value = v.get('value', '')
      w.options['{{k}}'] = '{{value}}';
   %end

    // save into global widgets array
   widgets.push(w);
   if (new_widget) {
      new_widget = false;
      saveWidgets();
   }

   function submit_{{wid}}_form(){
      var form = document.forms["options-{{wid}}"];
      var widget = search_widget('{{wid}}');

      // If we can't find the widget, bail out
      if (widget == -1) {
         console.error('Cannot find the widget : {{wid}} for saving options!');
         return;
      }

      %for (k, v) in options.iteritems():
         %# """ for checkbox, the 'value' is useless, we must look at checked """
         %if v.get('type', 'text') == 'bool':
            var v = form.{{k}}.checked;
         %else:
            var v = form.{{k}}.value;
         %end
         widget.options['{{k}}'] = v;
      %end
      // so now we can ask for saving the state :)
      saveWidgets(function() {
         // If save is successfull we reload the widget
         reloadWidget('{{wid}}');
      });

      // Prevent the form to be actually sent.
      return false;
   }
</script>

%editable = 'editable'
%if len(options) == 0:
    %editable = ''
%end

<div class="widget movable collapsable removable {{editable}} closeconfirm {{collapsed_s}}" id="{{wid}}">
   <div class="widget-header">
      <span class="icon"><i class="fa fa-leaf"></i> </span>
      <strong>{{title}}</strong>
   </div>
   <div class="widget-editbox">
      <form id="options-{{wid}}" name="options-{{wid}}" class="well" role="form" onsubmit="return submit_{{wid}}_form();">
         %for (k, v) in options.iteritems():
            <div class="form-group" >
               %value = v.get('value', '')
               %label = v.get('label', k)
               %t = v.get('type', 'text')
               %if t != 'hidden':
                  <label for="{{k}}">{{label}}: </label>
               %end

               %# """ Manage the different types of values"""
               %if t in ['text', 'int', 'hst_srv']:
                  %if t == 'hst_srv':
                     <input type="text" class="form-control typeahead" placeholder="{{_('Search elements ...')}}" name="{{k}}" value="{{value}}" id="input-{{wid}}-{{k}}">
                     <script>
                            // On page loaded ...
                            $(function() {
                                // Typeahead: builds suggestion engine
                                var elements = new Bloodhound({
                                    datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
                                    queryTokenizer: Bloodhound.tokenizers.whitespace,
                                    remote: {
                                        url: '/lookup?q=%QUERY',
                                        filter: function (elements) {
                                            return $.map(elements, function (element) { return { value: element }; });
                                        }
                                    }
                                });
                                elements.initialize();

                                // Typeahead: activation
                                var typeahead = $('#input-{{wid}}-{{k}}').typeahead({
                                    hint: true,
                                    highlight: true,
                                    minLength: 3
                                },
                                {
                                    name: 'elements',
                                    displayKey: 'value',
                                    source: elements.ttAdapter(),
                                });

                                typeahead.on('typeahead:selected', function (eventObject, suggestionObject, suggestionDataset) {
                                    $('#input-{{wid}}-{{k}}').val(suggestionObject.value).html(suggestionObject.value);
                                    elementsubmittable = true;
                                });
                            });
                        </script>
                  %else:
                     <input type="text" class="form-control" placeholder="{{ value }} ..." name="{{k}}" value="{{value}}" id="input-{{wid}}-{{k}}">
                  %end
               %end
               %if t == 'hidden':
                  <input type="hidden" name='{{k}}' value='{{value}}'/>
               %end
               %if t in ['select']:
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
               %end
               %if t == 'bool':
                  %checked = 'checked' if value else ''
                  <input name='{{k}}' type="checkbox" {{checked}}/>
               %end
            </div>
         %end

         <a class="widget-close-editbox btn btn-success" onclick="return submit_{{wid}}_form();" title="{{_('Save changes')}}"><i class="fa fa-save fa-white"></i> Save changes</a>
      </form>
   </div>
   <div class="widget-content">
      % setdefault('base', 'nothing')
      {{!base}}
   </div>
</div>
