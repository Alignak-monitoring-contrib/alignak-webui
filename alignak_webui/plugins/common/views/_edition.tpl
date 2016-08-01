<div class="container">
   <div class="row">
      <div id="justified-button-bar" class="col-sm-12">
         <div class="btn-group btn-group-justified">
            <div class="btn-group">
               <button title="Edit an element"
                       type="button" class="btn btn-default"
                       data-reaction="selection-not-empty"
                       data-action="edit-element">
                  <span class="fa fa-plus-square"></span>&nbsp; Edit an element
               </button>
            </div>
            <div class="btn-group">
               <button title="Add an element"
                       type="button" class="btn btn-default"
                       data-action="add-element">
                  <span class="fa fa-plus-square"></span>&nbsp; Add an element
               </button>
            </div>
            <div class="btn-group">
               <button title="Delete selected elements"
                       type="button" class="btn btn-default"
                       data-reaction="selection-not-empty"
                       data-action="delete-selection">
                  <span class="fa fa-plus-square"></span>&nbsp; Delete selected elements
               </button>
            </div>
            <div class="btn-group">
               <button title="Select all elements"
                       type="button" class="btn btn-default"
                       data-reaction="selection-empty"
                       data-action="select-all" >
                  <span class="fa fa-plus-square"></span>&nbsp; Select all elements
               </button>
            </div>
            <div class="btn-group">
               <button title="Unselect all elements"
                       type="button" class="btn btn-default"
                       data-reaction="selection-not-empty"
                       data-action="unselect-all" >
                  <span class="fa fa-plus-square"></span>&nbsp; Unselect all elements
               </button>
            </div>
         </div>
      </div>
   </div>
</div>

<script>
$(document).ready(function() {
    // Edit an element
    $('body').on('click', '[data-action="edit-element"]', function (e) {
        var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
        if (debugJs) console.debug('Datatable, edit first selected element ...');

        // Iterate selected rows
        table.rows( { selected: true } ).every( function () {
            var data = this.data();
            if (! data) return false;

            if (debugJs) console.debug('Navigate to: /{{object_type}}s/'+data["{{object_type}}_name"]);
            $(location).attr('href', '/{{object_type}}s/'+data["{{object_type}}_name"]);
        });
    });

    // Add a new element
    $('body').on('click', '[data-action="add-element"]', function (e) {
        $(location).attr('href', '/{{object_type}}s?action=add');
    });

    // Select all elements
    $('body').on('click', '[data-action="select-all"]', function (e) {
        var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
        if (debugJs) console.debug('Datatable, select all elements ...');

        // Iterate selected rows
        table.rows().select();
    });

    // Unselect all elements
    $('body').on('click', '[data-action="unselect-all"]', function (e) {
        var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
        if (debugJs) console.debug('Datatable, unselect all elements ...');

        // Iterate selected rows
        table.rows().deselect();
    });

    // Delete selected elements
    $('body').on('click', '[data-action="delete-selection"]', function (e) {
        var table = $('#tbl_{{object_type}}').DataTable({ retrieve: true });
        if (debugJs) console.debug('Datatable, delete selected elements ...');

        // Iterate selected rows
        table.rows( { selected: true } ).every( function () {
            var data = this.data();
            if (! data) return false;

            if (debugJs) console.debug('Selected row: ', data);
            if (debugJs) console.debug('Name: ', data["{{object_type}}_name"]);
            $.ajax({
                url: "/{{object_type}}s/"+data["{{object_type}}_name"],
                method: "delete",
                dataType: "json"
            })
            .done(function(html, textStatus, jqXHR) {
                user_notification("Element '"+data["{{object_type}}_name"]+"' deleted.", "success", 5, function() {
                    // Navigate ...
                    $(location).attr('href', '/{{object_type}}s');
                });
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
                user_notification(jqXHR.responseText, "error", 5, function() {
                    // Navigate ...
                    $(location).attr('href', '/{{object_type}}s');
                });
            })
            .always(function() {
            });
        });
    });
});
</script>
