%setdefault('debug', True)
%setdefault('title', _('Hostgroup view'))

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], page="/hostgroup/{{element.name}}")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<!-- hosts filtering and display -->
<div id="hostgroup">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#collapse_{{element.id}}"><i class="fa fa-bug"></i> Hostgroup as dictionary</a>
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
   </div>
   %end

   %if not element.members:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
   <div class="panel panel-default">
      <div class="panel-body">

         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               <th>{{_('Host name')}}</th>
               <th>{{_('Address')}}</th>
               <th>{{_('Check command')}}</th>
               <th>{{_('Active checks enabled')}}</th>
               <th>{{_('Passive checks enabled')}}</th>
               <th>{{_('Business impact')}}</th>
            </tr></thead>

            <tbody>
            %for elt in element.members:
               %if isinstance(elt, basestring):
               %continue
               %end
               <tr id="#{{elt.id}}">
                  <td title="{{elt.alias}}">
                     %title = "%s - %s (%s)" % (elt.state, Helper.print_duration(elt.last_check, duration_only=True, x_elts=0), elt.output)
                     {{! elt.get_html_state(text=None, title=title)}}
                  </td>

                  <td title="{{elt.alias}}">
                     <small>{{!elt.get_html_link()}}</small>
                  </td>

                  <td>
                     <small>{{elt.address}}</small>
                  </td>

                  <td>
                     {{! elt.check_command.get_html_state_link() if elt.check_command != 'command' else ''}}
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(elt.active_checks_enabled)}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(elt.passive_checks_enabled)}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_html_business_impact(elt.business_impact)}}</small>
                  </td>
               </tr>
            %end
            </tbody>
         </table>
      </div>
   </div>
   %end
 </div>
