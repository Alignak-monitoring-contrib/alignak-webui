%setdefault('read_only', False)
%setdefault('auto_post', False)

%# Acknowledge attributes
%setdefault('element', 'acknowledge')
%setdefault('action', 'add')
%setdefault('elements_type', 'host')
%setdefault('element_id', '-1')
%setdefault('element_name', 'unknown')
%setdefault('sticky', True)
%setdefault('notify', False)
%setdefault('persistent', True)

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
   <small><em>
      {{', '.join(element_name)}}
   </em></small>
</div>

<div class="modal-body">
   <form data-item="{{element}}" data-action="{{action}}" method="post" action="/{{element}}/{{action}}" role="form">
      <div class="form-group" style="display: none">
         %for id in element_id:
         <input type="text" readonly id="element_id" name="element_id" value="{{id}}">
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}">
         %end
         <input type="text" readonly id="elements_type" name="elements_type" value="{{elements_type}}">
      </div>

      <fieldset>
         <div class="form-group">
            <label class="col-md-2 control-label" for="sticky">{{_('Acknowledge is sticky:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="checkbox">
                  <label>
                     <input id="sticky" name="sticky" type="checkbox" {{'checked="checked"' if sticky else ''}} >
                  </label>
               </div>
               <p class="help-block">{{_('If checked, the acknowledge will remain until the element returns to an OK state.')}}</p>
            </div>
         </div>
         <div class="form-group">
            <label class="col-md-2 control-label" for="notify">{{_('Acknowledge notifies:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="checkbox">
                  <label>
                     <input id="notify" name="notify" type="checkbox" {{'checked="checked"' if notify else ''}} >
                  </label>
               </div>
               <p class="help-block">{{_('If checked, a notification will be sent out to the concerned contacts')}}</p>
            </div>
         </div>
         <div class="form-group">
            <label class="col-md-2 control-label" for="persistent">{{_('Acknowledge is persistent:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="checkbox">
                  <label>
                     <input id="persistent" name="persistent" type="checkbox"
                        {{'checked="checked"' if persistent else ''}}
                        >
                  </label>
               </div>
               <p class="help-block">{{_('If checked, the comment will persist after the acknowledge is no more useful')}}</p>
            </div>
         </div>

         <div class="form-group">
            <div class="col-sm-12">
               <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
            </div>
            <p class="help-block">{{_('This comment will be associated to the acknowledge')}}</p>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>{{_('Request acknowledge')}}</button>
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
