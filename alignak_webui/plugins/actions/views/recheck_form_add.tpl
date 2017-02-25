%setdefault('read_only', False)
%setdefault('auto_post', False)

%setdefault('form_class', 'form-horizontal')

%# recheck attributes
%setdefault('element', 'recheck')
%setdefault('action', 'add')
%setdefault('element_id', '-1')
%setdefault('elements_type', 'host')
%setdefault('element_name', 'unknown')

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
         <input type="text" readonly id="element_id" name="element_id" value="{{id}}">
         %end
         %for name in element_name:
         <input type="text" readonly id="element_name" name="element_name" value="{{name}}">
         %end
         <input type="text" readonly id="elements_type" name="elements_type" value="{{elements_type}}">
      </div>

      <fieldset>
         {{_('Recheck comment:')}}
         <div class="form-group">
            <div class="col-xs-12">
               <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
               <p class="help-block">{{_('This comment will be associated to the re-check command')}}</p>
            </div>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>&nbsp;{{_('Request recheck')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function(){
   %if auto_post:
      // Submit form
      $('form[data-item="recheck"]').submit();
   %end
});
</script>
