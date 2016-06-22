%setdefault('debug', False)

%setdefault('host', None)

%from bottle import request
%search_string = request.query.get('search', '')

%rebase("layout", title=title, pagination=pagination, page='/'+object_type + ('/'+host.id if host else ''), css=['common/htdocs/css/timeline.css'])

%from alignak_webui.utils.helper import Helper

<!-- Tree display -->
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

   %if not items:
      %include("_nothing_found.tpl", search_string=search_string)
   %else:

   <h3 class="timeline-title">{{! _('Timeline for: %s') % host.html_link}}</h3>

   <ul class="timeline">
   %for item in items:
      %if not item.user:
      %continue
      %end
      <li class="{{'' if item.status.startswith('check') else 'timeline-inverted'}}">
         <div class="timeline-badge">
            {{! item.get_html_state(text=None)}}
         </div>
         <div class="timeline-panel">
            <div class="timeline-heading">
               <p>
                  <small class="text-muted">
                     <i class="fa fa-clock-o"></i>
                     {{item.get_check_date(fmt='%H:%M:%S', duration=True)}}
                  </small>
               </p>
            </div>
            <div class="timeline-body">
               %if item.status.startswith('check'):
                  <p>
                     <small>
                     %if host:
                     {{! item.service.html_link if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.html_link}}{{! ' / '+item.service.html_link if item.service and item.service!='service' else ''}}
                     %end
                     </small>
                  </p>
                  %message = "%s - %s" % (item.logcheckresult.get_html_state(text=None), item.logcheckresult.output)
                  <p>
                     <small>{{! message}}</small>
                  </p>
               %end

               %if item.status.startswith('ack'):
                  {{! item.user.get_html_state(text=item.user.alias) if item.user and item.user!='user' else ''}}
                  <p>
                     <small>
                     %if host:
                     {{! item.service.html_link if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.html_link}}{{! ' / '+item.service.html_link if item.service and item.service!='service' else ''}}
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
                     %if host:
                     {{! item.service.html_link if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.html_link}}{{! ' / '+item.service.html_link if item.service and item.service!='service' else ''}}
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
   </ul>
</div>
%end
