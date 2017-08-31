%import json

%setdefault('debug', False)
%setdefault('debugTable', False)

%setdefault('edition_mode', False)

%# embedded is True if the table is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%# Default filtering is to use the table saved state
%setdefault('where', {'saved_filters': True})
%setdefault('global_where', None)

%setdefault('commands', False)
%setdefault('object_type', 'unknown')

%from bottle import request
%search_string = request.query.get('search', '')

%if not embedded:
%# Datatables js and css are included in the page layout
%rebase("layout", title=title, page="/{{object_type}}s_table")
%end

%if embedded and identifier:
%scheme = request.urlparts.scheme
%location = request.urlparts.netloc
%path = request.urlparts.path
%#Do not change path ...
%#path = path.replace('/external/table/'+identifier, '')
%server_url = scheme + '://' + location + path
%else:
%server_url = ''
%end
<!-- Table identifiers -->
%table_id = "%ss_table" % object_type
%if dt.templates:
%table_id = "%ss_templates_table" % object_type
%end
%table_pref = "table_%s" % object_type
%if dt.templates:
%table_pref = "templates_table_%s" % object_type
%end

<!-- Table filtering ... -->
%include("_filters.tpl")

<div id="{{table_id}}" class="alignak_webui_table {{'embedded' if embedded else ''}}">
   <table id="tbl_{{table_id}}" class="{{dt.css}}">
      <thead>
         <tr>
            %for column in dt.table_columns:
            %hint = _('Field name: %s\nComment: %s') % (column['data'], column.get('comment', ''))
            <th data-name="{{ column['data'] }}" data-type="{{ column['type'] }}" title="{{ hint }}">{{ column['title'] }}</th>
            %end
         </tr>
         %if dt.searchable:
         %if debug:
         <tr id="debug">
            %idx=0
            %for field in dt.table_columns:
               %name = field.get('data', '')
               %label = field.get('title', '')
               %field_type = field.get('type', 'string')
               %content_type = field.get('content_type', 'string')
               %placeholder = field.get('placeholder', label)
               %allowed = field.get('allowed', '')
               %if not isinstance(allowed, list):
               %allowed = allowed.split(',')
               %end
               %if allowed[0] == '':
               %  allowed = []
               %end
               %format = field.get('format')
               %format_parameters = field.get('format_parameters')
               <th>
                  <div>
                  <i class="fa fa-bug"></i>
                  %if field_type=='list':
                  {{'%s -> %s (%s) - %s (%s)' % (name, field_type, content_type, format, format_parameters)}}
                  %else:
                  {{'%s -> %s - %s (%s)' % (name, field_type, format, format_parameters)}}
                  %end
                  <br/>
                  <i class="fa fa-list"></i> {{allowed}}
                  </div>
               </th>
            %end
         </tr>
         %end
         <tr id="filterrow">
            %idx=0
            %timeout=0
            %for field in dt.table_columns:
               %selectize = False
               %name = field.get('data', '')
               %label = field.get('title', '')
               %field_type = field.get('type', 'string')
               %content_type = field.get('content_type', 'string')
               %placeholder = field.get('placeholder', '')
               %allowed = field.get('allowed', '')
               %if not isinstance(allowed, list):
               %allowed = allowed.split(',')
               %end
               %if allowed[0] == '':
               %  allowed = []
               %end
               %format = field.get('format')
               %format_parameters = field.get('format_parameters')
               %required = field.get('required')

               %column_class = ''
               %if field['data'].startswith('ls_'):
               %column_class = 'livestate'
               %end

               %is_list = False
               %if field_type=='list':
               %  is_list = True
               %  selectize = True
               %  field_type = content_type
               %else:
               %  if allowed:
               %  selectize = True
               %  end
               %  if field_type in ['boolean', 'objectid']:
               %  selectize = True
               %  end
               %end

               <td class="{{column_class}}" data-index="{{idx}}" data-name="{{ field['data'] }}" data-selectized="{{selectize}}"
                   data-searchable="{{ field['searchable'] }}" data-regex="{{ field['regex_search'] }}"
                   data-type="{{ field['type'] }}" data-content-type="{{ field['content_type'] }}"
                   data-format="{{ field['format'] }}" data-format-parameters="{{ field['format_parameters'] }}"
                   data-allowed="{{ field['allowed'] }}">
                  %if is_list:
                  <div class="form-group form-group-sm">
                     <select id="filter_{{name}}" class="form-control"></select>
                  </div>
                  %else:
                  %  if field_type in ['boolean']:
                  %  allowed = {'Yes': 'true', 'No': 'false', 'Both': ''}
                  <div class="form-group form-group-sm">
                     <input id="filter_{{name}}" class="form-control" type="text" placeholder="{{placeholder}}">
                  </div>
                  %  else:
                  <div class="form-group form-group-sm">
                     <input id="filter_{{name}}" class="form-control" type="{{'number' if field_type=='integer' else 'text'}}" placeholder="{{placeholder}}">
                  </div>
                  %  end
                  %end
                  %if selectize:
                  <script>
                     //window.setTimeout(function() {
                     $('#filter_{{name}}').selectize({
                        plugins: ['remove_button'],
                        delimiter: ',',
                        persist: true,

                        valueField: 'id',
                        labelField: 'name',
                        searchField: 'name',

                        create: false,

                        %if allowed:
                        %  if isinstance(allowed, dict):
                           options: [
                        %     for k in allowed:
                                 { 'id': '{{allowed[k]}}', 'name': '{{k}}' },
                        %     end
                           ],
                        %  else:
                        %     if isinstance(allowed[0], basestring) and allowed[0].startswith('inner://'):
                        preload: true,
                        load: function(query, callback) {
                           $.ajax({
                              url: "{{allowed[0].replace('inner://', '/')}}",
                              type: 'GET',
                              error: function() {
                                 callback();
                              },
                              success: function(res) {
                                 callback(res);
                              }
                           });
                        },
                        %     else:
                           options: [
                        %        for option in allowed:
                                    { 'id': '{{option}}', 'name': '{{option}}' },
                        %        end
                           ],
                        %     end
                        %  end
                        %end

                        maxItems: {{'1' if not is_list else 'null'}},
                        closeAfterSelect: {{'true' if format == 'select' else 'false'}},
                        placeholder: '{{placeholder}}',
                        hideSelected: true,
                        allowEmptyOption: false,
                        openOnFocus: true,
                        onChange: function(value) {
                           if (debugTable) console.log("Changed:", value, this);
                           //this.clear(true);
                        }
                     });
                     //}, {{timeout}});
                     %timeout += 500
                  </script>
                  %end
               </td>
               %idx += 1
            %end
         </tr>
         %end
      </thead>
      <tbody>
      </tbody>
   </table>
