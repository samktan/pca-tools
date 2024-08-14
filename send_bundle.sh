#!/usr/bin/sh

# send_bundle.sh
# sam.k.tan@oracle.com
# AUG-2024

if [ -z $1 ]; then
    echo "$0 <bundle-file>"
    exit 1
fi

CWD="$(pwd -P)"
case $1 in
        /*) BUNDLE_FILE="$(realpath $1)" ;;
        *) BUNDLE_FILE="$(realpath $PWD/$1)" ;;
esac

CURL=$(which curl)
if [ -z ${CURL} ]; then
    exit 1
fi

echo "Bundle: ${BUNDLE_FILE}"
echo -n "SR #: "; read MOS_SR
echo -n "MOS username / email: "; read MOS_LOGIN

if [ -z ${MOS_SR} ] || [ -z ${MOS_LOGIN} ]; then
	echo "Missing input ... exiting."
	exit 1
fi

set -x
${CURL} \
    --verbose \
    --progress-bar \
    --proxy "${https_proxy}" \
    --user "${MOS_LOGIN}" \
    --upload-file "${BUNDLE_FILE}" \
    "https://transport.oracle.com/upload/issue/${MOS_SR}/" \
