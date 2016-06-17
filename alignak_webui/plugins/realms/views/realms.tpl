%setdefault('debug', True)

%from bottle import request
%rebase("layout", title=title, js=['realms/htdocs/js/jstree/jstree.min.js'], css=['realms/htdocs/css/default/style.min.css'], page="/realm")

%from alignak_webui.utils.helper import Helper

<style>
   // Get sure that jsTree context menu is visible ...
   .jstree-contextmenu {
       z-index: 1000;
   }
</style>

<!-- Realm view -->
<div id="realm">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Realms as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for realm in realms:
                  <li class="list-group-item"><small>Host: {{realm}} - {{realm.__dict__}}</small></li>
               %end
            </ul>
            <div class="panel-footer">{{len(realms)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="panel panel-default">
      <div class="panel-body">
      %if not realms:
         %include("_nothing_found.tpl", search_string=search_string)
      %else:

         <div id="jstree_demo_div">
         <!-- in this example the tree is populated from inline HTML -->
    <ul>
      <li>Root node 1
        <ul>
          <li id="child_node_1">Child node 1</li>
          <li>Child node 2</li>
        </ul>
      </li>
      <li>Root node 2</li>
    </ul>
         </div>

         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th width="40px"></th>
               <th>{{_('Realm name')}}</th>
               <th>{{_('Level')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
               %for realm in realms:
               <tr id="#{{realm.id}}">
                  <td title="{{realm.alias}}">
                     {{! realm.get_html_state(text=None, title=_('No livestate for this element'))}}
                  </td>

                  <td>
                     <small>{{!realm.html_link}}</small>
                  </td>

                  <td>
                     <small>{{realm._level}}</small>
                  </td>

               </tr>
             %end
            </tbody>
         </table>
      %end
      </div>
   </div>
 </div>

 <script>
   var jsTreeData = [];
   %for realm in realms:
      jsTreeData.push( {
         "id" : '{{realm.id}}',
         li_attr: {
            "realm_id" : '{{realm.id}}'
         },
         "parent" : '{{'#' if realm._level == 0 else realm._tree_parents[0]}}',
         "text" : '{{realm.name}}'
      } );
   %end

   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");

      $('#jstree_demo_div').on("changed.jstree", function (e, data) {
         console.log(data.selected);
      });
      $('button').on('click', function () {
         $('#jstree_demo_div').jstree(true).select_node('child_node_1');
         $('#jstree_demo_div').jstree('select_node', 'child_node_1');
         $.jstree.reference('#jstree_demo_div').select_node('child_node_1');
      });

      $('#jstree_demo_div').jstree();
   });
 </script>
