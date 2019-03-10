#!/bin/bash

REPOBASE="https://raw.githubusercontent.com/jchrisfarris/computercontrol/master/"
BASEDIR="/rm17/cc/"

CONFIG=$1

if [ ! -f $CONFIG ] ; then
    echo "Cannot find config file or not specificed."
    echo "usage: $0 <config>"
    exit 1
fi

if [ `whoami` != "root" ] ; then
    echo "must run as sudo"
    exit 1
fi


if [ ! -x /usr/local/bin/aws ] ; then
    echo "AWS CLI not installed, cannot continue"
    exit 1
fi

if [ ! -d $BASEDIR ] ; then
    mkdir -p $BASEDIR
fi

if [ ! -d $BASEDIR/logs ] ; then
    mkdir -p $BASEDIR/logs
fi

# Allow user to write to logdir
chmod 777 /rm17/cc/logs/

cp $CONFIG /rm17/cc/config

# Download Scripts
curl -s ${REPOBASE}/scripts/download_scripts.sh | bash

pip install boto3

# Install LaunchAgent
curl -s ${REPOBASE}/mac_files/com.room17.computercontrol.plist > /rm17/cc/com.room17.computercontrol.plist
# curl -s ${REPOBASE}/mac_files/computercontrol.sudo > /private/etc/sudoers.d/computercontrol

sudo -u leo -s "launchctl load /rm17/cc/com.room17.computercontrol.plist"




