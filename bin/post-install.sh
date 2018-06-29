#!/bin/sh

# --------------------------------------------------------------------------------
# This script is doing the post-install processing for Alignak WebUI application:
# - checking and creating alignak:alignak user account
# - installing the python dependencies for Alignak.
# -----
# Command line parameters may be used to change the default 'alignak'
# user account and the default '/usr/local' prefix
# --------------------------------------------------------------------------------
# Default is to use an alignak account
ACCOUNT=$1
# Default is to use /usr/local prefix
PREFIX=$2
# Parse command line arguments
if [ $# -eq 0 ]; then
    ACCOUNT="alignak"
    PREFIX="/usr/local"
fi
if [ $# -eq 1 ]; then
    PREFIX="/usr/local"
fi

echo "-----"
echo "Alignak-WebUI post-install"
echo "-----"

echo "Detecting OS platform"
platform='unknown'
unamestr=`uname`
echo "-> system is: $unamestr"
if [ "$unamestr" = 'Linux' ]; then
   platform='linux'
elif [ "$unamestr" = 'FreeBSD' ]; then
   platform='freebsd'
fi
echo "-> found ${platform}"
if [ "$platform" = 'linux' ]; then
   ## Create user and group
   echo "Checking / creating '$ACCOUNT' user and users group"
   id -u $ACCOUNT &>/dev/null || useradd $ACCOUNT --system --no-create-home --user-group -c "Alignak daemons user"
elif [ "$platform" = 'freebsd' ]; then
   ## Create user and group
   echo "Checking / creating '$ACCOUNT' user and users group"
   id -u $ACCOUNT &>/dev/null || pw adduser $ACCOUNT -d /nonexistent -s /usr/sbin/nologin -c "Alignak daemons user"
fi

echo "Installing python packages dependencies from requirements.txt..."
sudo pip install -r $PREFIX/share/alignak-backend/requirements.txt
echo "Installed."
echo "Creating some necessary directories"
mkdir -p $PREFIX/var/run/alignak-backend
chown -R $ACCOUNT:$ACCOUNT $PREFIX/var/run/alignak-backend
mkdir -p $PREFIX/var/log/alignak-backend
chown -R $ACCOUNT:$ACCOUNT $PREFIX/var/log/alignak-backend
echo "Created."
