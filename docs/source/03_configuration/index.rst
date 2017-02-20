.. raw:: LaTeX

    \newpage

.. _configuration:

Configuration
=============

The application runs without any extra configuration file with its default parameters. Nevertheless, the application is best used when suited to user's neeeds ;)



Application log
---------------
The application uses the Python logger facility to produce an activity log. The log can be configured thanks to a configuration file ``logging.json`` located on your system in a directory according to whether your system is a Linux (Debian) or Unix (FreeBSD) distribution. This location is, most often, */usr/local/etc/alignak-webui/*.

Thus, the application searches in several location for a logger configuration file:

    - /usr/local/etc/alignak-webui/logging.json
    - /etc/alignak-webui/logging.json
    - ~/alignak-webui/logging.json
    - ./etc/logging.json
    - ./alignak-webui/etc/logging.json
    - ./logging.json

The first file found is retained as the application logger configuration file.

If an environment variable ``ALIGNAK_WEBUI_LOGGER_FILE`` exists, this variable is used by the application as the only configuration file name to be loaded by the application. It allows to **override the default file list**.

The application stores its log file(s) in a directory searched among:

    - /usr/local/var/log/alignak-webui
    - /var/log/alignak-webui
    - /tmp/alignak-webui

The log file(s) location is the first found directory. If an environment variable ``ALIGNAK_WEBUI_LOG`` exists, this variable is used by the application as the log directory. It allows to **override the default log location**.



The default logging behavior is to log to the console and in a daily rotating file at INFO log level with a local time date.

Some simple modifications:

* to change log level: change the root logger `level` to DEBUG, WARNING, ...

* to set date time as UTC: change the console handler formatter to `utc`

Else, if you are aware of the Python logger configuration, update the file according to your needs:
::

    {
      "version": 2,
      "disable_existing_loggers": false,
      "formatters": {
        "utc": {
          "()": "alignak_webui.utils.logger.UTCFormatter",
          "format": "[%(asctime)s] %(levelname)s: [%(name)s] %(message)s"
        },
        "local": {
          "format": "[%(asctime)s] %(levelname)s: [%(name)s] %(message)s"
        }
      },

      "handlers": {
        "console": {
          "class": "alignak_webui.utils.logger.ColorStreamHandler",
          "level": "DEBUG",
          "formatter": "local",
          "stream": "ext://sys.stdout"
        },
        "file": {
          "class": "logging.handlers.TimedRotatingFileHandler",
          "level": "DEBUG",
          "formatter": "local",
          "filename": "alignak-webui.log",
          "when": "midnight",
          "interval": 1,
          "backupCount": 7,
          "encoding": "utf8"
        }
      },

      "root": {
        "level": "INFO",
        "handlers": ["console", "file"]
      }
    }

**Note** that the Web UI is intended to be launched as an uWSGI application and that uWSGI will be configured to log the application console output to a file...


Configuration file location
---------------------------
The application can be configured thanks to a configuration file. When installed for an end user, the configuration file ``settings.cfg`` is located on your system in a directory according to whether your system is a Linux (Debian) or Unix (FreeBSD) distribution. This location is determined by the Python setup.py script.

Thus, the application searches in several location for a configuration file:

    - /usr/local/etc/alignak-webui/settings.cfg
    - /etc/alignak-webui/settings.cfg
    - ~/alignak-webui/settings.cfg
    - ./etc/settings.cfg
    - ./alignak-webui/etc/settings.cfg
    - ./settings.cfg

Each file found takes precedence over the previous files. As of it, for the same parameter with different values in */usr/local/etc/alignak-webui/settings.cfg* and *./settings.cfg*, the retained value will be the one configured in *./settings.cfg*.

If an environment variable ``ALIGNAK_WEBUI_CONFIGURATION_FILE`` exists, this variable is used by the application as the only configuration file name to be loaded by the application. It allows to **override the default file list**.

If an environment variable ``ALIGNAK_WEBUI_CONFIGURATION_THREAD`` exists, the application will check periodically if its configuration file changed. If the configuration file modification time changed, the configuration is reloaded by the application.

If an environment variable ``ALIGNAK_WEBUI_DEBUG`` exists, the application will run in debug mode; which means that the application logs will be set to a DEBUG level.

If an environment variable ``ALIGNAK_WEBUI_BACKEND`` exists, the value of this variable will override the one defined in the configuration file  (``alignak_backend``).

If an environment variable ``ALIGNAK_WEBUI_WS`` exists, the value of this variable will override the one defined in the configuration file (``alignak_ws``).




Configuration file format
-------------------------

This file is a text file in classic ``.ini`` file format. It is parsed using Python ConfigParser module.

Sections are introduced by a [section] header, and contain name = value entries.

Lines beginning with # or ; are ignored as comments.

Strings don’t need quotes.

Multi-valued strings can be created by indenting values on multiple lines.

Boolean values can be specified as on, off, true, false, 1, or 0 and are case-insensitive.

Environment variables can be substituted in by using dollar signs: $WORD ${WORD} will be replaced with the value of WORD in the environment. A dollar sign can be inserted with $$. Missing environment variables will result in empty strings with no error.

A percent sign can be inserted with %%.


Configuration parameters
------------------------

**Note**: The default configuration file contains a commented copy of all the available parameters.

**Note**: please do not change these parameters unless you know what you're doing!

[bottle] section
~~~~~~~~~~~~~~~~

This section contains parameters to configure the base Web server.

    * **host**, interface the application listens to (default: *127.0.0.1*)

    * **port**, TCP port the application listens to (default: *8868*)

    * **debug**, to make the server run in debug mode (only useful for developers)


[session] section
~~~~~~~~~~~~~~~~~

