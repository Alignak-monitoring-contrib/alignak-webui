%setdefault('read_only', False)
%setdefault('auto_post', False)

%# Acknowledge attributes
%setdefault('element', 'acknowledge')
%setdefault('action', 'add')
%setdefault('livestate_id', '-1')
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
         %for id in livestate_id:
         <input type="text" readonly id="livestate_id" name="livestate_id" value="{{id}}">
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}">
         %end
      </div>

      <fieldset>
         <div class="form-group">
            <label class="col-md-2 control-label" for="sticky">{{_('Acknowledge option - sticky:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="togglebutton">
                  <label>
                     <input id="sticky" name="sticky" type="checkbox" {{'checked="checked"' if sticky else ''}} >
                  </label>
               </div>
               <p class="help-block">{{_('Sticky acknowledge')}}</p>
            </div>
         </div>
         <div class="form-group">
            <label class="col-md-2 control-label" for="notify">{{_('Acknowledge option - notify:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="input-group">
                  <span class="input-group-addon text-info">
                  </span>
                  <div class="checkbox">
                     <label>
                        <input id="notify" name="notify" type="checkbox" {{'checked="checked"' if notify else ''}} >
                     </label>
                  </div>
               </div>
               <p class="help-block">{{_('Sticky acknowledge')}}</p>
            </div>
         </div>
         <div class="form-group">
            <label class="col-md-2 control-label" for="persistent">{{_('Acknowledge option - persistent:')}}</label>
            <div class="col-md-offset-2 col-md-10">
               <div class="input-group">
                  <span class="input-group-addon text-info">
                  </span>
                  <div class="checkbox">
                     <label>
                        <input id="persistent" name="persistent" type="checkbox"
                           {{'checked="checked"' if persistent else ''}}
                           >
                     </label>
                  </div>
               </div>
               <p class="help-block">{{_('Persistent acknowledge')}}</p>
            </div>
         </div>

         <div class="form-group">
            <div class="col-sm-12">
               <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
            </div>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-block"> <i class="fa fa-check"></i>{{_('Request acknowledge')}}</button>
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
