<!-- Service configuration widget -->
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
   <tbody>
   %for var in sorted(service.variables):
      %if isinstance(var['value'], list):
      %first_row = True
      %for list_item in var['value']:
      <tr>
         %if first_row:
         <td title="{{var['name']}}">{{var['alias']}}</td>
         %first_row=False
         %else:
         <td></td>
         %end
         <td>
         %if isinstance(list_item, dict):
         %data = []
         %for prop in list_item:
            %data.append("%s = %s" % (prop, list_item[prop]))
         %end
         {{", ".join(data)}}
         %else:
         {{list_item}}
         %end
         </td>
      </tr>
      %end
      %else:
      <tr>
         <td title="{{var['name']}}">{{var['alias']}}</td>
         <td>{{var['value']}}</td>
      </tr>
      %end
   %end
   </tbody>
</table>
