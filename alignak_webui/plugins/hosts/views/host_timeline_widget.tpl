<!-- Host timeline widget -->
%setdefault('debug', False)

%# embedded is True if the widget is got from an external application
%setdefault('embedded', False)
%from bottle import request
%setdefault('links', request.params.get('links', ''))
%setdefault('identifier', 'widget')
%setdefault('credentials', None)

%# Filtering?
%setdefault('types', [])
%setdefault('selected_types', [])

%setdefault('object_type', 'host')
%setdefault('page', '/' + object_type + '/' + host.id)

%from bottle import request
%search_action = request.urlparts.path
%search_string = request.query.get('search', '')
%page_string = request.query.get('page', None)

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
               %for item in history:
                  <li class="list-group-item">
                     <small>Element: {{item}} - {{item.__dict__}}</small>
                  </li>
               %end
            </ul>
            <div class="panel-footer">{{len(history)}} elements</div>
         </div>
      </div>
   </div>
   %end

   <style>
      /* navbar */
      .navbar-primary .navbar { background:#7a97a5; border-bottom:none; }
      .navbar-primary .navbar .nav > li > a {color: #501762;}
      .navbar-primary .navbar .nav > li > a:hover {color: #fff; background-color: #8e49a3;}
      .navbar-primary .navbar .nav .active > a,.navbar .nav .active > a:hover {color: #fff; background-color: #7a97a5;}
      .navbar-primary .navbar .nav li > a .caret, .tnav .navbar .nav li > a:hover .caret {border-top-color: #fff;border-bottom-color: #fff;}
      .navbar-primary .navbar .nav > li.dropdown.open.active > a:hover {}
      .navbar-primary .navbar .nav > li.dropdown.open > a {color: #fff;background-color: #9f58b5;border-color: #fff;}
      .navbar-primary .navbar .nav > li.dropdown.open.active > a:hover .caret, .tnav .navbar .nav > li.dropdown.open > a .caret {border-top-color: #fff;}
      .navbar-primary .navbar .navbar-brand {color:#fff;}
      .navbar-primary .navbar .nav.pull-right {margin-left: 10px; margin-right: 0;}
      .navbar-xs .navbar-primary .navbar { min-height:28px; height: 28px; }
      .navbar-xs .navbar-primary .navbar .navbar-brand{ padding: 0px 12px;font-size: 16px;line-height: 28px; }
      .navbar-xs .navbar-primary .navbar .navbar-nav > li > a {  padding-top: 0px; padding-bottom: 0px; line-height: 28px; }
      .navbar-sm .navbar-primary .navbar { min-height:40px; height: 40px; }
      .navbar-sm .navbar-primary .navbar .navbar-brand{ padding: 0px 12px;font-size: 16px;line-height: 40px; }
      .navbar-sm .navbar-primary .navbar .navbar-nav > li > a {  padding-top: 0px; padding-bottom: 0px; line-height: 40px; }
      .navbar-sm form { margin-top: 5px!important; }
   </style>
   <div class="navbar-sm">
      <div class="navbar-primary">
         <nav class="navbar navbar-static-top" role="navigation">
            <!-- Brand and toggle get grouped for better mobile display -->
            <div class="navbar-header">
                 <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#host-timeline-navbar">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                 </button>
             </div>
            <!-- Collect the nav links, forms, and other content for toggling -->
            <div class="collapse navbar-collapse" id="host-timeline-navbar">
               <ul class="nav navbar-nav navbar-left">
                  <li class="hidden-xs" id="timeline_loading">
                     <a href="#">
                        <span class="fa fa-spinner fa-pulse fa-1x"></span>
                        <span class="sr-only">{{_('Loading...')}}</span>
                     </a>
                  </li>

                  <div class="pull-left">
                     %setdefault('start', 0)
                     %setdefault('count', 25)
                     %setdefault('total', 0)
                     %setdefault('pagination', Helper.get_pagination_control('unknown', total, start, count))

                     %page_url, start, count, total, active = pagination[0]
                     %item_id = page_url.replace('/', '_')
                     %item_id = item_id.replace('#', '_')
                     <div id="pagination_{{item_id}}" style="margin-top: 5px" class="elts_per_page btn-toolbar" role="toolbar" aria-label="{{_('Pages number sequence')}}">
                        %if pagination and len(pagination) > 1:
                        <div class="input-group input-group-sm">
                           <ul class="pagination pagination-sm" >
                           %first_element=False
                           %next_page=False
                           %for label, start, count, total, active in pagination:
                              %if not first_element:
                                 %first_element=True
                                 %continue
                              %end
                              <li class="{{'active' if active else ''}} {{'next_page' if next_page else ''}}">
                                 <a href="#" data-action="paginate" data-start="{{start}}" data-count="{{count}}">{{!label}}<span class="sr-only">{{!label}}</span></a>
                              </li>
                              %if active:
                                 %next_page=True
                              %else:
                                 %if next_page:
                                    %next_page=False
                                 %end
                              %end
                           %end
                           </ul>
                           <div class="input-group-btn">
                              <button type="button" class="btn dropdown-toggle" data-toggle="dropdown" aria-expanded="false">{{count}}&nbsp;#&nbsp;<span class="caret"></span></button>
                              <ul class="dropdown-menu" role="menu">
                                 <li><a href="#" data-action="paginate" data-count="5">{{_('%d elements') % 5}}</a></li>
                                 <li><a href="#" data-action="paginate" data-count="10">{{_('%d elements') % 10}}</a></li>
                                 <li><a href="#" data-action="paginate" data-count="25">{{_('%d elements') % 25}}</a></li>
                                 <li><a href="#" data-action="paginate" data-count="50">{{_('%d elements') % 50}}</a></li>
                              </ul>
                           </div>
                        </div>

                        <script>
                        $('a[data-action="paginate"]').on('click', function(e){
                           get_new_page($(this).data('start'), $(this).data('count'));
                        });
                        </script>
                        %end
                     </div>
                  </div>
               </ul>

               <ul class="nav navbar-nav navbar-right">
                  <div class="pull-right">
                     <div class="input-group input-group-sm">
                        <div class="input-group-btn">
                           <form class="navbar-form navbar-left" role="search" method="get" action="{{ search_action }}">
                              <label class="sr-only" for="host-timeline-search">{{_('Filter input field')}}</label>
                              <div class="input-group">
                                 <input class="form-control" type="search"
                                        id="host-timeline-search" name="host-timeline-search"
                                        value="{{ search_string }}" placeholder="{{_('search filter...')}}">
                              </div>
                           </form>

                           <button type="button" class="btn dropdown-toggle" data-toggle="dropdown" aria-expanded="false">
                              <span class="fa fa-filter"></span>&nbsp;<span class="caret"></span>
                           </button>
                           <ul class="dropdown-menu" role="menu">
                              <li role="presentation">
                                 <a role="menuitem" data-action="filter" data-filter="">{{_('Clear filter')}}</a>
                              </li>
                              <li role="presentation" class="divider"></li>
                              %for k in sorted(search_filters.keys()):
                                 %title, filter = search_filters[k]
                                 %if not title:
                                 <li class="divider"/>
                                 %else:
                                 <li role="presentation">
                                    <a role="menuitem" data-action="filter" data-filter="{{filter}}">{{title}}</a>
                                 </li>
                                 %end
                              %end
                              <li role="presentation" class="divider hidden-xs hidden-sm"></li>
                              <li role="presentation" >
                                 <a role="menuitem" data-action="search-box">
                                    <strong>{{! _('<span class="fa fa-question-circle"></span> Search syntax')}}</strong>
                                 </a>
                              </li>
                           </ul>
                        </div>
                     </div>
                     <script>
                        $('a[data-action="filter"]').on('click', function(e) {
                           get_new_filtered_page($(this).data('filter'));
                        });
                        $('#form-timeline-search').on("submit", function (evt) {
                           // Do not automatically submit ...
                           evt.preventDefault();

                           get_new_filtered_page($('#host-timeline-search').val());
                        });
                     </script>
                  </div>
               </ul>
            </div><!-- /.navbar-collapse -->
         </nav>
      </div>

   %if not history:
      <div class="alert alert-info">
         <p>{{_('No available history events.')}}</p>
      </div>
   %else:
   <ol id="included_timeline" class="timeline">
   %for item in history:
      %if not item.user:
      %continue
      %end
      <li class="{{'' if item.status.startswith('check.result') else 'timeline-inverted'}}">
         <div class="timeline-badge">
            {{! item.get_html_state(text=None, title=item.get_title())}}
         </div>
         <div class="timeline-panel">
            <div class="timeline-heading">
               <div class="pull-left">
                  {{! item.user.get_html_state(text=item.user.alias) if item.user and item.user!='user' else ''}}
               </div>
               <div class="pull-right clearfix">
                  <small class="text-muted">
                     <span class="fa fa-clock-o"></span>
                     <em title="{{_('UTC timestamp: %d'% item.get_check_date(timestamp=True))}}"><strong>{{item.get_check_date(fmt='%H:%M:%S', duration=True)}}</strong></em>
                  </small>
               </div>
               <div class="clearfix">
               </div>
            </div>
            <div class="timeline-body">
               <p><small>
                  {{! item.service.get_html_link() if item.service and item.service!='service' else ''}}
               </small></p>
               %message = ''
               %if getattr(item, 'logcheckresult') and item.logcheckresult!='logcheckresult':
               %message = "%s%s - %s" % (message, item.logcheckresult.get_html_state(text=None), item.logcheckresult.output)
               %end
               %if getattr(item, 'message') and item.message!='':
               %message = item.message
               %end
               <p>
                  <small>{{! message}}</small>
               </p>
            </div>
         </div>
      </li>
   %end
   </ol>
   %end
</div>
<script>
   var g_start = {{start}};
   var g_count = {{count}};
   var g_total = {{total}};
   var g_search_string = '{{search_string}}';

   function get_new_page(start, count) {
      if (start == undefined) start=0;
      console.log("Set start: ", start);
      if (count == undefined) count=10;
      console.log("Set count: ", count);

      $('#timeline_loading').show();

      %if embedded:
         var $url = '{{request.urlparts.scheme}}://{{request.urlparts.netloc}}{{request.urlparts.path}}';

         $.ajax({
            url: $url,
            data: {
               'page': 'yes', 'start': start, 'count': count, 'search': g_search_string
            }
         })
         .done(function(content, textStatus, jqXHR) {
            $('#wd_panel_timeline').html(content);
            g_start = start;
            g_count = count;
         })
         .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('get host tab, error: ', jqXHR, textStatus, errorThrown);
         })
         .always(function() {
            $('#timeline_loading').hide();
         });
      %else:
         var $url = '{{request.urlparts.scheme}}://{{request.urlparts.netloc}}{{request.urlparts.path}}';

         // Save user preference
         save_user_preference('elts_per_page', count, function() {
            // Changed tab
            var $url = window.location.href.replace(window.location.search,'');
            $url = $url.split('#');
            if (($url[1] == undefined) || ($url[1] == '')) {
               $url = 'host_timeline';
            } else {
               $url = $url[1];
            }
            var loading='<div class="alert alert-info text-center"><span class="fa fa-spin fa-spinner"></span>&nbsp;{{_("Fetching data...")}}&nbsp;<span class="fa fa-spin fa-spinner"></span></div>';
            $('#'+$url).html(loading);
            $.ajax({
               url: '/'+$url+'/{{host.id}}',
               data: {
                  'start': start, 'count': count, 'search': g_search_string
               }
            })
            .done(function(content, textStatus, jqXHR) {
               $('#'+$url).html(content);
               g_start = start;
               g_count = count;
            })
            .fail(function(jqXHR, textStatus, errorThrown) {
               console.error('get host tab, error: ', jqXHR, textStatus, errorThrown);
            })
            .always(function() {
               $('#timeline_loading').hide();
            });
         });
      %end
   }

   function get_new_filtered_page(filter) {
      if (filter == undefined) return;
      console.log("Set filter: ", filter);

      $('#timeline_loading').show();

      %if embedded:
         var $url = '{{request.urlparts.scheme}}://{{request.urlparts.netloc}}{{request.urlparts.path}}';

         $.ajax({
            url: $url,
            data: {
               'page': 'yes', 'search': filter, 'start': g_start, 'count': g_count
            }
         })
         .done(function(content, textStatus, jqXHR) {
            $('#{{object_type}}_timeline_view').html(content);
         })
         .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('get host tab, error: ', jqXHR, textStatus, errorThrown);
         })
         .always(function() {
            $('#timeline_loading').hide();
         });
      %else:
         var $url = '{{request.urlparts.scheme}}://{{request.urlparts.netloc}}{{request.urlparts.path}}';

         $.ajax({
            url: $url,
            data: {
               'page': 'yes', 'start': start, 'count': count, 'search': g_search_string
            }
         })
         .done(function(content, textStatus, jqXHR) {
            $('#{{object_type}}_timeline_view').html(content);
         })
         .fail(function(jqXHR, textStatus, errorThrown) {
            console.error('get host tab, error: ', jqXHR, textStatus, errorThrown);
         })
         .always(function() {
            $('#timeline_loading').hide();
         });
      %end
   }

   $(document).ready(function() {
      $('#timeline_loading').hide();

      var win = $(window);

      // Set ajaxready status
      win.data('ajaxready', true);

      // Each time the user scrolls
      win.scroll(function() {
         // Request new data only if timeline tab is active...
         url = document.location.href.split('#');
         if ((url[1] != undefined) && (url[1] != 'host_timeline')) {
            return;
         }

         // If a request is still in progress, return...
         if ($(window).data('ajaxready') == false) return;

         // End of the document reached?
         if ($(document).height() - win.height() == win.scrollTop()) {
            $('#timeline_loading').show();

            // Set ajaxready to avoid multiple requests...
            $(window).data('ajaxready', false);

            start += {{count}};
            var url = '{{'/' + object_type + '/' + host.id}}' + '?infiniteScroll=true&start=' + start + '&count={{count}}';
            $.get(url, function(data) {
               $(data).find('#included_timeline li').each(function(idx, li){
                  var elt = '<li/>';
                  if ($(li).hasClass("timeline-inverted")) {
                     elt = '<li class="timeline-inverted"/>';
                  }
                  $(elt)
                     .hide()
                     .append($(li).html())
                     .appendTo('#included_timeline')
                     .delay(100)
                     .slideDown('slow');
               });

               $('#timeline_loading').hide();
               // Unset ajaxready because request is finished...
               win.data('ajaxready', true);
            });
         }
      });
   });
</script>
