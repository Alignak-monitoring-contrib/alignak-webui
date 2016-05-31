%import json

%setdefault('commands', True)
%setdefault('object_type', 'unknown')

%from bottle import request
%search_string = request.query.get('search', '')

%# Datatables js and css are included in the page layout
%rebase("layout", title=title, page="/{{object_type}}_table")

<!-- Table display -->
<div id="{{object_type}}_table">
   <!-- Bootstrap responsive table
   <div class="table-responsive"> -->
      <table id="tbl_{{object_type}}" class="table table-striped table-condensed dt-responsive nowrap" cellspacing="0" width="100%">
         <thead>
            <tr>
               %for column in dt.table_columns:
               <th data-name="{{ column['name'] }}" data-type="{{ column['type'] }}">{{ column['title'] }}</th>
               %end
            </tr>
            %if dt.searchable:
            <tr id="filterrow">
               %idx=0
               %for column in dt.table_columns:
                  <th data-index="{{idx}}" data-name="{{ column['name'] }}"
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
   var columns = {{ ! json.dumps(dt.table_columns) }};
   var selectedRows = [];

   $(document).ready(function() {
      set_current_page("{{ webui.get_url(request.route.name) }}");

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

         table
            .column( $(this).parent().index()+':visible' )
               .search($(this).val(), $(this).data('regex')=='True', false)
               .draw();

         // Enable the clear filter button
         table.buttons('clearFilter:name').enable();
      });

      // Apply the search filter for selectable fields
      $("#tbl_{{object_type}} thead select").on('change', function () {
         if (debugTable) console.debug('Datatable event, selectable column search ...');

         table
            .column( $(this).parent().index()+':visible' )
              .search($(this).val(), false, false)
              .draw();

         // Enable the clear filter button
         table.buttons('clearFilter:name').enable();
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
      });

      $('#tbl_{{object_type}}').on( 'select.dt', function ( e, dt, type, indexes ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, selected row ...');
      });

      $('#tbl_{{object_type}}').on( 'deselect.dt', function ( e, dt, type, indexes ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, deselected row ...');
      });

      $('#tbl_{{object_type}}').on( 'stateLoaded.dt', function ( e, settings, data ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, state loaded ...');

         // Enable the clear filter button
         table.buttons('clearFilter:name').disable();

         // Update each search field with the received value
         $.each(data.columns, function(index, value) {
            if (value['search']['search'] != "") {
               if (debugTable) console.debug('Update column', index, value['search']['search']);
               // Update search filter input field value
               $('#filterrow th[data-index="'+index+'"]').children().val(value['search']['search']);

               // Enable the clear filter button
               table.buttons('clearFilter:name').enable();
            }
         });
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
         "lengthMenu": [ 5, 10, 25, 50, 75, 100 ],

         // Table information
         "info": true,
         /* Table fixed header - do not activate because table scrolling is not compatible
         "fixedHeader": true, */
         // Table ordering
         "ordering": {{'true' if dt.orderable else 'false'}},
         // First row for ordering
         "orderCellsTop": true,
         // Default initial sort
         "order": [[1, 'asc']],

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
               , display: $.fn.dataTable.Responsive.display.modal( {
                  header: function ( row ) {
                     var data = row.data();
                     return ('{{_('Details for %s') % object_type}}');
                  }
                })
               , renderer: $.fn.dataTable.Responsive.renderer.tableAll( {
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
         select: true,

         // Server side processing: request new data
         "columns": columns,
         "serverSide": true,
         "ajax": {
            "url": "/{{object_type}}_table_data",
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
            // Ignore global search parameter ...
            data.search.search = "";
         },
         // Load table configuration
         stateLoadCallback: function (settings) {
            if (debugTable) console.debug("state loading for 'tbl_{{object_type}}' ...");

            // Get table stored state from the server ...
            var o;
            $.ajax( {
               "url": "/contact/preference",
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
               "url": "/contact/preference",
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
            B - buttons
            l - length changing input control
            f - filtering input
            t - The table!
            i - Table information summary
            p - pagination control
            r - processing display element
         dom: 'Blfrtip',
         */
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
         ]
      });

      %if dt.responsive:
      $('#tbl_{{object_type}}').on( 'responsive-resize.dt', function ( e, datatable, columns ) {
         var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
         if (debugTable) console.debug('Datatable event, responsive resize...');

         $.each(columns, function(index, visibility){
            if (debugTable) console.debug('Column: '+index+', visibility: '+visibility);
            console.log( index, visibility );
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
         console.debug('Datatable event, state loaded ... recalculate columns and table width');
         table.columns.adjust()
         table.responsive.recalc();
      });
      %end
   });
 </script>
