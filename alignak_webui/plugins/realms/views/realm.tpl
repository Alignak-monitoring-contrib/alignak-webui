%setdefault('debug', False)
%setdefault('title', _('Realm view'))

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, js=[], css=[], page="/realm/{{element.name}}")

%from alignak_webui.utils.helper import Helper
%from alignak_webui.objects.item_command import Command

<div class="realm" id="realm_{{element.id}}">
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

   %if element._parent and element._parent is not None and element._parent != 'realm':
   <div class="realm-parent btn-group" role="group" aria-label="{{_('Group navigation')}}">
      <a class="btn btn-default btn-raised" href="{{element._parent.endpoint}}" role="button">
         <span class="fa fa-arrow-up"></span>
         {{_('Parent realm')}}
      </a>
   </div>
   %end

   <div class="realm-members panel panel-default">
      <div class="panel-body">
         <div class="col-xs-6 col-sm-2 text-center">
            %(realm_state, realm_status) = datamgr.get_realm_overall_state(element)
            {{! element.get_html_state(text=None, size="fa-3x", use_status=realm_status)}}
            <legend><strong>{{element.alias}}</strong></legend>
         </div>
         <div class="col-xs-6 col-sm-10">
         %members = datamgr.get_realm_members(element)
         %if not members:
            <div class="text-center alert alert-warning">
               <h4>{{_('No hosts found in this realm.')}}</h4>
            </div>
         %else:
            <table class="table table-condensed">
               <thead><tr>
                  <th style="width: 40px"></th>
                  <th>{{_('Host name')}}</th>
                  <th>{{_('Business impact')}}</th>
                  <th>{{_('Host check')}}</th>
                  <th>{{_('Last check')}}</th>
                  <th>{{_('Output')}}</th>
               </tr></thead>

               <tbody>
               %for elt in members:
                  <tr id="#{{elt.id}}">
                     <td title="{{elt.alias}}">
                        {{! elt.get_html_state(text=None, size="fa-1x", use_status=elt.overall_status)}}
                     </td>

                     <td title="{{elt.alias}}">
                        <small>{{!elt.get_html_link()}}</small>
                     </td>

                     <td>
                        <small>{{! Helper.get_html_business_impact(elt.business_impact)}}</small>
                     </td>

                     <td>
                        {{! elt.get_html_state(text=None)}}
                     </td>

                     <td>
                        {{Helper.print_duration(elt.last_check, duration_only=False, x_elts=0)}}
                     </td>

                     <td>
                        {{! elt.output}}
                     </td>
                  </tr>
               %end
               </tbody>
            </table>
         %end
            </div>
      </div>
   </div>

   <div class="realm-children panel panel-default">
      %children = datamgr.get_realm_children(element)
      %if not children:
         <!--
         <div class="text-center alert alert-warning">
            <h4>{{_('No children found in this realm.')}}</h4>
         </div>
         -->
      %else:
      <div class="panel-body">
         <table class="table table-condensed">
            <thead><tr>
               <th style="width: 40px"></th>
               <th>{{_('Name')}}</th>
               <th>{{_('Alias')}}</th>
               <th>{{_('Level')}}</th>
            </tr></thead>

            <tbody>
            %for elt in children:
               %if isinstance(elt, basestring):
               %continue
               %end
               <tr id="realm-{{elt.id}}">
                  <td title="{{elt.alias}}">
                     %(realm_state, realm_status) = datamgr.get_realm_overall_state(elt)
                     {{! elt.get_html_state(text=None, use_status=realm_status)}}
                  </td>

                  <td>
                     {{! elt.get_html_link()}}
                  </td>

                  <td>
                     {{elt.alias}}
                  </td>

                  <td>
                     {{elt.level}}
                  </td>
               </tr>
            %end
            </tbody>
         </table>
      </div>
      %end
   </div>
 </div>
