%setdefault('debug', False)
%setdefault('title', _('Command view'))

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], page="/command/{{command.id}}")

%from alignak_webui.utils.helper import Helper

<!-- commands filtering and display -->
<div class="command" id="command_{{element.id}}">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{element.id}}"><i class="fa fa-bug"></i> command as dictionary</a>
            </h4>
         </div>
         <div id="collapse_{{element.id}}" class="panel-collapse collapse">
            <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
               %for k,v in sorted(element.__dict__.items()):
                  <dt>{{k}}</dt>
                  <dd>{{v}}</dd>
               %end
            </dl>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse1"><i class="fa fa-bug"></i> Group members as dictionaries</a>
            </h4>
         </div>
         <div id="collapse1" class="panel-collapse collapse">
            <ul class="list-group">
               %for elt in element.members:
               %if isinstance(elt, basestring):
               %continue
               %end
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#collapse_{{elt.id}}"><i class="fa fa-bug"></i> {{elt.name}}</a>
                     </h4>
                  </div>
                  <div id="collapse_{{elt.id}}" class="panel-collapse collapse">
                     <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                        %for k,v in sorted(elt.__dict__.items()):
                           <dt>{{k}}</dt>
                           <dd>{{v}}</dd>
                        %end
                     </dl>
                  </div>
               </div>
               %end
            </ul>
            <div class="panel-footer">{{len(element.members)}} members</div>
         </div>
      </div>
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse2"><i class="fa fa-bug"></i> Group groups as dictionaries</a>
            </h4>
         </div>
         <div id="collapse2" class="panel-collapse collapse">
            <ul class="list-group">
               %for elt in groups:
               %if isinstance(elt, basestring):
               %continue
               %end
               <div class="panel panel-default">
                  <div class="panel-heading">
                     <h4 class="panel-title">
                        <a data-toggle="collapse" href="#collapse_{{elt.id}}"><i class="fa fa-bug"></i> {{elt.name}}</a>
                     </h4>
                  </div>
                  <div id="collapse_{{elt.id}}" class="panel-collapse collapse">
                     <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                        %for k,v in sorted(elt.__dict__.items()):
                           <dt>{{k}}</dt>
                           <dd>{{v}}</dd>
                        %end
                     </dl>
                  </div>
               </div>
               %end
            </ul>
            <div class="panel-footer">{{len(element.members)}} groups</div>
         </div>
      </div>
   </div>
   %end

   %if not element:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
   <div class="panel panel-default">
      <div class="panel-body">
         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               <th>{{_('Command name')}}</th>
               <th>{{_('Command line')}}</th>
               <th>{{_('Timeout')}}</th>
               <th>{{_('Environment macros')}}</th>
               <th>{{_('Poller tag')}}</th>
               <th>{{_('Reactionner tag')}}</th>
            </tr></thead>

            <tbody>
               %elts = [element]
               %for command in elts:
               <tr id="#{{command.id}}">
                  <td>
                     {{! command.get_html_state()}}
                  </td>

                  <td>
                     <small>{{command.name}}</small>
                  </td>

                  <td>
                     <small>{{command.command_line}}</small>
                  </td>

                  <td>
                     <small>{{command.timeout}}</small>
                  </td>

                  <td>
                     <small>{{ ! Helper.get_on_off(command.enable_environment_macros) }}</small>
                  </td>

                  <td>
                     <small>{{command.poller_tag}}</small>
                  </td>

                  <td>
                     <small>{{command.reactionner_tag}}</small>
                  </td>
               </tr>
             %end
            </tbody>
         </table>
      </div>
   </div>
   %end
 </div>
