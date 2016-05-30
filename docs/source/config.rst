.. _config:

Configuration
=============

The application can be run without any extra configuration file with default parameters. Nevertheless, the application is best used when suited to user's neeeds.

The application can be configured thanks to a configuration file. When installed for an end user, the configuration file ``settings.cfg`` is installed on your system in the */etc/alignak_webui* or */usr/local/etc/alignak_webui* directory according to whether your system is a Linux (Debian) or Unix (FreeBSD) distribution.

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
-------------------------

**Note**: The default configuration file contains a commented copy of all the available parameters.

**Note**: please do not change these parameters unless you know what you're doing!

[Alignak-WebUI] section
~~~~~~~~~~~~~~~~~~~~~~~~~~

This section contains parameters to configure the user interface.

[logs] section
~~~~~~~~~~~~~~~~~~~~~~~~~~

This section contains parameters to configure the application logs.

TO BE COMPLETED:!