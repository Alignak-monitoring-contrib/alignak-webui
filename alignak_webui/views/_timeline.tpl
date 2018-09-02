%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)

%# For a specific host?
%setdefault('timeline_host', None)

%# Filtering?
%setdefault('types', [])
%setdefault('selected_types', [])

%setdefault('object_type', 'history')
%setdefault('page', '/'+object_type + ('/'+timeline_host.id if timeline_host else ''))

%from bottle import request
%search_string = request.query.get('search', '')

%# Fetch elements per page preference for user, default is 25
%elts_per_page = datamgr.get_user_preferences(current_user, 'elts_per_page', 25)
%elts_per_page = elts_per_page['value']

%if layout:
%rebase("layout", title=title, pagination=pagination, page=page)
%end

%from alignak_webui.utils.helper import Helper

<!-- Timeline display -->
<div id="{{object_type}}_timeline_view">
   %if debug:
   <div class="panel-group">
      <div class="panel panel-default">
         <div class="panel-heading">
            <h4 class="panel-title">
               <a data-toggle="collapse" href="#{{object_type}}_timeline_collapse"><i class="fa fa-bug"></i> Elements as dictionaries</a>
            </h4>
         </div>
         <div id="{{object_type}}_timeline_collapse" class="panel-collapse collapse">
            <ul class="list-group">
               %for item in items:
                  <li class="list-group-item">
                     <small>Element: {{item}} - {{item.__dict__}}</small>
                  </li>
               %end
            </ul>
            <div class="panel-footer">{{len(items)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <div class="pull-left">
   <h3 class="timeline-title">{{title}}</h3>
   </div>

   <!-- Filtering menu -->
   %if types:
   <div class="pull-right">
      <form data-item="filter-timeline" data-action="filter" class="form" method="get" role="form">
         <div class="btn-toolbar" role="toolbar" aria-label="...">
            <div class="btn-group btn-group-xs" role="group" aria-label="{{_('Timeline filtering')}}">
               <button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown">
                  <span class="fa fa-filter fa-fw"></span>
                  <span class="caret"></span>
               </button>
               <ul class="dropdown-menu pull-right" role="menu" style="width: 240px">
                  %for type in types:
                  <li style="padding:5px">
                     <label class="checkbox-inline">
                        <input type="checkbox" {{'checked' if type in selected_types else ''}} name="{{type}}"> {{types[type]}}
                     </label>
                  </li>
                  %end
                  <li class="divider"></li>
                  <li style="padding:5px">
                     <button type="submit" class="btn btn-default btn-sm btn-block">
                        <span class="fa fa-check"></span>
                        &nbsp;{{_('Apply filter')}}
                     </button>
                  </li>
                </ul>
            </div>

            <div class="btn-group btn-group-xs" role="group" aria-label="{{_('Timeline navigation')}}">
            %if layout:
               <a href="/host/{{timeline_host.id}}" class="btn btn-default">
                  <span class="fa fa-server"></span>&nbsp;
               </a>
            %else:
               <a href="/history/{{timeline_host.id}}" class="btn btn-default">
                  <span class="fa fa-desktop"></span>&nbsp;
               </a>
            %end
            </div>
         </div>
      </form>
   </div>
   %end

   <div class="clearfix"></div>

   %if timeline_pagination and not layout:
   %include("_pagination_element", pagination=timeline_pagination, page=page, elts_per_page=elts_per_page, display_steps_form=True)
   %end

   <ol id="included_timeline" class="timeline">
   %for item in items:
      %if not item.user:
      %continue
      %end
      <li class="{{'' if item.status.startswith('check.result') else 'timeline-inverted'}}">
         <div class="timeline-badge">
            {{! item.get_html_state(text=None)}}
         </div>
         <div class="timeline-panel">
            <div class="timeline-heading">
               <div class="pull-left">
                  {{! item.user.get_html_state(text=item.user.alias) if item.user and item.user!='user' else ''}}
               </div>
               <div class="pull-right clearfix">
                  <small class="text-muted">
                     <span class="fa fa-clock-o"></span>
                     <em><strong>{{item.get_check_date(fmt='%H:%M:%S', duration=True)}}</strong></em>
                  </small>
               </div>
               <div class="clearfix">
               </div>
            </div>
            <div class="timeline-body">
               %if item.status.startswith('check.result'):
                  <p>
                     <small>
                     %if timeline_host:
                     {{! item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.get_html_link()}}{{! ' / '+item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %end
                     </small>
                  </p>
                  %if item.logcheckresult!='logcheckresult':
                  %message = "%s - %s" % (item.logcheckresult.get_html_state(text=None), item.logcheckresult.output)
                  %else:
                  %message = 'Fake!'
                  %end
                  <p>
                     <small>{{! message}}</small>
                  </p>
               %end

               %if item.status.startswith('check.request'):
                  <p>
                     <small>
                     %if timeline_host:
                     {{! item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.get_html_link()}}{{! ' / '+item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %end
                     </small>
                  </p>
                  <p>
                     <small>{{! item.message}}</small>
                  </p>
               %end

               %if item.status.startswith('ack'):
                  <p>
                     <small>
                     %if timeline_host:
                     {{! item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.get_html_link()}}{{! ' / '+item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %end
                     </small>
                  </p>
                  <p>
                     <small>{{! item.message}}</small>
                  </p>
               %end

               %if item.status.startswith('downtime'):
                  {{! item.user.get_html_state(text=item.user.alias) if item.user and item.user!='user' else ''}}
                  <p>
                     <small>
                     %if timeline_host:
                     {{! item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.get_html_link()}}{{! ' / '+item.service.get_html_link() if item.service and item.service!='service' else ''}}
                     %end
                     </small>
                  </p>
                  %message = "%s - %s" % (item.logcheckresult.get_html_state(text=None), item.logcheckresult.output)
                  <p>
                     <small>{{! message}}</small>
                  </p>
               %end
            </div>
         </div>
      </li>
   %end
   </ol>
</div>
<script>
   $(document).ready(function() {
      var win = $(window);
      %name, start, count, total, active = timeline_pagination[0]
      var start = {{start}};

      // Set ajaxready status
      $(window).data('ajaxready', true);

      // Each time the user scrolls
      win.scroll(function() {
         // If a request is still in progress, return...
         if ($(window).data('ajaxready') == false) return;

         // End of the document reached?
         if ($(document).height() - win.height() == win.scrollTop()) {
            $('#loading').show();

            // Set ajaxready to avoid multiple requests...
            $(window).data('ajaxready', false);

            start += {{elts_per_page}};
            var url = '{{'/'+object_type + ('/'+timeline_host.id if timeline_host else '')}}' + '?infiniteScroll=true&start=' + start + '&count={{count}}';
            $.get(url, function(data) {
               //var content = $(data).find('#included_timeline li').html();

               $(data).find('#included_timeline li').each(function(idx, li){
                  var elt = '<li/>';
                  if ($(li).hasClass("timeline-inverted")) {
                     elt = '<li class="timeline-inverted"/>';
                  }
                  $(elt)
                     .hide()
                     .append(li)
                     .appendTo('#included_timeline')
                     .delay(100)
                     .slideDown('slow');
               });

               $('#loading').hide();
               // Unset ajaxready because request is finished...
               $(window).data('ajaxready', true);
            });
         }
      });
   });

</script>
