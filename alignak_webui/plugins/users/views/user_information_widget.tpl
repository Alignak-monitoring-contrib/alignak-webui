<!-- User information widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.utils.helper import Helper
%from alignak_webui.utils.perfdata import PerfDatas

<div class="col-md-6">
   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Overview:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Name:')}}</strong></td>
            <td>{{user.name}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Alias:')}}</strong></td>
            <td>{{user.alias}}</td>
         </tr>
         <tr>
            <td></td>
            <td><img src="{{user.picture}}" class="img-circle user-logo" alt="{{_('Photo: %s') % user.name}}" title="{{_('Photo: %s') % user.name}}"></td>
         </tr>
      </tbody>
   </table>
</div>
<div class="col-md-6">
   <table class="table table-condensed">
      <colgroup>
         <col style="width: 40%" />
         <col style="width: 60%" />
      </colgroup>
      <thead>
         <tr>
            <th colspan="2">{{_('Rights:')}}</th>
         </tr>
      </thead>
      <tbody style="font-size:x-small;">
         <tr>
            <td><strong>{{_('Administrator')}}</strong></td>
            <td>{{! webui.helper.get_on_off(status=user.is_administrator())}}</td>
         </tr>
         <tr>
            <td><strong>{{_('Commands')}}</strong></td>
            <td>{{! webui.helper.get_on_off(user.is_power())}}</td>
         </tr>
      </tbody>
   </table>
</div>
