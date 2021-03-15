#!/usr/bin/env bash

# Andre Augusto Giannotti Scota (https://sites.google.com/view/a2gs/)

# Script exit if a command fails:
#set -e

# Script exit if a referenced variable is not declared:
#set -u

# If one command in a pipeline fails, its exit code will be returned as the result of the whole pipeline:
#set -o pipefail

# Activate tracing:
#set -x

if [ "$#" -ne 4 ]; then
	echo "Illegal number of parameters"
	echo "echo [GROUP] [APPNAME] [PACKAGE] [VERSION]"
else
	checksum=`sha1sum $1/$3 | cut -f1 -d' '`
	echo -e "$2\t$4\t$3\t$checksum" >> $1/apps.txt
	echo -e "Added into $1/apps.txt: [$2\t$4\t$3\t$checksum]"
fi