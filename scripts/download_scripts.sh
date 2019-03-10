#!/bin/bash

# Script to update the scripts from Github

REPOBASE="https://raw.githubusercontent.com/jchrisfarris/computercontrol/master/scripts/"
SCRIPTS="download_scripts.sh mute.sh sleep.sh poll_for_commands.py"
SCRIPT_HOME="/rm17/cc/scripts"

if [ ! -d $SCRIPT_HOME ] ; then
    mkdir -p $SCRIPT_HOME
fi

for s in $SCRIPTS ; do
    curl -s ${REPOBASE}/${s} > ${SCRIPT_HOME}/${s}
    chmod 755 ${SCRIPT_HOME}/${s}
done