<!-- Hosts configuration widget -->
%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

<table class="table table-condensed table-bordered">
   <colgroup>
      <col style="width: 40%" />
      <col style="width: 60%" />
   </colgroup>
   <thead>
      <tr>
         <th colspan="3">{{_('Customs:')}}</th>
      </tr>
   </thead>
   <tbody style="font-size:x-small;">
   %for var in sorted(host.customs):
      <tr>
         <td>{{var}}</td>
         <td>{{host.customs[var]}}</td>
      </tr>
   %end
   </tbody>
</table>
