%setdefault('read_only', False)
%setdefault('auto_post', False)

%# recheck attributes
%setdefault('action', 'add')
%setdefault('element_id', '-1')
%setdefault('elements_type', 'host')
%setdefault('element_name', 'unknown')

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
   <h3>{{title}}</h3>
   <small><em>
      {{', '.join(element_name)}}
   </em></small>
</div>

<div class="modal-body">
   <form data-item="recheck" data-action="recheck" class="form-horizontal" method="post" action="/recheck/add" role="form">
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
            <div class="col-sm-12">
               <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
            </div>
            <p class="help-block">{{_('This comment will be associated to the scheduled downtime')}}</p>
         </div>
      </fieldset>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>{{_('Request recheck')}}</button>
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
