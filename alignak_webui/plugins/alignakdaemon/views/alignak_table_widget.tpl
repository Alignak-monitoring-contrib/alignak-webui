<!-- Alignak widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper

%if not elements:
   <center>
      <h4>{{_('No Alignak daemons state available...')}}</h4>
   </center>
%else:
   <table class="table table-condensed">
      <thead><tr>
         <th style="width: 40px"></th>
         <th>{{_('Daemon name')}}</th>
         <th>{{_('Spare')}}</th>
      </tr></thead>

      <tbody>
      %for daemon in elements:
         <tr id="#daemon-{{daemon.id}}">
             <td title="{{daemon.name}}">
              %title = "%s - %s" % (daemon.state, Helper.print_duration(daemon.last_check, duration_only=False, x_elts=1))
              {{! daemon.get_html_state(text=None, title=title)}}
             </td>

             <td title="{{daemon.name}}">
                 {{daemon.name}}
             </td>

             <td>
                 <small>{{! Helper.get_on_off(daemon.spare)}}</small>
             </td>
         </tr>
      %end
      </tbody>
   </table>
%end
