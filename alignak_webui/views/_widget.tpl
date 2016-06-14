%# Default values
%setdefault('title', _('Untitled...'))

%setdefault('widget_id', 'widget')
%setdefault('collapsed', False)

<div id="wd_panel_{{widget_id}}" class="panel panel-default">
   <div class="panel-heading">
      <i class="fa fa-leaf"></i>
      <span class="hosts-all">
         {{title}}
      </span>
      <div class="pull-right">
         <a data-widget="{{widget_id}}" data-action="remove-widget" type="button" class="btn btn-xs"><i class="fa fa-close fa-fw"></i></a>
      </div>
      %if options:
      <div class="pull-right">
         <div class="btn-group">
            <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
               <i class="fa fa-gear fa-fw"></i>
               <span class="caret"></span>
            </button>
            <ul class="dropdown-menu pull-right" role="menu" style="padding: 10px; min-width: 320px;">
               <li>
                  <form role="form" data-widget="{{widget_id}}" data-action="save-options" method="post" action="{{widget_uri}}" style="font-size: 0.9em">
                     <input type="hidden" name='widget_id' value='{{widget_id}}'/>
                     <input type="hidden" name='widget_template' value='{{widget_template}}'/>
                     <input type="hidden" name='title' value='{{title}}'/>
                     <div class="panel panel-default">
                        <div class="panel-heading">
                           <h3 class="panel-title">{{_('Widget options:')}}</h3>
                        </div>
                        <div class="panel-body">
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
                                    %if type == 'hst_srv':
                                    <input type="text" class="form-control input-sm typeahead" placeholder="{{_('Search by name ...')}}" name="{{key}}" value="{{value}}" id="input-{{widget_id}}-{{key}}">
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
                                    <input type="{{'number' if type=='int' else 'text'}}" class="form-control input-sm" placeholder="{{ value }} ..." name="{{key}}" value="{{value}}" id="input-{{widget_id}}-{{key}}">
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

                           <button type="submit" class="btn btn-success btn-block"> <i class="fa fa-save"></i>&nbsp;{{_('Save changes')}}</button>
                        </div>
                     </div>
                  </form>
               </li>
            </ul>
         </div>
      </div>
      %end
   </div>
      <div class="panel-body">
         % setdefault('base', 'nothing')
         {{!base}}
      </div>
</div>

<script>
   $('body').on("submit", 'form[data-action="save-options"]', function (evt) {
      console.debug('Submit form data: ', $(this));
      console.debug('Form item/action: ', $(this).data("widget"), $(this).data("action"));
      console.debug('Form data: ', $(this).serializeArray());

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
            raise_message_ko(jqXHR.status, data);
         } else {
            $("#" + widget_id + " div.grid-stack-item-content").html(data);
            raise_message_ok("{{_('Widget options saved')}}");
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         raise_message_ko(jqXHR.responseJSON['message']);
      })
     .always(function() {
         $('#widgets_loading').hide();
      });
   });

   $('body').on("click", 'a[data-action="remove-widget"]', function (evt) {
      console.debug('Remove widget: ', $(this));
      console.debug('Form item/action: ', $(this).data("widget"), $(this).data("action"));

      var grid = $('.grid-stack').data('gridstack');
      grid.removeWidget('#' + $(this).data("widget"));
   });
</script>