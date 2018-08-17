.. raw:: LaTeX

    \newpage

.. _02_installation:

Installation
============

Requirements
------------


To use this application, you first need to install some Python modules that are listed in the ``requirements.txt`` file:

    .. literalinclude:: ../../../requirements.txt

**Note**: if you proceed to an end-user installation with pip, the required modules are automatically installed.

uWSGI
~~~~~

We recommend to use uWSGI as an application server for the Alignak Web UI.

You can install uWsgi with the python packaging::

   sudo pip install uWSGI

To get pip3 for Python 3 packages installation::

   sudo apt-get install python3-pip
   sudo pip3 install uWSGI

If you prefer using your Unix/Linux ditribution packaging to install uWSGI and the alignak Web UI, please refer to your distribution packages for installing. You will also need to install the uWSGI Python plugin.

As an example on Debian (for python 2)::

   sudo apt-get install uwsgi uwsgi-plugin-python

As an example on Debian (for python 3)::

   sudo apt-get install uwsgi uwsgi-plugin-python3

As an example on CentOS (for python 2)::

   # You need EPEL repository!
   sudo yum install epel-release

   sudo yum install uwsgi uwsgi-plugin-python

.. warning:: If you get some errors with the plugins, you will need to set some options in the alignak Web UI */usr/local/share/alignak-webui/etc/uwsgi.ini* configuration file or in the installed systemctl service unit. See this configuration file commented accordingly.


Install on Debian-like Linux
----------------------------

Installing Alignak Web UI for a Debian based Linux distribution (eg. Debian, Ubuntu, etc.) is using ``deb`` packages and it is the recommended way. You can find packages in the Alignak dedicated repositories.

To proceed with installation, you must register the alignak repository and store its public key on your system. This script is an example (for Ubuntu 16) to be adapted to your system::

Create the file */etc/apt/sources.list.d/alignak.list* with the following content::

   # Alignak DEB stable packages
   sudo echo deb https://dl.bintray.com/alignak/alignak-deb-stable xenial main | sudo tee -a /etc/apt/sources.list.d/alignak.list

If your system complains about missing GPG key, you can add the publib BinTray GPG key::

   sudo apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv D401AB61

If you wish to use the non-stable versions (eg. current develop or any other specific branch), you can also add the repository source for the test versions::

   # Alignak DEB testing packages
   sudo echo deb https://dl.bintray.com/alignak/alignak-deb-testing xenial main | sudo tee -a /etc/apt/sources.list.d/alignak.list

.. note:: According to your OS, replace {xenial} in the former script example:

    - Debian 8: ``jessie``
    - Ubuntu 16.04: ``xenial``
    - Ubuntu 14.04: ``trusty``
    - Ubuntu 12.04: ``precise``

And then update the repositories list::

   sudo apt-get update


Once the download sources are set, you can simply use the standard package tool to have more information about Alignak packages and available versions::

   apt-cache search python-alignak-webui


Or you can simply use the standard package tool to install Alignak Web UI::

   sudo apt install python-alignak-webui

   # Check Alignak Web UI installation
   # It copied the default shipped files and sample configuration.
   ll /usr/local/share/alignak-webui/

   # It installed the Alignak systemd services
   ll /lib/systemd/system/alignak*
      -rw-r--r-- 1 root root 1715 juil.  1 11:12 /lib/systemd/system/alignak-uwsgi.service

   # Alignak Web UI service status
   sudo systemctl status alignak-webui
   $ sudo systemctl status alignak-webui
      ● alignak-webui.service - uWSGI instance to serve Alignak Web UI
         Loaded: loaded (/lib/systemd/system/alignak-webui.service; enabled; vendor preset: enabled)
         Active: inactive (dead)

.. note:: that immediately after the installation the *alignak-webui* service is enabled and started! This is a side effect of the packaging tool that is used (*fpm*).

A post-installation script (repository *bin/python-post-install.sh*) is started at the end of the installation procedure to install the required Python packages. This script is copied during the installation in the default installation directory: */usr/local/share/alignak-webui*. It is using the Python pip tool to get the Python packages listed in the default installation directory *requirements.txt* file.

.. note:: this hack is necessary to be sure that we use the expected versions of the needed Python libraries...

It is recommended to set-up a log rotation because the Alignak backend log may be really verbose! Using the ``logrotate`` is easy. A default file is shipped with the installation script and copied to the */etc/logrotate.d/alignak-backend* with this content::

   "/var/log/alignak-webui/*.log" {
     copytruncate
     daily
     rotate 5
     compress
     delaycompress
     missingok
     notifempty
   }

A log rotation file for uWsgi is also shipped with the installation script and copied to the */etc/logrotate.d/uwsgi* with this content::

    "/var/log/uwsgi/alignak-webui.log" {
      copytruncate
      daily
      rotate 5
      compress
      delaycompress
      missingok
      notifempty
    }


.. note:: for Python 3 version, replace ``python`` with ``python3`` in the package and post-installation script names.

Install on RHEL-like Linux
--------------------------

Installing Alignak Web UI for an RPM based Linux distribution (eg. RHEL, CentOS, etc.) is using ``rpm`` packages and it is the recommended way. You can find packages in the Alignak dedicated repositories.

To proceed with installation, you must register the alignak repositories on your system.

Create the file */etc/yum.repos.d/alignak-stable.repo* with the following content::

   [Alignak-rpm-stable]
   name=Alignak RPM stable packages
   baseurl=https://dl.bintray.com/alignak/alignak-rpm-stable
   gpgcheck=0
   repo_gpgcheck=0
   enabled=1

