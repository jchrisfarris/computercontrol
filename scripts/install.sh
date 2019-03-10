#!/bin/bash

REPOBASE="https://raw.githubusercontent.com/jchrisfarris/computercontrol/master/"
BASEDIR="/rm17/cc/"


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


# Install LaunchAgent
curl -s ${REPOBASE}/mac_files/com.room17.computercontrol.plist > ~/Library/LaunchAgents/com.room17.computercontrol.plist
curl -s ${REPOBASE}/mac_files/computercontrol.sudo > /private/etc/sudoers.d/computercontrol

launchctl load ~/Library/LaunchAgents/com.room17.computercontrol.plist


# Download Scripts
curl -s ${REPOBASE}/scripts/download_scripts.sh | bash

