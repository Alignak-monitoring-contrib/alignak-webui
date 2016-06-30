%import json

%# embedded is True if the table is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%setdefault('commands', False)
%setdefault('object_type', 'unknown')

%from bottle import request
%search_string = request.query.get('search', '')

%if not embedded:
%# Datatables js and css are included in the page layout
%rebase("layout", title=title, page="/{{object_type}}_table")
%end

<style>
/* Set smaller font for table content */
tbody > tr {
   font-size:11px;
}
/* Modal opening button position adjusted */
table.dataTable.dtr-inline.collapsed>tbody>tr>td:first-child:before, table.dataTable.dtr-inline.collapsed>tbody>tr>th:first-child:before {
   top: 3px;
}
/* Selected line */
table.dataTable tbody>tr.selected,
table.dataTable tbody>tr>.selected {
   background-color:#FAF3CD; color: black;
}
</style>

%if dt.editable:
%include("_edition.tpl")
%end

<!-- Table display -->
<div id="{{object_type}}_table" class="alignak_webui_table {{'embedded' if embedded else ''}}">
   <!-- Bootstrap responsive table
   <div class="table-responsive"> -->
      <table id="tbl_{{object_type}}" class="table table-striped table-condensed dt-responsive">
         <thead>
            <tr>
               %for column in dt.table_columns:
               <th data-name="{{ column['data'] }}" data-type="{{ column['type'] }}">{{ column['title'] }}</th>
               %end
            </tr>
            %if dt.searchable:
            <tr id="filterrow">
               %idx=0
               %for column in dt.table_columns:
                  <th data-index="{{idx}}" data-name="{{ column['data'] }}"
                      data-regex="{{ column['regex'] }}" data-size="{{ column['size'] }}"
                      data-type="{{ column['type'] }}" data-format="{{ column['format'] }}"
                      data-allowed="{{ column['allowed'] }}" data-searchable="{{ column['searchable'] }}">
                  </th>
                  %idx += 1
               %end
            </tr>
            %end
         </thead>
         <tbody>
         </tbody>
      </table>
   <!--
   </div>
    -->
</div>

