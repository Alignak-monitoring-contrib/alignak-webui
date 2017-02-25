%setdefault('read_only', False)
%setdefault('auto_post', False)

%setdefault('form_class', 'form-horizontal')

%# downtime attributes
%setdefault('element', 'downtime')
%setdefault('action', 'add')
%setdefault('element_id', '-1')
%setdefault('elements_type', 'host')
%setdefault('element_name', 'unknown')

%setdefault('fixed', True)
%setdefault('duration', False)

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

      <div class="form-group">
         <div class="col-xs-12">
            <label class="col-xs-4 control-label">{{_('Downtime options')}}</label>
            <div class="checkbox col-xs-8">
               <label>
                  <input type="checkbox" name="fixed" {{'checked' if fixed else ''}} value="{{fixed}}"> {{_('Fixed')}}
               </label>
            </div>
         </div>
      </div>

      <div class="form-group">
         <label class="col-xs-4 control-label" for="duration">{{_('Duration')}}</label>
         <div class="col-xs-offset-4 col-xs-8 input-group">
            <span class="input-group-addon"><i class="fa fa-clock-o"></i></span>
            <input type="text" name="duration" id="duration" class="form-control" value="{{duration}}"/>
         </div>
      </div>

      <div class="form-group">
         <label class="col-xs-4 control-label" for="dtr_downtime">{{_('Downtime date range')}}</label>
         <div class="col-xs-offset-4 col-xs-8 input-group">
            <span class="input-group-addon"><i class="fa fa-calendar"></i></span>
            <input type="text" name="dtr_downtime" id="dtr_downtime" class="form-control" />
         </div>
      </div>

      <div class="form-group">
         <div class="col-xs-12">
            <textarea hidden {{'readonly' if read_only else ''}} class="form-control" name="comment" id="comment" rows="3" placeholder="{{comment}}">{{comment}}</textarea>
         </div>
      </div>

      <div class="form-group" style="display:none">
         <input type="text" readonly name="start_time" id="start_time" value="{{start_time}}" />
         <input type="text" readonly name="end_time" id="end_time" value="{{end_time}}" />
      </div>

      <button type="submit" class="btn btn-success btn-lg btn-raised"> <i class="fa fa-check"></i>&nbsp;{{_('Request downtime')}}</button>
   </form>
</div>

<script type="text/javascript">
// Initial start/stop for downtime, do not consider seconds ...
//var downtime_start = moment().seconds(0);
// Set default downtime period as two days
//var downtime_stop = moment().seconds(0).add('hours', 2);

$(document).ready(function(){
   %if auto_post:
      // Submit form
      $('form[data-item="downtime"]').submit();
   %end

   $("#dtr_downtime").daterangepicker(
      {
         "ranges": {
            "{{_('2 hours')}}":       [moment(), moment().add(2, 'hours')],
            "{{_('8 hours')}}":       [moment(), moment().add(8, 'hours')],
            "{{_('1 day')}}":         [moment(), moment().add(1, 'days')],
            "{{_('2 days')}}":        [moment(), moment().add(2, 'days')],
            "{{_('1 week')}}":        [moment(), moment().add(7, 'days')],
            "{{_('1 month')}}":       [moment(), moment().add(1, 'month')],
         },

         "locale": {
            "format": "{{_('MM/DD/YYYY HH:mm')}}",
            "separator": "{{_(' - ')}}",
            "applyLabel": "{{_('Apply')}}",
            "cancelLabel": "{{_('Cancel')}}",
            "fromLabel": "{{_('From')}}",
            "toLabel": "{{_('To')}}",
            "customRangeLabel": "{{_('Custom')}}",
            "weekLabel": "{{_('W')}}",
            "daysOfWeek": [
               "{{_('Su')}}",
               "{{_('Mo')}}",
               "{{_('Tu')}}",
               "{{_('We')}}",
               "{{_('Th')}}",
               "{{_('Fr')}}",
               "{{_('Sa')}}"
            ],
            "monthNames": [
               "{{_('January')}}",
               "{{_('February')}}",
               "{{_('March')}}",
               "{{_('April')}}",
               "{{_('May')}}",
               "{{_('June')}}",
               "{{_('July')}}",
               "{{_('August')}}",
               "{{_('September')}}",
               "{{_('October')}}",
               "{{_('November')}}",
               "{{_('December')}}"
            ],
            "firstDay": 1
         },
         "linkedCalendars": false,

         "minDate": moment(),
         "startDate": moment(),
         "endDate": moment().add('days', 2),

         "timePicker": true,
         "timePickerIncrement": 5,
         "timePicker24Hour": true,

         "showDropdowns": false,
         "showWeekNumbers": false,
         "opens": 'center'
      }
   );

   // Set the initial date range of that picker
   $('#dtr_downtime').data('daterangepicker').setStartDate(moment().seconds(0));
   $('#dtr_downtime').data('daterangepicker').setEndDate(moment().seconds(0).add(2, 'hours'));

   $('#start_time').val(moment().seconds(0).format('X'));
   $('#end_time').val(moment().seconds(0).add(2, 'hours').format('X'));

   // When update dates on apply button ...
   $('#dtr_downtime').on('apply.daterangepicker', function(ev, picker) {
      //console.log("Apply", picker.startDate.format('MM/DD/YYYY'));
      $('#start_time').val(picker.startDate.format('X'));
      $('#end_time').val(picker.endDate.format('X'));
   });
});
</script>
