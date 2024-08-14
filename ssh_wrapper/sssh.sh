#!/usr/bin/sh

# Name: sssh.sh
# Author: sam.k.tan@oracle.com
# JUN-2024

# save the input parameters
PARAMS="$*"

# get the paths to the executables
SSH=$(which ssh)
SSHKEYGEN=$(which ssh-keygen)
SSSH="SSSH:"

echo "${SSSH} Sam's SSH by sam.k.tan@oracle.com"

# run SSH with the given parameters
${SSH} ${PARAMS}

# if SSH exits with status code 255 ...
if [ $? -eq 255 ]
then
	# extract the hostname from the SSH parameters
	HOST=$(${SSH} -G ${PARAMS} | grep -i '^hostname' | cut -d ' '  -f2)

	# check if hostname exists in known_hosts file
	${SSHKEYGEN} -F ${HOST} > /dev/null 2>&1

	# if hostname does not exist, then exit
	if [ $? -eq 1 ]
	then
		exit 0
	fi

	# since hostname exists, ask to delete and try again
	echo "${SSSH} Matching hostname found in known_hosts file."
	echo "${SSSH} Do you want to remove the offending host key(s) and retry the connection?"
	echo "${SSSH} Only YES is accepted, any other key to cancel."
	read RESPONSE

	if [ "xx${RESPONSE}xx" == "xxYESxx" ]
	then
		echo "${SSSH} Removing offending keys ..."
		${SSHKEYGEN} -R ${HOST}

		echo "${SSSH} Retrying SSH ..."
		${SSH} ${PARAMS}
	else
		echo "${SSSH} Exiting ... no changes made."
	fi
fi

