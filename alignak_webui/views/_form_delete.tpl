%import json
%from alignak_webui.objects.element import BackendElement
%from alignak_webui.objects.element_state import ElementState

%# Default values
%setdefault('debug', False)
%setdefault('edition', edition_mode)
%setdefault('is_templated', '_is_template' in plugin.table)
%setdefault('is_template', False)
%setdefault('has_template', False)
%setdefault('refresh', False)

%if element:
%# An element still exists...
%setdefault('title', _('%s %s') % (plugin.backend_endpoint.capitalize(), element.name))

%if '_is_template' in element.__dict__ and element['_is_template']:
%is_template = True
%end

%if '_is_template' in element.__dict__ and not element['_is_template']:
%if '_template_fields' in element.__dict__ and element['_template_fields']:
%has_template = True
%end
%end

%else:
%# No element exist...
%setdefault('title', _('New %s') % (plugin.backend_endpoint))
%end

%rebase("layout", title=title, page="/{{plugin.backend_endpoint}}_form/{{element.name}}")

%if debug and element:
<div class="panel-group">
   <div class="panel panel-default">
      <div class="panel-heading">
         <h4 class="panel-title">
            <a data-toggle="collapse" href="#collapse_{{element.id}}"><i class="fa fa-bug"></i> Element as dictionary</a>
         </h4>
      </div>
      <div id="collapse_{{element.id}}" class="panel-collapse collapse">
         <dl class="dl-horizontal" style="height: 200px; overflow-y: scroll;">
            %for k,v in sorted(element.__dict__.items()):
               <dt>{{k}}</dt>
               <dd>{{v}}</dd>
            %end
         </dl>
      </div>
   </div>
</div>
%end

<div id="form_delete_{{plugin.backend_endpoint}}">
   %post=""
   %if edition:
   %post='''method="post" action="/%s/%s/delete"''' % (plugin.backend_endpoint, element.id)
   %end
   <form role="form" data-element="{{element.id if element else 'None'}}" class="element_form {{'template_form' if is_template else ''}}" {{! post}}>
      <div class="well page">
      <fieldset>
      %# Editing a template
      %if is_template:
         <div class="alert alert-dismissible alert-warning">
            <button type="button" class="close" data-dismiss="alert">×</button>
            <h4>{{_('You are deleting a %s template.') % plugin.backend_endpoint}}</h4>
            <hr/>
            <p>{{_('All the %ss based upon this template may be affected by your modifications.') % plugin.backend_endpoint}}</p>
         </div>

         <legend>{{! _('%s template <code>%s</code>') % (plugin.backend_endpoint.capitalize(), element.name)}}</legend>
      %# Editing an element
      %elif element:
          <div class="alert alert-dismissible alert-warning">
             <button type="button" class="close" data-dismiss="alert">×</button>
             <h4>{{_('Please confirm that this element must be deleted.')}}</h4>
          </div>
         <legend>{{! _('%s <code>%s</code>') % (plugin.backend_endpoint.capitalize(), element.name)}}</legend>
      %end

      %if edition:
      </div>
      <div class="well page">
         <button type="reset" class="btn btn-default pull-left">{{_('Cancel')}}</button>
         <button type="submit" class="btn btn-primary pull-right">{{_('Delete')}}</button>
         <div class="clearfix"></div>
      </div>
      %end

      <script>
         window.setTimeout(function() { $("div.alert-dismissible").alert('close'); }, 10000);
      </script>
   </form>
</div>

%if edition:
<script>
   $('form[data-element="{{element.id if element else 'None'}}"]').on("submit", function (evt) {
      // Do not automatically submit ...
      evt.preventDefault();
      //console.log("Submit form...", $(this).attr('method'), $(this).attr('action'))

      // Submitting message
      wait_message('{{_('Submitting form...')}}', true)

      $.ajax({
         url: $(this).attr('action'),
         type: $(this).attr('method'),
         data: $(this).serialize()
      })
      .done(function(data, textStatus, jqXHR) {
         // data is JSON formed with a _message field
         if (jqXHR.status != 200) {
            console.error(jqXHR.status, data);
            raise_message_ko(data._message);
         } else {
            raise_message_info(data._message);
            // Navigate to the home page
            window.setTimeout(function() {
               window.location.href = '/';
            }, 3000);
         }
      })
      .fail(function( jqXHR, textStatus, errorThrown ) {
         // data is JSON formed with a _message field
         if (jqXHR.status != 409) {
            console.error(errorThrown, textStatus);
         } else {
            raise_message_info(data._message);
         }
      })
      .always(function() {
         wait_message('', false)
      });
   });
</script>
%end