<script>
   var debugTable = false;
   var where = {{! json.dumps(where)}};
   var columns = '';
   var selectedRows = [];

   $(document).ready(function() {
      $.ajaxSetup({
         headers: { "Authorization": "Basic " + btoa('{{credentials}}') }
      });

      %if dt.searchable:
      // Setup - add a text/select input to each search cell
      $('#tbl_{{object_type}} thead tr#filterrow th').each( function () {
         // Beware to only add one element that is the edit field ...
         // or change the stateLoadCallback restore processing!
         var title = $('#tbl_{{object_type}} thead th').eq( $(this).index() ).text();

         if ($(this).data('searchable') != 'True') {
            if (debugTable) console.log('Do not search for field: ' + $(this).data('name'));
            return;
         }

         if ($(this).data('format')=='select') {
            var html = '<select><option value=""></option>';
            var allowed = $(this).data('allowed').split(',');
            $.each(allowed, function(idx){
               html += '<option value="'+allowed[idx]+'">'+allowed[idx]+'</option>'
            });
            html += '</select>';
            $(this).html( html );
         } else {
            // Simple input field
            var html = '<input size="'+$(this).data('size')+'" type="text" data-regex="'+$(this).data('regex')+'" placeholder="'+title+'" />';
            if ($(this).data('type')=='integer') {
               html = '<input size="'+$(this).data('size')+'" type="number" placeholder="'+title+'" />';
            } else if ($(this).data('type')=='email') {
               html = '<input size="'+$(this).data('size')+'" type="email" placeholder="'+title+'" />';
            }
            $(this).html( html );
         }
      });
      // Apply the search filter for input fields
      $("#tbl_{{object_type}} thead input").on('keyup change', function () {
         if (debugTable) console.debug('Datatable event, text column search ...');

         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         table
            .column( $(this).parent().index()+':visible' )
               .search($(this).val(), $(this).data('regex')=='True', false)
               .draw();

         // Enable the clear filter button
         table.buttons('clearFilter:name').enable();
      });

      // Apply the search filter for selectable fields
      $("#tbl_{{object_type}} thead select").on('change', function () {
         if (debugTable) console.debug('Datatable event, selectable column search ...', table);

         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         table
            .column( $(this).parent().index() )
              .search($(this).val(), false, false)
              .draw();

         // Enable the clear filter button
         table.buttons('clearFilter:data').enable();
      });
      %end

      $('#tbl_{{object_type}}').on( 'xhr.dt', function () {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         var json = table.ajax.json();
         /*
         if (debugTable) console.debug('Datatable event, xhr, url: ' + table.ajax.url());
         if (debugTable) console.debug('Datatable event, xhr, json: ' + table.ajax.json());
         if (debugTable) console.debug('Datatable event, xhr, data: ' + json.data);
         */
         if (debugTable) console.debug('Datatable event, xhr, ' + json);
         if (debugTable) console.debug('Datatable event, xhr, ' + json.data.length +' row(s) loaded');
      });

      $('#tbl_{{object_type}}').on( 'draw.dt', function () {
         if (debugTable) console.debug('Datatable event, draw ...');
      });

      $('#tbl_{{object_type}}').on( 'column-sizing.dt', function () {
         if (debugTable) console.debug('Datatable event, column-sizing ...');
      });

      $('#tbl_{{object_type}}').on( 'error.dt', function ( e, settings ) {
         if (debugTable) console.error('Datatable event, error ...');
      });

      $('#tbl_{{object_type}}').on( 'init.dt', function ( e, settings ) {
         if (debugTable) console.debug('Datatable event, init ...');
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });

         %if dt.selectable:
         if (table.rows( { selected: true } ).count() > 0) {
             $('[data-reaction="selection-not-empty"]').prop('disabled', false);
             $('[data-reaction="selection-empty"]').prop('disabled', true);
         } else {
             $('[data-reaction="selection-not-empty"]').prop('disabled', true);
             $('[data-reaction="selection-empty"]').prop('disabled', false);
         }
         %end
      });

      %if dt.selectable:
      $('#tbl_{{object_type}}').on( 'select.dt', function ( e, dt, type, indexes ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, selected row ...');

         var rowData = table.rows( indexes ).data().toArray();
         if (debugTable) console.debug('Datatable event, selected: ', rowData);

         if (table.rows( { selected: true } ).count() > 0) {
             $('[data-reaction="selection-not-empty"]').prop('disabled', false);
             $('[data-reaction="selection-empty"]').prop('disabled', true);
         } else {
             $('[data-reaction="selection-not-empty"]').prop('disabled', true);
             $('[data-reaction="selection-empty"]').prop('disabled', false);
         }
      });

      $('#tbl_{{object_type}}').on( 'deselect.dt', function ( e, dt, type, indexes ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, deselected row ...');

            var rowData = table.rows( indexes ).data().toArray();
            if (debugTable) console.debug('Datatable event, deselected: ', rowData);

            if (table.rows( { selected: true } ).count() > 0) {
                $('[data-reaction="selection-not-empty"]').prop('disabled', false);
                $('[data-reaction="selection-empty"]').prop('disabled', true);
            } else {
                $('[data-reaction="selection-not-empty"]').prop('disabled', true);
                $('[data-reaction="selection-empty"]').prop('disabled', false);
            }
      });
      %end

      $('#tbl_{{object_type}}').on( 'stateLoaded.dt', function ( e, settings, data ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, state loaded ...');

         // Enable the clear filter button
         table.buttons('clearFilter:data').disable();

         // Update each search field with the received value
         $.each(data.columns, function(index, value) {
            if (value['search']['search'] != "") {
               if (debugTable) console.debug('Update column', index, value['search']['search']);
               // Update search filter input field value
               $('#filterrow th[data-index="'+index+'"]').children().val(value['search']['search']);

               // Enable the clear filter button
               table.buttons('clearFilter:data').enable();
            }
         });

         // Update each search field with the filter URL parameters
         $.each(where, function(key, value) {
            var index = table.column(key+':name').index();
            if (debugTable) console.debug('Update column search', index, key, value);

            // Update search filter input field value
            $('#filterrow th[data-index="'+index+'"]').children().val(value).trigger('change');
         });
      });

      // Table declaration
      var table = $('#tbl_{{object_type}}').DataTable( {
         // Disable automatic width calculation
         "autoWidth": false,

         // Pagination
         "paging": {{'true' if dt.paginable else 'false'}},
         "pagingType": "full_numbers",

         // Pagination
         "lengthChange": true,
         "pageLength": 25,
         "lengthMenu": [ 5, 10, 25, 50, 75, 100, '-1' ],
         "lengthMenu": [
            [ 10, 25, 50, 100, -1 ],
            [
               "{{_('10 rows')}}", "{{_('25 rows')}}", "{{_('50 rows')}}",
               "{{_('100 rows')}}", "{{_('Show all')}}"
            ]
         ],

         // Table information
         "info": true,
         /* Table fixed header - do not activate because table scrolling is not compatible
         "fixedHeader": true, */

         // Server side processing: request new data
         "serverSide": true,
         "ajax": {
            "url": "{{links}}{{'/external/table/' + identifier if embedded else ''}}/{{object_type}}_table_data",
            "type": "POST",
            //"dataSrc": "data",
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
                     var data = row.data();
                     console.log(data.data)
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

         // Table columns definition
         "columns": {{ ! json.dumps(dt.table_columns) }},

         // Table state saving/restoring
         stateSave: true,
         // Saved parameters
         "stateSaveParams": function (settings, data) {
            if (debugTable) console.debug("state saved data", data);
            // Ignore global search parameter ...
            data.search.search = "";
         },
         // Load table configuration
         stateLoadCallback: function (settings) {
            if (debugTable) console.debug("state loading for 'tbl_{{object_type}}' ...");

            // Get table stored state from the server ...
            var o;
            $.ajax( {
               "url": "{{links}}{{'/external/table/' + identifier if embedded else ''}}/preference/user",
               "dataType": "json",
               "type": "GET",
               "data": {
                  "key": '{{object_type}}_table'
               },
               "async": false,
               "success": function (json) {
                  if (debugTable) console.debug("state restored for 'tbl_{{object_type}}' ...", json);
                  o = json;
               }
            });

            return o;
         },
         // Save table configuration
         stateSaveCallback: function (settings, data) {
            if (debugTable) console.debug("state saving for 'tbl_{{object_type}}' ...", settings, data);

            // Post table data to the server ...
            $.ajax({
               "url": "{{links}}{{'/external/table/' + identifier if embedded else ''}}/preference/user",
               "dataType": "json",
               "type": "POST",
               "data": {
                  "key": '{{object_type}}_table',
                  // Json stringify to avoid complex array formatting ...
                  "value": JSON.stringify( data )
               },
               "success": function () {
                  if (debugTable) console.debug("state saved for 'tbl_{{object_type}}' ...", settings, data);
               }
            });
         },

         // Each created row ...
         createdRow: function (row, data, index) {
            //var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
            //if (debugTable) console.debug('Datatable createdRow, table: ', table);
            //if (debugTable) console.debug('Datatable createdRow, row: ', row);
            if (debugTable) console.debug('Datatable createdRow, data: ', data);

            if ('{{dt.id_property}}' in data) {
               var name_node = table.cell(index, 'data:name').node();
               if (debugTable) console.debug('Datatable createdRow, name: ', data.data);
            }

            if ('{{dt.name_property}}' in data) {
               var name_node = table.cell(index, 'data:name').node();
               if (debugTable) console.debug('Datatable createdRow, name: ', data.data, name_node);
               // The node descendants should contain some information about the element
               /*
               <a href="host/575422f64c988c217b0b1c50">
               <div class="item-state item_hostUnknown " style="display: inline; font-size:0.9em;" data-item-id="575422f64c988c217b0b1c50" data-item-name="webui" data-item-type="host">
               <span class="fa-stack"  title="Host is unknown"><i class="fa fa-circle fa-stack-2x item_hostUnknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span>
               <span>webui</span>
               </div></a>
                */
               var id = $(name_node).find('[data-item-id]').data('item-id');
               var type = $(name_node).find('[data-item-type]').data('item-type');
               var name = $(name_node).find('[data-item-name]').data('item-name');
               var state = $(name_node).find('[data-item-state]').data('item-state');
               console.log(type, id, name)
            }

            if ('{{dt.status_property}}' in data) {
               var status_node = table.cell(index, 'data:name').node();
               if (debugTable) console.debug('Datatable createdRow, name: ', data.data, status_node);
               // The node descendants should contain some information about the element
               /*
               <a href="host/575422f64c988c217b0b1c50">
               <div class="item-state item_hostUnknown " style="display: inline; font-size:0.9em;" data-item-id="575422f64c988c217b0b1c50" data-item-name="webui" data-item-type="host">
               <span class="fa-stack"  title="Host is unknown"><i class="fa fa-circle fa-stack-2x item_hostUnknown"></i><i class="fa fa-question fa-stack-1x fa-inverse"></i></span>
               <span>webui</span>
               </div></a>
                */
               var id = $(status_node).find('[data-item-id]').data('item-id');
               var type = $(status_node).find('[data-item-type]').data('item-type');
               var name = $(status_node).find('[data-item-name]').data('item-name');
               var state = $(status_node).find('[data-item-state]').data('item-state');
               console.log(type, id, name)
            }
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
         */
         dom: "<'row'<'col-sm-8'B><'col-sm-4'f>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-5'i><'col-sm-7'p>>",
         // Table columns visibility button
         buttons: [
            {
                 extend: 'pageLength'
            }
            ,{
                 extend: 'colvis'
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
               }
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
                     title: table,
                     extension: ".csv",
                     exportOptions: {
                        columns: ':visible',
                        modifier: {
                           search: 'none'
                        }
                     }
                  }
                  ,
                  {
                     extend: 'excel',
                     header: true,
                     footer: false,
                     title: table,
                     extension: ".xlsx",
                     exportOptions: {
                        columns: ':visible',
                        modifier: {
                           search: 'none'
                        }
                     }
                  }
                  ,
                  {
                     extend: 'pdf',
                     header: true,
                     footer: false,
                     title: table,
                     extension: ".pdf",
                     orientation: 'landscape',
                     pageSize: 'A4',
                     exportOptions: {
                        columns: ':visible',
                        modifier: {
                           search: 'none'
                        }
                     }
                  }
               ]
            }
            %end
            %if dt.searchable:
            ,{
               name: 'clearFilter',
               text: '<span id="clearFilter" class="fa-stack" style="font-size:0.63em;"><i class="fa fa-filter"></i><i class="fa fa-ban fa-stack-2x text-danger"></i></span>',
               titleAttr: "{{_('Reset all the search filters')}}",
               action: function ( e, dt, node, data ) {
                  // Reset table columns search
                  table
                     .columns()
                        .search('', false, false)
                        .draw();

                  // Clear the search fields
                  // Update search filter input field value
                  $('#filterrow th').children().val('');

                  // Disable the clear filter button
                  table.buttons('clearFilter:name').disable();
               }
            }
            %end
            %if dt.selectable:
            /*
            ,{
               extend: 'selected',
               text: 'Count selected rows',
               action: function (e, dt, button, config) {
                  alert( dt.rows( { selected: true } ).indexes().length +' row(s) selected' );
               }
            }
            ,{
               extend: 'selected',
               text: 'Count selected rows 2',
               action: function (e, dt, button, config) {
                  alert( dt.rows( { selected: true } ).indexes().length +' row(s) selected !' );
               }
            }
            ,{
               extend: 'selectedSingle',
            }
            */
            ,{
               extend: 'selectAll',
            }
            ,{
               extend: 'selectNone',
            }
            /*
            ,{
               extend: 'selectRows',
            }
            ,{
               extend: 'selectColumns',
            }
            ,{
               extend: 'selectCells'
            }
            */
            %end
            %if dt.commands:
            // Only for tables with 'commands' attribute (eg. livestate)
            ,{
               extend: 'collection',
               text: "{{! _('<span class=\'fa fa-bolt\'></span>')}}",
               buttons: [
                  {
                     extend: 'selected',
                     text: "{{_('Re-check')}}",
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        var count_selected = selected.indexes().length;
                        if (count_selected == 0) {
                           return;
                        }
                        var url = "/recheck/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           var elt_name = elt.display_name_host;
                           if (elt.type == 'service') {
                              elt_name += ' (' + elt.display_name_service + ')';
                           }
                           if (! first) url += '&';
                           url += "livestate_id="+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name);
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     }
                  }
                  ,
                  {
                     extend: 'selected',
                     text: "{{_('Acknowledge')}}",
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        var count_selected = selected.indexes().length;
                        if (count_selected == 0) {
                           return;
                        }
                        var url = "/acknowledge/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           var elt_name = elt.display_name_host;
                           if (elt.type == 'service') {
                              elt_name += ' (' + elt.display_name_service + ')';
                           }
                           if (! first) url += '&';
                           url += "livestate_id="+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name);
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     }
                  }
                  ,
                  {
                     extend: 'selected',
                     text: "{{_('Downtime')}}",
                     action: function (e, dt, button, config) {
                        // Fix for datatable that do not close dropdown immediatly...
                        $(".dt-button-background").trigger("click");
                        var selected = dt.rows( { selected: true } );
                        var count_selected = selected.indexes().length;
                        if (count_selected == 0) {
                           return;
                        }
                        var url = "/downtime/form/add?";
                        var first = true;
                        $.each(selected.data(), function(index, elt){
                           var elt_name = elt.display_name_host;
                           if (elt.type == 'service') {
                              elt_name += ' (' + elt.display_name_service + ')';
                           }
                           if (! first) url += '&';
                           url += "livestate_id="+encodeURIComponent(elt._id)+'&element_name='+encodeURIComponent(elt_name);
                           if (first) first = false;
                        });
                        window.setTimeout(function(){
                           display_modal(url);
                        }, 50);
                     }
                  }
               ]
            }
            %end
         ]
      });

      %if dt.responsive:
      $('#tbl_{{object_type}}').on( 'responsive-resize.dt', function ( e, datatable, columns ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, responsive resize...');

         $.each(columns, function(index, visibility){
            if (visibility == false) {
               // Update search filter input field value
               $('#filterrow th[data-index="'+index+'"]').css({
                  width : "0px",
                  display: "none"
               });
            }
            if (visibility == true) {
               // Update search filter input field value
               $('#filterrow th[data-index="'+index+'"]').css({
                  width : "10px",
                  display: "table-cell"
               });
            }
         });
         // Recalculate columns and table width
         if (debugTable) console.debug('Datatable event, state loaded ... recalculate columns and table width');
         table.columns.adjust()
         table.responsive.recalc();
      });
      %end
   });
 </script>
