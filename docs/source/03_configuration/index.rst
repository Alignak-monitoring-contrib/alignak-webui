.. raw:: LaTeX

    \newpage

.. _configuration:

Configuration
=============

The application runs without any extra configuration file with default parameters. Nevertheless, the application is best used when suited to user's neeeds.

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

If an environment variable ``ALIGNAK_WEBUI_BACKEND`` exists, the value of this variable will override the one defined in the configuration file.




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


[Alignak-WebUI] section
~~~~~~~~~~~~~~~~~~~~~~~

This section contains parameters to configure the application.

    * **alignak_backend**, Alignak backend endpoint (default: *http://127.0.0.1:5000*)

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


[buttons] section
~~~~~~~~~~~~~~~~~

This section defines patterns used by the application to build the buttons commands toolbar.
**TO BE COMPLETED**

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

