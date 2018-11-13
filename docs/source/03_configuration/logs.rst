.. raw:: LaTeX

    \newpage

.. _configuration_logs:

Application log
===============

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

The log file(s) location is the first found directory. If an environment variable ``ALIGNAK_WEBUI_LOG_DIR`` exists, this variable is used by the application as the log directory. It allows to **override the default log location**.



The default logging behavior is to log to the console and in a daily rotating file at INFO log level with a local time date.

Some simple modifications:

* to change log level: change the root logger `level` to DEBUG, WARNING, ...

* to set date time as UTC: change the console handler formatter to `utc`

Else, if you are aware of the Python logger configuration, update the file according to your needs:
::

    {
      "version": 1,
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
