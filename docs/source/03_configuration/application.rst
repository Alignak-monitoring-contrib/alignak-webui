.. raw:: LaTeX

    \newpage

.. _configuration_application:

Application configuration
=========================

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

If an environment variable ``BOTTLE_DEBUG`` exists and is set to '1', the Bottle application server will run in debug mode. If an environment variable ``ALIGNAK_WEBUI_DEBUG`` exists and is set to '1', the application will run in debug mode; which means that the application logs will be set to a DEBUG level.

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

With the default configuration the application server listens on TCP port 5001 of all interfaces.


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

    * **grafana**, Grafana application URL (default: empty value). When this parameter is present, the WebUI will try to display Grafana panels for the hosts/services if a panel definition exists in the data fetched from the Alignak Backend.

    * **livestate_layout**, configure the layout to be used in the livestate view: single table, multiple panels or tabbed view, for each business impact level
