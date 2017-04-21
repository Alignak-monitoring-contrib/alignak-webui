<!-- Hosts configuration widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

<table class="table table-condensed table-bordered">
   <colgroup>
      <col style="width: 20%" />
      <col style="width: 80%" />
   </colgroup>
   <thead>
      <tr>
         <th colspan="2">{{_('Custom variables:')}}</th>
      </tr>
   </thead>
   <tbody>
   %for var in host.variables:
      <tr>
         <td title="{{var['name']}}">{{var['alias']}}</td>
         <td>{{var['value']}}</td>
      </tr>
   %end
   </tbody>
</table>
