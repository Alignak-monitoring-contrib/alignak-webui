%setdefault('debug', False)
%# When layout is False, this template is embedded
%setdefault('layout', True)

%# For a specific host?
%setdefault('timeline_host', None)

%# Filtering?
%setdefault('types', [])
%setdefault('selected_types', [])

%from bottle import request
%search_string = request.query.get('search', '')

%if layout:
%rebase("layout", title=title, pagination=pagination, page='/'+object_type + ('/'+timeline_host.id if timeline_host else ''))
%end

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

   <div class="pull-left">
   <h3 class="timeline-title">{{title}}</h3>
   </div>

   <!-- Filtering menu -->
   %if types:
   <div class="pull-right">
      <form data-item="filter-timeline" data-action="filter" class="form" method="get" role="form">
         <div class="btn-group">
            <button type="button" class="btn btn-default btn-xs dropdown-toggle" data-toggle="dropdown">
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
                     <span class="fa fa-check"></i>
                     &nbsp;{{_('Apply filter')}}
                  </button>
               </li>
             </ul>
         </div>
      </form>
   </div>
   %end

   <div class="clearfix"></div>

   <ul class="timeline">
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
                  <small class="text-muted"><em>
                     <i class="fa fa-clock-o"></i> {{item.get_check_date(fmt='%H:%M:%S', duration=True)}}
                  </em></small>
               </div>
               <div class="clearfix">
               </div>
            </div>
            <div class="timeline-body">
               %if item.status.startswith('check.result'):
                  <p>
                     <small>
                     %if timeline_host:
                     {{! item.service.html_link if item.service and item.service!='service' else ''}}
                     %else:
                     {{! item.host.html_link}}{{! ' / '+item.service.html_link if item.service and item.service!='service' else ''}}
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

               %if item.status.startswith('ack'):
                  <p>
                     <small>
                     %if timeline_host:
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
                     %if timeline_host:
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
