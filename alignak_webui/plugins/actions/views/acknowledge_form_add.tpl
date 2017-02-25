%setdefault('read_only', False)
%setdefault('auto_post', False)

%setdefault('form_class', 'form-horizontal')

%# Acknowledge attributes
%setdefault('element', 'acknowledge')
%setdefault('action', 'add')
%setdefault('elements_type', 'host')
%setdefault('element_id', '-1')
%setdefault('element_name', 'unknown')

%setdefault('sticky', True)
%setdefault('notify', False)

<div class="modal-header">
   <a class="close" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
   <small><em>
      {{', '.join(element_name)}}
   </em></small>
</div>

<div class="modal-body">
   <form class="{{form_class}}" data-item="{{element}}" data-action="{{action}}" method="post" action="/{{element}}/{{action}}" role="form">
      <div class="form-group" style="display: none">
         %for id in element_id:
         <input type="text" readonly id="element_id" name="element_id" value="{{id}}"/>
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}"/>
         %end
         <input type="text" readonly id="elements_type" name="elements_type" value="{{elements_type}}"/>
      </div>

      <fieldset>
         <div class="form-group">
            <label class="col-xs-4 control-label" for="sticky">{{_('Acknowledge is sticky:')}}</label>
            <div class="checkbox col-xs-8">
               <label>
                  <input type="checkbox" id="sticky" name="sticky" {{'checked' if sticky else ''}} value="{{sticky}}" />
               </label>
               <p class="help-block">{{_('If checked, the acknowledge will remain until the element returns to an OK state.')}}</p>
            </div>
         </div>

         <div class="form-group">
            <label class="col-xs-4 control-label" for="notify">{{_('Acknowledge notifies:')}}</label>
            <div class="checkbox col-xs-8">
               <label>
                  <input type="checkbox" id="notify" name="notify" {{'checked="checked"' if notify else ''}} />
               </label>
               <p class="help-block">{{_('If checked, a notification will be sent out to the related contacts')}}</p>
            </div>
         </div>

         <div class="form-group">
            {{_('Acknowledge comment:')}}
            <div class="col-xs-12">
               <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
               <p class="help-block">{{_('This comment will be associated to the acknowledge')}}</p>
            </div>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>&nbsp;{{_('Request acknowledge')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function(){
   %if auto_post:
      // Submit form
      $('form[data-item="{{element}}"]').trigger('submit');
   %end
});
</script>
