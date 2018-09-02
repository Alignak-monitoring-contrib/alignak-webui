<!-- users view widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%from alignak_webui.objects.item_user import User

<div id="user_view_information" class="col-lg-4 col-sm-4 text-center">
   <div>
      {{! user.get_html_state(text=None, size="fa-5x")}}
      <legend><strong>{{user.alias}}</strong></legend>
      %if current_user.is_power():
         {{! Helper.get_html_commands_buttons(user, _('Actions'))}}
      %end
   </div>
</div>
<div id="user_view_graphes" class="col-lg-8 col-sm-8">
   <!-- Last check output -->
   <table class="table table-condensed table-nowrap">
      <thead>
         <tr>
            <th colspan="2">{{_('Main information:')}}</th>
         </tr>
      </thead>
      <tbody>
         <tr>
            <td><strong>{{_('Realm:')}}</strong></td>
            <td>
               {{! user._realm.get_html_link()}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Role:')}}</strong></td>
            <td>
               {{user.get_role(display=True)}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Email:')}}</strong></td>
            <td>
               {{user.email}}
            </td>
         </tr>
         <tr>
            <td><strong>{{_('Picture:')}}</strong></td>
            <td>
               <img src="{{current_user.picture}}" class="img-circle user-logo" alt="{{_('Photo: %s') % current_user.name}}" title="{{_('Photo: %s') % current_user.name}}">
            </td>
         </tr>
      </tbody>
   </table>
</div>