</div>

<script>
   var debugTable = {{'true' if debugTable else 'false'}};
   var where = {{! json.dumps(where)}};
   var selectedRows = [];

   function resetFilters() {
      if (debugTable) console.debug('Reset table filters');
      var table = $('#tbl_{{table_id}}').DataTable({ retrieve: true });

      // Reset table columns search
      table
         .columns()
            .search('', false, false)
            .draw();

      // Clear the search fields based on selectize
      $('td[data-searchable="True"]').each( function () {
         var field_name = $(this).data('name');

         if ($(this).data('selectized') == "True") {
            if ($('#filter_'+field_name).length) {
               var input_filter = $('#filter_'+field_name).selectize()[0].selectize;
               if (input_filter) {
                  if (debugTable) console.debug('*** clear selectized filter: ', field_name, input_filter.items);
                  input_filter.clear(true);
               }
            }
         } else {
            if ($('#filter_'+field_name).length) {
               if (debugTable) console.debug('*** clear filter: ', field_name, $('#filter_'+field_name).val());
               $('#filter_'+field_name).val('');
            }
         }
      });

      // Disable the clear filter button
      table.buttons('clearFilter:name').disable();
   }

   $(document).ready(function() {
      %if not embedded:
      set_current_page("{{ webui.get_url(request.route.name) }}");
      %end

      %if credentials:
      $.ajaxSetup({
         headers: { "Authorization": "Basic " + btoa('{{credentials}}') }
      });
      %end

      %if dt.searchable:
      // event for search on enter keyup
      $(function () {
         $('.dataTables_filter input').unbind();
         $('#webui-search-input input').bind('keyup', function (e) {
            if (e.keyCode != 13) return;
            if (debugTable) console.debug('Datatable global search:', $(this).val());
            var table = $('#tbl_{{table_id}}').DataTable({ retrieve: true });
            table.search($(this).val()).draw();
         });
      });

      // Apply the search filter for input fields
      $("#tbl_{{table_id}} thead input").on('keyup change', function () {
         var parent = $(this).parents('[data-name]')
         var column_index = parent.data('index');
         var column_name = parent.data('name');
         var regex = parent.data('regex');
         var value = $(this).val();
         if ($(this).attr('type') == 'checkbox') {
            value = $(this).is(':checked');
         }
         if (debugTable) console.debug('Datatable input event, search column '+column_name+' for '+value);

         table
            .column(column_index)
               .search(value, regex=='True', false)
               .draw();

         // Enable the clear filter button
         table.buttons('clearFilter:name').enable();
      });

      // Apply the search filter for select fields
      $("#tbl_{{table_id}} thead select").on('change', function () {
         var parent = $(this).parents('[data-name]')
         var column_index = parent.data('index');
         var column_name = parent.data('name');
         var value = $(this).val() || [];

         if (debugTable) console.debug("Datatable select event, search column '"+column_name+"' for '" + value + "'");

         var table = $('#tbl_{{table_id}}').DataTable({ retrieve: true });
         table
            .column(column_index)
              .search(value, false, false)
              .draw();

         // Enable the clear filter button
         table.buttons('clearFilter:name').enable();
      });
      %end

      $('#tbl_{{table_id}}').on( 'init.dt', function ( e, settings ) {
         if (debugTable) console.debug('Datatable event, init ...');
      });

      %if dt.selectable:
      $('#tbl_{{table_id}}').on( 'select.dt', function ( e, dt, type, indexes ) {
         if (debugTable) console.debug('Datatable event, selected row ...');

         var rowData = table.rows( indexes ).data().toArray();
         if (debugTable) console.debug('Datatable event, selected: ', rowData);
      });

      $('#tbl_{{table_id}}').on( 'deselect.dt', function ( e, dt, type, indexes ) {
         if (debugTable) console.debug('Datatable event, deselected row ...');

         var rowData = table.rows( indexes ).data().toArray();
         if (debugTable) console.debug('Datatable event, deselected: ', rowData);
      });
      %end

      $('#tbl_{{table_id}}').on( 'stateLoaded.dt', function ( e, settings, data ) {
         var table = $('#tbl_{{table_id}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, stateLoaded.dt...');
         if (debugTable) console.debug('Saved filters:', where['saved_filters']);

         // Disable the clear filter button
         table.buttons('clearFilter:name').disable();

         if (where['saved_filters']) {
            if (debugTable) console.debug('Restoring saved filters:', where, data);

            // Update each search field with the received value
            $.each(data.columns, function(index, value) {
               var name = $('#filterrow td[data-index="'+index+'"]').data('name');
               var selectized = $('#filterrow td[data-index="'+index+'"]').data('selectized') == 'True';

               if ($('#filter_'+name).length) {
                  if (value['search']['search'] != "") {
                     if (debugTable) console.debug('*** update filter: ', index, name, value['search']['search']);

                     if (selectized) {
                        var input_filter = $('#filter_'+name).selectize()[0].selectize;
                        if (debugTable) console.debug('*** input filter: ', selectized, input_filter);

                        // Update search filter input field value
                        input_filter.setValue(value['search']['search']);
                     } else {
                        var input_filter = $('#filter_'+name);
                        input_filter.val(value['search']['search']);
                     }

                     // Configure table filtering
                     table
                        .column(index)
                           .search(value['search']['search'], $('#filterrow th[data-index="'+index+'"]').data('regex'), false);

                     // Enable the clear filter button
                     table.buttons('clearFilter:name').enable();
                  }
               }
            });
         } else {
            if (debugTable) console.debug('Erasing saved filters:', where);

            resetFilters();

            if (debugTable) console.debug('Datatable global search:', where);
            var table = $('#tbl_{{table_id}}').DataTable({ retrieve: true });
            table.search(where).draw();

            /* *****************************
             * Removed in benefit of the Web UI search engine
            // Update each search field with the filter URL parameters
            $.each(where, function(key, value) {
               var special = '';
               // Special filtering ($ne, $in, ...)
               if (key[0] == "$") {
                  special = key;
                  for (k in value) {
                     key = k;
                     value = value[k];
                  }
               }
               var column_index = table.column(key+':name').index();
               var column_regex = table.column(key+':name').data('regex');

               if (debugTable) console.debug('Update column search', column_index, key, value, column_regex);
               if (debugTable) console.debug('Update column search special', special);

               // Update search filter input field value
               var input_filter = $('#filter_'+key).selectize()[0].selectize;
               if (debugTable) console.debug("Set new value: '" + value + "', for "+key);
               $('#filterrow th[data-name="'+key+'"]').children().val(value);

               // Update search filter input field value
               input_filter.setValue(value);

               // Configure table filtering
               table
                  .column(column_index)
                     .search(value, $('#filterrow th[data-name="'+key+'"]').data('regex'), false);

               // Enable the clear filter button
               table.buttons('clearFilter:name').enable();
            });

            ************************** */
         }
      });

      // Table declaration
      table = $('#tbl_{{table_id}}').DataTable( {
         // Table columns definition
         "columns": {{ ! json.dumps(dt.table_columns) }},

         // Disable automatic width calculation
         "autoWidth": false,

         // Pagination
         "paging": {{'true' if dt.paginable else 'false'}},
         "pagingType": "simple_numbers",

         // Pagination
         "lengthChange": true,
         "pageLength": 25,
/* Issue #81
         "lengthMenu": [
            [ 10, 25, 50, 100, -1 ],
            [
               "{{_('10 rows')}}", "{{_('25 rows')}}", "{{_('50 rows')}}", "{{_('100 rows')}}", "{{_('Show all')}}"
            ]
         ],
*/
         "lengthMenu": [
            [ 10, 25, 50 ],
            [
               "{{_('10 rows')}}", "{{_('25 rows')}}", "{{_('50 rows')}}"
            ]
         ],
         // Table information
         "info": true,

         /* Table fixed header: #74
         "fixedHeader": {
            header: true,
            headerOffset: $('#topbar').outerHeight() + $('#filter-bar').outerHeight(),
            footer: true,
            footerOffset: '50px'
         }, */
         /* Fixed leftmost column and scrolling mode: #74
         "scrollX": true,
         "fixedColumns": {
            leftColumns: 1
         },*/

         // Server side processing: request new data
         "processing": true,
         "serverSide": true,
         "ajax": {
            "url": "{{server_url}}/{{object_type}}s/{{'templates_table_data' if dt.templates else 'table_data'}}",
            "method": "POST",
            "data": function ( d ) {
               // Add an extra field
               d = $.extend({}, d, {
                  "object_type": '{{object_type}}',
                  "embedded": '{{embedded}}',
                  "links": '{{links}}'
               });

               // Json stringify to avoid complex array formatting ...
               d.columns = JSON.stringify( d.columns );
               d.search = JSON.stringify( d.search );
               d.order = JSON.stringify( d.order );
               return ( d );
            }
         },

         %if dt.orderable:
         // Table ordering
         "ordering": true,
         // First row for ordering
         "orderCellsTop": true,
         // Default initial sort
         "order": {{ ! json.dumps(dt.initial_sort) }},
         %else:
         "ordering": false,
         %end

         // Language
         "language": {{! json.dumps(dt.get_language_strings())}},

         // Responsive mode
         %if dt.responsive:
         %setdefault('details', True)
         %setdefault('inline', True)
         %setdefault('immediateRow', False)
         %setdefault('modalDisplay', True)

         responsive: {
            %if details:
            details: {
               %if inline:
               type: 'inline'
               %else:
               type: 'inline'
               %end
               %if immediateRow:
               , display: $.fn.dataTable.Responsive.display.childRowImmediate
               , type: ''
               %elif modalDisplay:
               , display: $.fn.dataTable.Responsive.display.modal({
                  header: function ( row ) {
                     return ('{{_('Details for %s') % object_type}}');
                  }
                })
               , renderer: $.fn.dataTable.Responsive.renderer.tableAll({
                    tableClass: 'table'
               })
               %end
            }
            %else:
            details: false,
            %end
         },
         %else:
         responsive: false,
         %end

         // Selection mode
         select: {{'true' if dt.selectable else 'false'}},

         // Table state saving/restoring
         stateSave: true,
         // Saved parameters
         "stateSaveParams": function (settings, data) {
            if (debugTable) console.debug("state saved data", data);
            // Ignore global search parameter ...
            data.search.search = "";
         },
         // Load table configuration
         %if not request.query.get('no_restore', ''):
         stateLoadCallback: function (settings) {
            if (debugTable) console.debug("state loading for 'tbl_{{object_type}}' ...");

            // Get table stored state from the server ...
            var o;
            $.ajax( {
               "url": "{{server_url}}/preference/user",
               "dataType": "json",
               "type": "GET",
               "data": {
                  "key": '{{table_pref}}'
               },
               "async": false,
               "success": function (json) {
                  if (debugTable) console.debug("state restored for 'tbl_{{table_id}}' ...", json);
                  o = json;
               }
            });

            return o;
         },
         %end
         // Save table configuration
         stateSaveCallback: function (settings, data) {
            if (debugTable) console.debug("state saving for 'tbl_{{object_type}}' ...", settings);

            // Post table data to the server ...
            $.ajax({
               "url": "{{server_url}}/preference/user",
               "dataType": "json",
               "type": "POST",
               "data": {
                  "key": '{{table_pref}}',
                  // Json stringify to avoid complex array formatting ...
                  "value": JSON.stringify(data)
               },
               "success": function () {
                  //if (debugTable) console.debug("state saved for 'tbl_{{table_id}}' ...", settings);
               }
            });
         },

         /*
            B - buttons
            l - length changing input control
            f - filtering input
            t - The table!
            i - Table information summary
            p - pagination control
            r - processing display element
         dom: 'Blfrtip',
         No datatable global search...
         */
         dom:
            "<'row buttons'<'col-xs-12'B>>" +
            "<'row table'<'col-xs-12'tr>>" +
            "<'row'<'hidden-xs'i>>" +
            "<'row'<'col-xs-12'p>>",
         // Table columns visibility button
         buttons: [
            {
               extend: 'pageLength',
               className: 'btn-raised btn-xs'
            }
            ,{
               extend: 'colvis',
               className: 'btn-raised btn-xs'
            }
            ,{
               extend: 'columnsToggle',
               columns: '.livestate'
            }
            %if dt.printable:
            ,{
               extend: 'print',
               autoPrint: false,
               // message: 'Utiliser la fonction Imprimer de votre navigateur pour imprimer la page',
               exportOptions: {
                  columns: ':visible',
                  modifier: {
                     search: 'none'
                  }
               },
               className: 'btn-raised btn-xs'
            }
            %end
            %if dt.exportable:
            ,{
               extend: 'collection',
               buttons: [
                  {
                     extend: 'csv',
                     header: true,
                     footer: false,
                     fieldBoundary: '"',
                     fieldSeparator: ";",
                     extension: ".csv",
                     exportOptions: {
                        columns: ':visible',
                        modifier: {
                           search: 'none'
                        }
                     },
                     className: 'btn-raised btn-xs'
                  }
                  ,
                  {
                     extend: 'excel',
                     header: true,
                     footer: false,
                     extension: ".xlsx",
                     exportOptions: {
                        columns: ':visible',
                        modifier: {
                           search: 'none'
                        }
                     },
                     className: 'btn-raised btn-xs'
                  }
                  ,
                  {
                     extend: 'pdf',
                     header: true,
                     footer: false,
                     extension: ".pdf",
                     orientation: 'landscape',
                     pageSize: 'A4',
                     exportOptions: {
                        columns: ':visible',
                        modifier: {
                           search: 'none'
                        }
                     },
                     className: 'btn-raised btn-xs'
                  }
               ],
               className: 'btn-raised btn-xs'
            }
            %end
            %if dt.searchable:
            ,{
               name: 'clearFilter',
               text: '<span id="clearFilter" class="fa-stack" style="font-size:0.63em;"><i class="fa fa-filter"></i><i class="fa fa-ban fa-stack-2x text-danger"></i></span>',
               titleAttr: "{{_('Reset all the search filters')}}",
               action: function ( e, dt, node, data ) {
                  resetFilters();
               },
               className: 'btn-raised btn-xs'
            }
            %end
            %if dt.selectable:
            ,{
               extend: 'selectAll',
               titleAttr: "{{_('Select all the table rows')}}",
               className: 'btn-raised btn-xs'
            }
            ,{
               extend: 'selectNone',
               titleAttr: "{{_('Unselect all rows')}}",
               className: 'btn-raised btn-xs'
            }
            %end
            %if dt.editable and edition_mode:
            // Only for 'editable' tables
            ,{
               text: "{{! _('<span class=\'text-warning fa fa-plus\'></span>')}}",
               titleAttr: "{{_('Create a new item')}}",
               className: 'btn-raised btn-xs',
               action: function (e, dt, button, config) {
                  var url = "{{server_url}}/{{object_type}}_form/None{{'?is_template=1' if dt.templates else ''}}";
                  window.setTimeout(function(){
                     window.location.href = url;
                  }, 50);
               }
            }
            ,{
               extend: 'selectedSingle',
               text: "{{! _('<span class=\'text-warning fa fa-edit\'></span>')}}",
               titleAttr: "{{_('Edit the selected item')}}",
               className: 'btn-raised btn-xs',
               action: function (e, dt, button, config) {
                  var selected = dt.rows( { selected: true } );
                  var count_selected = selected.indexes().length;
                  if (count_selected != 1) {
                     return;
                  }
                  var url = "";
                  var first = true;
                  $.each(selected.data(), function(index, elt){
                     if (! first) return false;
                     url = "{{server_url}}/{{object_type}}_form/" + encodeURIComponent(elt._id) + "{{'?is_template=1' if dt.templates else ''}}";
                  });
                  window.setTimeout(function(){
                     window.location.href = url;
                  }, 50);
               }
            }
            ,{
               extend: 'selectedSingle',
               text: "{{! _('<span class=\'text-warning fa fa-trash-o\'></span>')}}",
               titleAttr: "{{_('Delete the selected item')}}",
               className: 'btn-raised btn-xs',
               action: function (e, dt, button, config) {
                  var selected = dt.rows( { selected: true } );
                  var count_selected = selected.indexes().length;
                  if (count_selected != 1) {
                     return;
                  }
                  var url = "";
                  var first = true;
                  $.each(selected.data(), function(index, elt){
                     if (! first) return false;
                     url = "{{server_url}}/{{object_type}}/" + encodeURIComponent(elt._id) + "/delete";
                  });
                  window.setTimeout(function(){
                     window.location.href = url;
                  }, 50);
               }
            }
            %end
            %if dt.commands and not dt.templates:
            // Only for tables with 'commands' attribute (eg. livestate)
            ,{
               extend: 'collection',
               text: "{{! _('<span class=\'fa fa-bolt\'></span>')}}",
               className: 'btn-raised btn-xs',
               buttons: [
                  {
                     extend: 'selected',
                     text: "{{_('Re-check')}}",
                     titleAttr: "{{_('Force a re-check for selected items')}}",
                     className: 'btn-raised btn-xs',
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        if (selected.indexes().length == 0) {
                           return;
                        }
                        var url = "/recheck/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           if (! first) url += '&';
                           var elt_name = elt.DT_RowData.object_{{object_type}};
                           if ('{{object_type}}' == 'service') {
                              elt_name = elt.DT_RowData.object_host + '/' + elt_name;
                           }
                           url += 'element_id='+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name)+'&elements_type={{object_type}}';
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     },
                  }
                  ,
                  {
                     extend: 'selected',
                     text: "{{_('Acknowledge')}}",
                     titleAttr: "{{_('Acknowledge selected items')}}",
                     className: 'btn-raised btn-xs',
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        if (selected.indexes().length == 0) {
                           return;
                        }
                        var url = "/acknowledge/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           if (! first) url += '&';
                           var elt_name = elt.DT_RowData.object_{{object_type}};
                           if ('{{object_type}}' == 'service') {
                              elt_name = elt.DT_RowData.object_host + '/' + elt_name;
                           }
                           url += 'element_id='+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name)+'&elements_type={{object_type}}';
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     },
                  }
                  ,
                  {
                     extend: 'selected',
                     text: "{{_('Downtime')}}",
                     titleAttr: "{{_('Schedule a downtime for selected items')}}",
                     className: 'btn-raised btn-xs',
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        if (selected.indexes().length == 0) {
                           return;
                        }
                        var url = "/downtime/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           if (! first) url += '&';
                           var elt_name = elt.DT_RowData.object_{{object_type}};
                           if ('{{object_type}}' == 'service') {
                              elt_name = elt.DT_RowData.object_host + '/' + elt_name;
                           }
                           url += 'element_id='+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name)+'&elements_type={{object_type}}';
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     },
                  }
                  ,
                  {
                     extend: 'selected',
                     text: "{{_('Command')}}",
                     titleAttr: "{{_('Notify a command for the selected items')}}",
                     className: 'btn-raised btn-xs',
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        if (selected.indexes().length == 0) {
                           return;
                        }
                        var url = "/command/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           if (! first) url += '&';
                           var elt_name = elt.DT_RowData.object_{{object_type}};
                           if ('{{object_type}}' == 'service') {
                              elt_name = elt.DT_RowData.object_host + '/' + elt_name;
                           }
                           url += 'element_id='+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name)+'&elements_type={{object_type}}';
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     },
                  }
               ],
            }
            %end
            %if dt.is_templated:
            ,{
               %if dt.templates:
               text: "{{! _('<span class=\'fa fa-square\'></span>')}}",
               titleAttr: "{{_('Navigate to the %ss table' % object_type)}}",
               action: function (e, dt, button, config) {
                  if (debugTable) console.log('Navigate to the {{object_type}} table!');
                  window.location.href = "/{{object_type}}s/table";
               },
               %else:
               text: "{{! _('<span class=\'fa fa-clone\'></span>')}}",
               titleAttr: "{{_('Navigate to the %ss templates table' % object_type)}}",
               action: function (e, dt, button, config) {
                  if (debugTable) console.log('Navigate to the {{object_type}} templates table!');
                  window.location.href = "/{{object_type}}s/templates/table";
               },
               %end
               className: 'btn-raised btn-xs'
            }
            %end
            %if dt.recursive:
            ,{
               text: "{{! _('<span class=\'fa fa-sitemap\'></span>')}}",
               titleAttr: "{{_('Navigate to the tree view')}}",
               action: function (e, dt, button, config) {
                  if (debugTable) console.log('Navigate to the tree view for {{object_type}}!');
                  window.location.href = "/{{object_type}}s/tree";
               },
               className: 'btn-raised btn-xs'
            }
            %end
         ]
      });

      %if dt.responsive:
      $('#tbl_{{table_id}}').on( 'responsive-resize.dt', function ( e, datatable, columns ) {
         var table = $('#tbl_{{table_id}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, responsive resize...');

         $.each(columns, function(index, visibility){
            if (visibility == false) {
               // Update search filter input field value
               $('#filterrow th[data-index="'+index+'"]').css({
                  display: "none"
               });
            }
            if (visibility == true) {
               // Update search filter input field value
               $('#filterrow th[data-index="'+index+'"]').css({
                  display: "table-cell"
               });
            }
         });
         // Recalculate columns and table width
         if (debugTable) console.debug('Datatable event, responsive resize... recalculate columns and table width');
         table.columns.adjust()
         table.responsive.recalc();
      });
      %end
   });
 </script>
