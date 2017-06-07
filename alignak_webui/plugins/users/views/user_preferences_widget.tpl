<!-- User information widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

<div id="user-preferences">
   <div class="panel">
      <div class="panel-body">
         <div class="user-body">
            <table class="table table-condensed table-user-preferences col-sm-12" style="table-layout: fixed; word-wrap: break-word;">
               <colgroup>
                  <col class="col-sm-1">
                  <col class="col-sm-3">
                  <col class="col-sm-8">
               </colgroup>
               <thead>
                  <tr>
                     <th colspan="3">{{_('User preferences:')}}</th>
                  </tr>
               </thead>
               <tbody>
                  %preferences = datamgr.get_user_preferences(current_user, None)
                  %if preferences:
                  %for key in sorted(preferences):
                     <tr>
                        <td>
                        %if current_user.is_power():
                           <a class="btn btn-default btn-xs btn-raised" href="#"
                              data-action="delete-user-preference"
                              data-element="{{key}}"
                              data-message="{{_('User preference deleted')}}"
                              data-toggle="tooltip" data-placement="top"
                              title="{{_('Delete this user preference')}}">
                              <span class="fa fa-trash"></span>
                           </a>
                        %end
                        </td>
                        <td>{{key}}</td>
                        %value = datamgr.get_user_preferences(current_user, key)
                        <td>
                        %if isinstance(value, dict):
                        <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                           %for k,v in sorted(value.items()):
                              <dt>{{k}}</dt>
                              <dd>{{v}}</dd>
                           %end
                        </dl>
                        %elif isinstance(value, list):
                        <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
                           %idx=0
                           %for v in value:
                              <dt>{{idx}}</dt>
                              <dd>{{v}}</dd>
                              %idx += 1
                           %end
                        </dl>
                        %else:
                        {{value}}
                        %end
                        </td>
                     </tr>
                  %  end
                  %else:
                     <tr>
                        <td colspan="2">{{_('No user preferences')}}</td>
                     </tr>
                  %end
               </tbody>
            </table>
         </div>
      </div>
   </div>
</div>
