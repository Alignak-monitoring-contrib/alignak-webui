%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%# No default refresh for this page
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/alignak", refresh=True)

%from alignak_webui.utils.helper import Helper

<div id="alignak" class="card" style="margin-top: 10px; padding:10px">
   %if not alignak_state:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:

      <table class="table table-condensed">
         <thead><tr>
            <th style="width: 40px"></th>
            <th>{{_('Daemon name')}}</th>
            <th>{{_('Address')}}</th>
            <th>{{_('Reachable')}}</th>
            <th>{{_('Last check')}}</th>
            <th>{{_('Spare')}}</th>
            <th>{{_('Passive daemon')}}</th>
            <th>{{_('Manage sub-realms')}}</th>
            <th>{{_('Manage arbiters')}}</th>
         </tr></thead>

         <tbody>
         %for daemon_type in alignak_state:
            %if daemon_type == '_status':
                %continue
            %end
            %daemons = alignak_state.get(daemon_type)
            %for daemon_name in daemons:
               %daemon = alignak_state.get(daemon_type).get(daemon_name)
               <tr id="#daemon-{{daemon_name}}">
                  <td>
                     <small>{{! Helper.get_on_off(daemon['alive'])}}</small>
                  </td>

                  <td title="{{daemon_name}}">
                     {{daemon_name}}
                  </td>

                  <td>
                     <small>{{daemon['address']}}:{{daemon['port']}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(daemon['reachable'])}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(daemon['last_check'])}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(daemon['spare'])}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(daemon['passive'])}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(daemon['manage_sub_realms'])}}</small>
                  </td>

                  <td>
                     <small>{{! Helper.get_on_off(daemon['manage_arbiters'])}}</small>
                  </td>
               </tr>
            %end
         %end
         </tbody>
      </table>
   %end
 </div>