And then update the repositories list::

   sudo yum repolist


If you wish to use the non-stable versions (eg. current develop or any other specific branch), you can also create a repository source for the test versions. Then create a file */etc/yum.repos.d/alignak-testing.repo* with the following content::

   [Alignak-rpm-testing]
   name=Alignak RPM testing packages
   baseurl=https://dl.bintray.com/alignak/alignak-rpm-testing
   gpgcheck=0
   repo_gpgcheck=0
   enabled=1

The Alignak packages repositories contain several version of the application. The versioning scheme is the same as the Alignak one.



Once the download sources are set, you can simply use the standard package tool to have more information about Alignak packages and available versions.
 ::

   yum search alignak-webui
        Loaded plugins: fastestmirror
        Loading mirror speeds from cached hostfile
        * base: mirrors.atosworldline.com
        * epel: mirror.speedpartner.de
        * extras: mirrors.atosworldline.com
        * updates: mirrors.standaloneinstaller.com
        =========================================================================== N/S matched: alignak ===========================================================================
        ...
        ...
        alignak-webui.noarch : Alignak WebUI, Web User Interface for Alignak

   yum info python-alignak-webui
        Modules complémentaires chargés : fastestmirror
        Loading mirror speeds from cached hostfile
        * base: ftp.rezopole.net
        * epel: mirror.miletic.net
        * extras: mirror.plusserver.com
        * updates: ftp.rezopole.net
        Paquets installés
        Nom                 : alignak-webui
        Architecture        : noarch
        Version             : packaging
        Révision            : 1
        Taille              : 12 M
        Dépôt               : installed
        Depuis le dépôt     : Alignak-rpm-testing
        Résumé              : Alignak WebUI, Web User Interface for Alignak
        URL                 : http://alignak.net
        Licence             : AGPL
        Description         : Alignak WebUI, Web User Interface for Alignak

Or you can simply use the standard package tool to install Alignak Web UI and its dependencies.
 ::

   sudo yum install python-alignak-webui

   # Check Alignak Web UI installation
   # It copied the default shipped files and sample configuration.
   ll /usr/local/share/alignak-webui/
      -rw-rw-r--. 1 root root  527 10 juil. 21:03 requirements.txt

A post-installation script (repository *bin/python-post-install.sh*) must be executed at the end of the installation procedure to install the required Python packages. This script is copied during the installation in the default installation directory: */usr/local/share/alignak-webui*. It is using the Python pip tool to get the Python packages listed in the default installation directory *requirements.txt* file.

 ::

    sudo /usr/local/share/alignak-webui/python-post-install.sh

.. note:: this hack is necessary to be sure that we use the expected versions of the needed Python libraries...

It is recommended to set-up a log rotation because the Alignak Web UI log may be really verbose! Using the ``logrotate`` is easy. A default file is shipped with the installation script and copied to the */etc/logrotate.d/alignak-webui* with this content::

   "/var/log/alignak-webui/*.log" {
     copytruncate
     daily
     rotate 5
     compress
     delaycompress
     missingok
     notifempty
   }

A log rotation file for uWsgi is also shipped with the installation script and copied to the */etc/logrotate.d/alignak-webui-uwsgi* with this content::

    "/var/log/uwsgi/alignak-backend.log" {
      copytruncate
      daily
      rotate 5
      compress
      delaycompress
      missingok
      notifempty
    }


To terminate the installation of the system services you must::

   # For Python 2 installation
   sudo cp /usr/local/share/alignak-webui/bin/systemd/python2/alignak-webui-centos7.service /etc/systemd/system/alignak-webui.service

   # For Python 3 installation
   sudo cp /usr/local/share/alignak-webui/bin/systemd/python3/alignak-webui-centos7.service /etc/systemd/system/alignak-webui.service

   ll /etc/systemd/system
      -rw-r--r--. 1 root root  777 May 24 17:48 /lib/systemd/system/alignak-webui.service

   sudo systemctl enable alignak-webui
      Created symlink from /etc/systemd/system/multi-user.target.wants/alignak-webui.service to /usr/lib/systemd/system/alignak-webui.service.

.. note:: for Python 3 version, replace ``python`` with ``python3`` in the package and post-installation script names.



Installation with PIP
---------------------

**Note** that the recommended way for installing on a production server is mostly often to use the packages existing for your distribution.

Nevertheless, the pip installation provides:
- a startup script using an uwsgi server,
- for FreeBSD users, an rc.d service script,
- for systemctl based systems (Debian, CentOS), an alignak-webui service unit.

All this stuff is available in the repository *bin* directory and is copied locally in the */usr/local/share/alignak-webui* directory.

End user installation
~~~~~~~~~~~~~~~~~~~~~

Installing with pip::

    sudo pip install alignak-webui

The required Python modules are automatically installed if not they are not yet present on your system.


From source
~~~~~~~~~~~

Installing from source::

    git clone https://github.com/Alignak-monitoring/alignak-webui
    cd alignak-webui
    pip install .


For contributors
~~~~~~~~~~~~~~~~

If you want to hack into the codebase (e.g for future contribution), just install like this::

    pip install -e .


Install from source without pip
-------------------------------

If you are on Debian::

    sudo apt-get -y install python python-dev python-pip git


Get the project sources::

    git clone https://github.com/Alignak-monitoring/alignak-webui


And then install::

    cd alignak-webui
    pip install .
