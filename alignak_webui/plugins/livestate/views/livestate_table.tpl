%import json

%setdefault('commands', True)
%setdefault('object_type', 'livestate')

%from bottle import request
%search_string = request.query.get('search', '')

%# Datatables js and css are included in the page layout
%rebase("layout", title=title, page="/livestate_table")

<!-- livestate filtering and display -->
<div id="livestate_table">
   <table id="tbl_{{object_type}}" class="table table-striped" cellspacing="0" width="100%">
      <thead>
         <tr>
            %for column in dt.table_columns:
            <th data-name="{{ column['name'] }}" data-type="{{ column['type'] }}">{{ column['title'] }}</th>
            %end
         </tr>
         %if dt.searchable:
         <tr id="filterrow">
            %for column in dt.table_columns:
            <th data-name="{{ column['name'] }}" data-regex="{{ column['regex'] }}" data-type="{{ column['type'] }}" data-format="{{ column['format'] }}" data-allowed="{{ column['allowed'] }}" data-searchable="{{ column['searchable'] }}"></th>
            %end
         </tr>
         %end
      </thead>
      <tbody>
      </tbody>
   </table>
</div>

<script>
   var debugTable = false;
   var column_links = {{ ! json.dumps(dt.table_links) }};
   var columns = {{ ! json.dumps(dt.table_columns) }};
   var selectedRows = [];

   $(document).ready(function() {
      set_current_page("{{ webui.get_url(request.route.name) }}");

      %if dt.searchable:
      // Setup - add a text input to each search cell
      $('#tbl_{{object_type}} thead tr#filterrow th').each( function () {
         var title = $('#tbl_{{object_type}} thead th').eq( $(this).index() ).text();

         if ($(this).data('searchable')!='True') {
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
            var html = '<input type="text" data-regex="'+$(this).data('regex')+'" placeholder="'+title+'" />';
            if ($(this).data('type')=='integer') {
               html = '<input type="number" placeholder="'+title+'" />';
            } else if ($(this).data('type')=='email') {
               html = '<input type="email" placeholder="'+title+'" />';
            }
            $(this).html( html );
         }
      });
      // Apply the search filter for input fields
      $("#tbl_{{object_type}} thead input").on('keyup change', function () {
         if (debugTable) console.debug('Datatable event, column search ...');

         table
            .column( $(this).parent().index()+':visible' )
               .search($(this).val(), $(this).data('regex')=='True', false)
               .draw();
      });

      // Apply the search filter for selectable fields
      $("#tbl_{{object_type}} thead select").on('change', function () {
         if (debugTable) console.debug('Datatable event, selectable column search ...');

         table
            .column( $(this).parent().index()+':visible' )
              .search($(this).val(), false, false)
              .draw();
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
         if (debugTable) console.debug('Datatable event, xhr, ' + json.data.length +' row(s) loaded');
      });

      $('#tbl_{{object_type}}').on( 'draw.dt', function () {
         if (debugTable) console.debug('Datatable event, draw ...');
      });

      $('#tbl_{{object_type}}').on( 'error.dt', function ( e, settings ) {
         if (debugTable) console.error('Datatable event, error ...');
      });

      $('#tbl_{{object_type}}').on( 'init.dt', function ( e, settings ) {
         if (debugTable) console.debug('Datatable event, init ...');
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         /*
         if (debugTable) console.debug('Datatable createdRow, row: ' + row);
         if (debugTable) console.debug('Datatable createdRow, data: ' + data);
         if (debugTable) console.debug('Datatable createdRow, index: ' + index);
         */

         if (table.rows( { selected: true } ).count() > 0) {
            $('[data-reaction="selection-not-empty"]').prop('disabled', false);
            $('[data-reaction="selection-empty"]').prop('disabled', true);
         } else {
            $('[data-reaction="selection-not-empty"]').prop('disabled', true);
            $('[data-reaction="selection-empty"]').prop('disabled', false);
         }
      });

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

      // Table declaration
      var table = $('#tbl_{{object_type}}').DataTable( {
         // Table features
         // Language
         "language": {{! json.dumps(dt.get_language_strings())}},
         // Pagination
         "paging": {{'true' if dt.paginable else 'false'}},
         "pagingType": "full_numbers",

         // Page length
         "lengthChange": true,
         "pageLength": 25,
         "lengthMenu": [ 1, 5, 10, 25, 50, 75, 100 ],

         // Table information
         "info": true,
         // Table ordering
         "ordering": {{'true' if dt.orderable else 'false'}},
         // First row for ordering
         "orderCellsTop": true,

         // Responsive mode
         responsive: true,

         // Selection mode
         select: true,

         // Server side processing
         "columns": columns,
         "serverSide": true,
         "ajax": {
            "url": "/livestate_table_data",
            "type": "POST",
            "dataSrc": "data",
            "data": function ( d ) {
               // Add an extra field
               d = $.extend({}, d, { "object_type": '{{object_type}}' });
               // Json stringify to avoid complex array formatting ...
               d.columns = JSON.stringify( d.columns );
               d.search = JSON.stringify( d.search );
               d.order = JSON.stringify( d.order );
               return ( d );
            }
         },

         // Table state saving/restoring
         stateSave: true,
         // Saved parameters
         "stateSaveParams": function (settings, data) {
            if (debugTable) console.debug("state saved data", data);
            // Ignore global search parameters ...
            data.search.search = "";
         },
         // Load table configuration
         stateLoadCallback: function (settings) {
            if (debugTable) console.debug("state loading for 'tbl_{{object_type}}' ...");

            // Get table data from the server ...
            var o;
            $.ajax( {
               "url": "/user/preference",
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
               "url": "/user/preference",
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

         /*
         // Each created row ...
         createdRow: function ( row, data, index ) {
            var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         },
         */

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
         //dom: 'Blfrtip',
         //dom: 'B<"clearfix">flrtip',
         //dom: 'B<"clearfix">frtip',
         dom: "<'row'<'col-sm-6'B><'col-sm-6'f>>" + "<'row'<'col-sm-12'tr>>" + "<'row'<'col-sm-5'i><'col-sm-7'p>>",
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
         ]
      });
/*
   To be finalized
      // Specific filters
      yadcf.init(table, [{
         column_number: 0
      }, {
         column_number: 1,
         filter_type: "range_number_slider"
      }, {
         column_number: 2,
         filter_type: "date"
      }, {
         column_number: 3,
         filter_type: "auto_complete",
         text_data_delimiter: ","
      }, {
         column_number: 4,
         column_data_type: "html",
         html_data_type: "text",
         filter_default_label: "Select tag"
      }]);
*/
   });
 </script>
