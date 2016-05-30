%rebase("widget")

%if not kiosks:
   <center>
      <h3>{{_('No elements found.')}}</h3>
   </center>
%else:
   <table class="table table-condensed">
      <tbody>
         %for kiosk in kiosks:
            <tr>
               <td>
                  {{! kiosk.get_html_state()}}
               </td>

               <td class="align-left">
                  <small>{{kiosk.get_name()}}</small>
               </td>

               <td class="align-left">
                  <small>{{kiosk.entity_name}}</small>
               </td>
               <td class="align-left">
                  <small>{{kiosk.short_location}}</small>
               </td>
            </tr>
         %end
      </tbody>
   </table>
%end
