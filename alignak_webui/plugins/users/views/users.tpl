%setdefault('debug', False)

%setdefault('commands', False)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], pagination=pagination)

<!-- Users filtering and display -->
<div id="users">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Users as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for user in elts:
                  <li class="list-group-item"><small>User: {{user}} - {{user.__dict__}}</small></li>
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
      %if commands and (current_user.is_super_administrator() or current_user.is_administrator()):
      <div class="panel-heading">
         <div class="btn-toolbar" role="toolbar" aria-label="{{_('Users commands')}}">
            <div class="btn-group btn-lg" role="group" data-type="actions" aria-label="{{_('Users commands')}}">
               <button class="btn btn-default"
                     data-type="action" data-action="add-user"
                     data-toggle="tooltip" data-placement="bottom" title="{{_('Create a new user')}}"
                     >
                     <i class="fa fa-plus"></i>
                     {{_('Add a new user')}}
               </button>
            </div>
         </div>
      </div>
      %end

      <div class="panel-body">
         %# First element for global data
         %object_type, start, count, total, dummy = pagination[0]
         <i class="pull-right small">{{_('%d elements out of %d') % (count, total)}}</i>

         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               <th>{{_('Name')}}</th>
               <th>{{_('Username')}}</th>
               <th>{{_('Administrator')}}</th>
               <th>{{_('Commands')}}</th>
               <!--
               <th>{{_('Widgets')}}</th>
               -->
               <th>{{_('Email')}}</th>
            </tr></thead>

            <tbody>
            %for user in elts:
               <tr data-toggle="collapse" data-target="#details-{{user.id}}" class="accordion-toggle">
                  <td>
                     {{! user.get_html_state()}}
                  </td>

                  <td>
                     <small data-toggle="tooltip" data-placement="top" title="{{user.notes}}">{{! user.get_html_link()}}</small>
                  </td>

                  <td>
                     <small data-toggle="tooltip" data-placement="top" title="{{user.notes}}">{{user.get_username()}}</small>
                  </td>

                  <td>
                     <small>{{! webui.helper.get_on_off(status=user.is_administrator())}}</small>
                  </td>

                  <td>
                     <small>{{! webui.helper.get_on_off(user.is_power())}}</small>
                  </td>

                  <!--
                  <td>
                     <small>{{! webui.helper.get_on_off(user.can_change_dashboard())}}</small>
                  </td>
                  -->

                  <td>
                     {{! user.email}}
                  </td>
               </tr>
            %end
            </tbody>
         </table>
      </div>
   </div>
   %end
</div>

<script>
   $(document).ready(function(){
      set_current_page("{{ webui.get_url(request.route.name) }}");
   });
</script>
