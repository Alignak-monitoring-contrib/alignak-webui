%setdefault('read_only', False)
%setdefault('auto_post', False)

%# Acknowledge attributes
%setdefault('action', 'add')
%setdefault('livestate_id', '-1')
%setdefault('sticky', True)
%setdefault('notify', False)
%setdefault('persistent', True)

<div class="modal-header">
   <a class="close" data-refresh="start" data-dismiss="modal">×</a>
    <h3>{{title}}</h3>
</div>

<div class="modal-body">
   <form data-item="acknowledge" data-action="add" class="form-horizontal" method="post" action="/acknowledge/add" role="form">
      <div class="form-group" style="display: none">
         <label for="livestate_id">Livestate id: </label>
         <input type="text" readonly id="livestate_id" name="livestate_id" placeholder="{{livestate_id}}" value="{{livestate_id}}">
      </div>

      <div class="form-group" >
         <label for="element_name">{{_('Element name:')}}</label>
         <input type="text" readonly id="element_name" name="element_name" placeholder="{{element_name}}" value="{{element_name}}">
      </div>

      <div class="form-group">
         <label class="col-sm-3 control-label">{{_('Acknowledge options: ')}}</label>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" name="sticky" {{'checked' if sticky else ''}} value="{{sticky}}"> {{_('Sticky')}}
               </label>
            </div>
         </div>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" name="notify" {{'checked' if notify else ''}} value="{{notify}}"> {{_('Notify')}}
               </label>
            </div>
         </div>
         <div class="col-sm-offset-3 col-sm-9">
            <div class="checkbox">
               <label>
                  <input type="checkbox" name="persistent" {{'checked' if persistent else ''}} value="{{persistent}}"> {{_('Persistent')}}
               </label>
            </div>
         </div>
      </div>

      <div class="form-group">
         <div class="col-sm-12">
            <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}"></textarea>
         </div>
      </div>

      <button type="submit" class="btn btn-success btn-lg btn-block"> <i class="fa fa-check"></i>{{_('Confirm creation')}}</button>
   </form>
</div>

<script type="text/javascript">
$(document).ready(function(){
   %if auto_post:
      // Submit form
      $('form[data-item="acknowledge"]').submit();
   %end
});
</script>
