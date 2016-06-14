%# Default values
%setdefault('css', [])
%setdefault('js', [])
%setdefault('title', _('Untitled...'))

%setdefault('widget_id', 'widget')
%setdefault('collapsed', False)

<script type="text/javascript">
%for p in css:
    loadjscssfile('/static/plugins/{{p}}', 'css');
%end

%for p in js:
    loadjscssfile('/static/{{p}}', 'js');
%end
</script>

<div id="wd_panel_{{widget_id}}" class="panel panel-default">
   <div class="panel-heading">
      <i class="fa fa-leaf"></i>
      <span class="hosts-all">
         {{title}}
      </span>
      <div class="pull-right">
         <div class="btn-group">
            <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
               <i class="fa fa-gear fa-fw"></i>
               <span class="caret"></span>
            </button>
            <ul class="dropdown-menu pull-right" role="menu" style="padding: 10px; min-width: 320px;">
               <li>
                  <form role="form" onsubmit="return submit_{{widget_id}}_form();" style="font-size: 0.9em">

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
                                    <input type="text" class="form-control input-sm typeahead" placeholder="Search hosts ..." name="{{key}}" value="{{value}}" id="input-{{widget_id}}-{{key}}">
                                    <script>
                                       // On page loaded ...
                                       $(function() {
                                          // Typeahead: builds suggestion engine
                                          var hosts = new Bloodhound({
                                             datumTokenizer: Bloodhound.tokenizers.obj.whitespace('value'),
                                             queryTokenizer: Bloodhound.tokenizers.whitespace,
                                             remote: {
                                                url: '/lookup?q=%QUERY',
                                                filter: function (hosts) {
                                                   return $.map(hosts, function (host) { return { value: host }; });
                                                }
                                             }
                                          });
                                          hosts.initialize();

                                          // Typeahead: activation
                                          var typeahead = $('#input-{{wid}}-{{key}}').typeahead({
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
                                             $('#input-{{wid}}-{{key}}').val(suggestionObject.value).html(suggestionObject.value);
                                             hostSubmittable = true;
                                          });
                                       });
                                    </script>
                                    %else:
                                    <input type="text" class="form-control input-sm" placeholder="{{ value }} ..." name="{{key}}" value="{{value}}" id="input-{{widget_id}}-{{key}}">
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

                           <a class="btn btn-success" title="{{_('Save changes')}}">
                              <i class="fa fa-save fa-white"></i> {{_('Save changes')}}
                           </a>
                        </div>
                     </div>
                  </form>
               </li>
            </ul>
         </div>
         <a href="#p_wd_panel_{{widget_id}}" data-toggle="collapse" type="button" class="btn btn-xs">
            <span class="fa {{'fa-minus-square' if not collapsed else 'fa-plus-square'}} fa-fw"></span>
         </a>
      </div>
   </div>
   <div id="p_wd_panel_{{widget_id}}" class="panel-collapse collapse {{'in' if not collapsed else ''}}">
      <div class="panel-body">
         % setdefault('base', 'nothing')
         {{!base}}
      </div>
   </div>
</div>

<script>
   // Panels collapse state
   $('.panel').on('hidden.bs.collapse', function () {
      console.log("Panel hide", $(this))
//      stop_refresh();
      //panels[$(this).parent().attr('id')].collapsed = true;
      var grid = $('.grid-stack').data('gridstack');
      console.log(grid)
      $(this).find('.fa-minus-square').removeClass('fa-minus-square').addClass('fa-plus-square');
      /*
      save_user_preference('panels', JSON.stringify(panels), function() {
         start_refresh();
         do_refresh(true);
      });
      */
   });
   $('.panel').on('shown.bs.collapse', function () {
      console.log("Panel show")
//      stop_refresh();
      //panels[$(this).parent().attr('id')].collapsed = false;
      $(this).find('.fa-plus-square').removeClass('fa-plus-square').addClass('fa-minus-square');
      /*
      save_user_preference('panels', JSON.stringify(panels), function() {
         start_refresh();
         do_refresh();
      });
      */
   });

   // Graphs options
   $('[data-action="toggle-title"]').on('click', function () {
      stop_refresh();
      graphs[$(this).data('graph')].title = ! graphs[$(this).data('graph')].title;
      save_user_preference('graphs', JSON.stringify(graphs), function() {
         start_refresh();
         do_refresh(true);
      });
   });
   $('[data-action="toggle-legend"]').on('click', function () {
      stop_refresh();
      graphs[$(this).data('graph')].legend = ! graphs[$(this).data('graph')].legend;
      save_user_preference('graphs', JSON.stringify(graphs), function() {
         start_refresh();
         do_refresh(true);
      });
   });
   $('[data-action="toggle-state"]').on('click', function () {
      stop_refresh();
      graphs[$(this).data('graph')]['display_states'][$(this).data('state')] = ! graphs[$(this).data('graph')]['display_states'][$(this).data('state')];
      save_user_preference('graphs', JSON.stringify(graphs), function() {
         start_refresh();
         do_refresh(true);
      });
   });

</script>