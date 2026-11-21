#!/bin/bash

# For launching the Flexxbutt from crontab
# Recommended crontab setting:
# */2 * * * * /bin/bash <path to this shell script>

# Firing more frequently than this is just extra overhead, firing less
# frequently means the bot will be down for longer if it crashes and
# needs to restart.

## Location of the code for the bot.
BOTHOLE=/home/ss13/discordbot

## Location of yuor BYOND install
BYONDHOLE=/home/ss13/byond

cd ${BOTHOLE}
source ./env/bin/activate # Activate the python virtual environment

source ${BYONDHOLE}/bin/byondsetup

# Check if the process is still running.
PROCESSIDCHECK=$(ps ax | grep -v grep | grep discord_bot.py)
if [ -z "$PROCESSIDCHECK" ]
then
  echo "Can't find Georgie. Starting the bot..."
  eval "python3 ./discord_bot.py > crudlog 2>&1"
else
  echo "Bot still running. We're ok!"
fi