This section contains parameters to configure the application user's sessions. Thanks to those parameters it is possible to adapt the session duration according to your needs. This requires to be aware of the Web client / server session handling to make some modifications in this section.

As a default, the user session is valid from the login time up to the client's browser closing, allowing to have infinite sessions to use the Web UI on stand-alone monitors;)


[Alignak-WebUI] section
~~~~~~~~~~~~~~~~~~~~~~~

This section contains parameters to configure the application.

    * **alignak_backend**, Alignak backend endpoint (default: *http://127.0.0.1:5000*)

    * **alignak_ws**, Alignak Web Services endpoint (default: *http://127.0.0.1:8888*)

    * **debug**, to make the application run in debug mode (much more log in the log file!)

    * **about_name**, application name in About modal box (default is defined in source code)

    * **about_version**, application name in About modal box (default is defined in source code)

    * **about_copyright**, application copyright in About modal box (default is defined in source code)

    * **about_release**, application release notes in About modal box (default is defined in source code)

    * **login_text**, welcome text on the login form (default: *Welcome!<br> Log-in to use the application*)

    * **company_log**, logo image used on the login form (default: *'/static/images/default_company.png'*)

    * **webui_logo**, logo image used in the application footer (default: */static/images/logo_webui_xxs.png*)

    * **play_sound**, plays a sound when a new problem is raised (default: *no*)

    * **refresh_period**, page refresh period in seconds (default: *60*). Use 0 to disable page refresh.

    * **header_refresh_period**, page header refresh period in seconds (default: *30*). Use 0 to disable page header refresh.

    * **locale**, language file to use (default: *en_US*). Language files are located in *locales* sub-directory.

    * **timezone**, preferred timezone for dates (default: *Europe/Paris*).

    * **timeformat**, default date format (default: *%Y-%m-%d %H:%M:%S*).

    * **cors_acao**, CORS Access Control Allow Origin for external application access (default: *127.0.0.1*).

    * **grafana**, Grafana application URL (default: empty value). When this parameter is present,
    the WebUI will try to display Grafana panels for the hosts/services if a panel definition exists
    in the data fetched from the Alignak Backend.

    * **livestat_layout**, configure the layout to be used in the livestate view: single table, multiple panels or tabbed view, for each business impact level


[on_off]
~~~~~~~~
This section allows to configure how the on/off (eg. enabled/disabled) is represented in the Web UI.
::

    [on_off]
    ; Global element to be included in the HTML and including the items and the text
    on=<span title="##title##" class="fa fa-fw fa-check text-success">##message##</span>

    ; Element to be included for each BI count
    off=<span title="##title##" class="fa fa-fw fa-close text-danger">##message##</span>

[business_impact]
~~~~~~~~~~~~~~~~~
This section allows to configure how the business impact of an element is represented in the Web UI.
::

    [business_impact]
    ; Global element to be included in the HTML and including the items and the text
    global=<div><span>##items##</span><span>##text##</span></div>

    ; Element to be included for each BI count
    item=<span class="fa fa-star"></span>

[buttons]
~~~~~~~~~

This section defines patterns used by the application to build the buttons commands toolbar.
::

    [buttons]
    ; First solution: a buttons group
    ; Global element to be included in the HTML
    ;livestate_commands=<div class="btn-group btn-group-xs btn-group-raised" role="group" data-type="actions" title="##title##">##commands##</div>
    ; Each command element to be included in the HTML
    ;livestate_command=<button class="btn btn-default" data-type="action" data-action="##action##" data-toggle="tooltip" data-placement="top" title="##title##" data-element_type="##type##" data-name="##name##" data-element="##id##" ##disabled##><i class="fa fa-##icon##"></i></button>

    ; Second solution (preferred one): a buttons dropdown list
    ; Global element to be included in the HTML
    livestate_commands=<div class="btn-group btn-group-xs" role="group" data-type="actions" title="##title##"><button type="button" class="btn btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">##title## <span class="caret"></span></button><ul class="dropdown-menu">##commands##</ul></div>
    ; Each command element to be included in the HTML
    livestate_command=<li><button class="btn btn-default" data-type="action" data-action="##action##" data-toggle="tooltip" data-placement="top" title="##title##" data-element_type="##type##" data-name="##name##" data-element="##id##" ##disabled##><i class="fa fa-##icon##"></i>&nbsp;&nbsp;##title##</button></li>

[tables.lists]
~~~~~~~~~~~~~~

This section defines patterns used by the application to build the elemnts lists in the tables.
::

    [tables.lists]
    ; Button to display the list
    button=<button class="btn btn-xs btn-raised" data-toggle="collapse" data-target="#list_##type##_##id##" aria-expanded="false">##title##</button><div class="collapse" id="list_##type##_##id##">##content##</div>

    ; Global element to be included in the HTML for the list
    list=<ul class="list-group">##content##</ul>

    ; Each command element to be included in the HTML list
    item=<li class="list-group-item"><span class="fa fa-check">&nbsp;##content##</span></li>

    ; Unique element to be included in the HTML list if the list contains only one element
    unique=##content##

[items] section
~~~~~~~~~~~~~~~

This section defines patterns used by the application to build the elements icons.
**TO BE COMPLETED**


Application interface layout
----------------------------
Material design:

    - *static/css/material* directory contains the files used to configure the material look and
    feel of the application. Those files may be changed with the result of the rebuild explained in
    the develop part of this documentation (see `Application UI design`_).

Css files:

    - *alignak_webui.css*, contains the main classes used by the Web UI
    - *alignak_webui-items.css*, contains the CSS classes used for the items icons styles as declared
    in the application configuration file (see hereunder)

Javascript files:

    - *alignak_webui-layout.js*, contains some colors definitions for the externally embedded widgets

