%import json

%setdefault('debug', False)
%setdefault('tree_type', 'services')

%# When layout is False, this template is embedded
%setdefault('layout', True)
%# When in_host_view is True, list the services tree in the host view (do not include the host information)
%setdefault('in_host_view', False)

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/{{tree_type}}/tree")
%end

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command
%from alignak_webui.objects.item_host import Host

<style>
   // Get sure that jsTree context menu is visible ...
   .jstree-contextmenu {
       z-index: 1000;
   }

.vcenter {
    display: inline-block;
    vertical-align: middle;
    height: 40px;
}
</style>

<!-- Services tree display -->
<div id="{{tree_type}}s_tree_view">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_services"><i class="fa fa-bug"></i> Services as dictionaries</a>
            </h4>
         </div>
         <div id="collapse_services" class="panel-collapse collapse">
            <ul class="list-group">
               %for service in elts:
                  <li class="list-group-item"><small>Service: {{service}} - {{service.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(elts)}} elements</div>
         </div>
      </div>
   </div>
   %end

   %if not elts:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
   <div class="panel panel-default">
      %collapsed = datamgr.get_user_preferences(current_user, "services-tree", {'opened': False})
      <div class="panel-heading {{ 'collapsed' if not collapsed['opened'] else ''}}"
           data-action="save-panel" data-target="#services-tree" data-toggle="collapse"
           aria-expanded="{{ 'true' if collapsed['opened'] else 'false' }}">
         <span class="caret"></span>&nbsp;{{title}}
      </div>

      <div id="services-tree" class="panel-body panel-collapse {{ 'collapse' if not collapsed['opened'] else ''}}">
         <div class="row">
            <div class="col-sm-3 col-xs-12">
               <!-- Tree structure to display items -->
               <div id="{{tree_type}}_tree"></div>
            </div>
            <div id="right_panel" class="col-sm-9 col-xs-12">
               <div class="card alert alert-dismissible alert-info">
                  <button type="button" class="close" data-dismiss="alert">×</button>
                  <h4>{{_('Select an item in the tree to display more information.')}}</h4>
               </div>
               <script>
                  window.setTimeout(function() { $("#right_panel div.alert-dismissible").alert('close'); }, 3000);
               </script>
            </div>
         </div>
      </div>
   </div>
   %end
 </div>

<script>
   var debugTree = {{'true' if debug else 'false'}};

   // Build tree data...
   var jsTreeData = [];
   %for item in tree_items:
      jsTreeData.push({{! json.dumps(item)}})
   %end

   $(document).ready(function(){
      $("#{{tree_type}}_tree")
         .jstree({
            "core" : {
               "check_callback" : true,   // Allow to change the tree
               "data" : jsTreeData
            },
            "plugins" : [
               "state",
               "sort"
            ],
            "state": {
               "key": "{{tree_type}}_tree",
               "filter": function(state) {
                  if (debugTree) console.log('Restoring saved state: ', state);
               }
            }
         })
         .bind('ready.jstree', function(e, data) {
            var o_{{tree_type}}_tree = $("#{{tree_type}}_tree").jstree(true);
            if (debugTree) console.log('{{tree_type}} tree ready!');
         })

         .bind('changed.jstree', function(event, action) {
            if (debugTree) console.log('Changed :', action.action, action.node);

            if (action.action == 'select_node') {
               if (debugTree) console.log('Selected :', action.node);

               if (action.node.data.type == '{{tree_type}}') {
                  wait_message('{{_('Loading service information...')}}', true);

                  $("#right_panel").slideUp(50, function() {
                     $(this).empty();

                     var o = $('<div class="card" style="padding:10px;">')
                        .appendTo('#right_panel');

                     $.ajax({
                        url: '/external/'+action.node.data.type+'/'+action.node.id+'/information'
                     })
                     .done(function(content, textStatus, jqXHR) {
                        $('#right_panel div.card').html(content);

                        $("#right_panel")
                           .slideDown('slow');
                     })
                     .fail(function( jqXHR, textStatus, errorThrown ) {
                        console.error('get tree element, error: ', jqXHR, textStatus, errorThrown);
                        raise_message_ko(errorThrown + ': '+ textStatus);
                     })
                     .always(function() {
                        wait_message('', false)
                     });
                  });
               }
            }
         });
   });
 </script>
