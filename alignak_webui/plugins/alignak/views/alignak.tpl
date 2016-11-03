%setdefault('debug', False)

%from bottle import request
%search_string = request.query.get('search', '')

%# No default refresh for this page
%rebase("layout", title=title, js=[], css=[], pagination=pagination, page="/alignak", refresh=True)

%from alignak_webui.utils.helper import Helper

<div id="alignak" class="card" style="margin-top: 10px; padding:10px">
   %if not alignak_daemons:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:
      <table class="table table-condensed">
         <thead><tr>
            <th style="width: 40px"></th>
            <th>{{_('Daemon name')}}</th>
            <th>{{_('Address')}}</th>
            <th>{{_('Reachable')}}</th>
            <th>{{_('Spare')}}</th>
            <th>{{_('Passive daemon')}}</th>
            <th>{{_('Manage sub-realms')}}</th>
            <th>{{_('Manage arbiters')}}</th>
         </tr></thead>

         <tbody>
         %for daemon in alignak_daemons:
            <tr id="#daemon-{{daemon.id}}">
                <td>
                 %title = "%s - %s" % (daemon.state, Helper.print_duration(daemon.last_check, duration_only=False, x_elts=1))
                 {{! daemon.get_html_state(text=None, title=title)}}
                </td>

                <td>
                    {{daemon.name}}
                </td>

                <td>
                    <small>{{daemon.address}}:{{daemon.port}}</small>
                </td>

                <td>
                    <small>{{! Helper.get_on_off(daemon.reachable)}}</small>
                </td>

                <td>
                    <small>{{! Helper.get_on_off(daemon.spare)}}</small>
                </td>

                <td>
                    <small>{{! Helper.get_on_off(daemon.passive)}}</small>
                </td>

                <td>
                    <small>{{! Helper.get_on_off(daemon.manage_sub_realms)}}</small>
                </td>

                <td>
                    <small>{{! Helper.get_on_off(daemon.manage_arbiters)}}</small>
                </td>
            </tr>
         %end
         </tbody>
      </table>
   %end
 </div>
