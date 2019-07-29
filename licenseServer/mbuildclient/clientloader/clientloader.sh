#!/bin/bash
source setenv.sh

LOCAL_MBUILDCLIENT_CLIENT_PATH=$LOCAL_MBUILDCLIENT_ROOT_PATH/client/licenseClient.py
LOCAL_MBUILDCLIENT_LOCALVERSION=$LOCAL_MBUILDCLIENT_ROOT_PATH/version.local
LOCAL_MBUILDCLIENT_REMOTEVERSION=$LOCAL_MBUILDCLIENT_ROOT_PATH/version.remote
REMOTE_MBUILDCLIENT_ROOT_PATH=/home/sssw/licenseClient
REMOTE_MBUILDCLIENT_VERSION=$REMOTE_MBUILDCLIENT_ROOT_PATH/version
REMOTE_MBUILDCLIENT_CLIENT_PATH=$REMOTE_MBUILDCLIENT_ROOT_PATH/client/licenseClient.py

sshpass -p ss!@#$ ssh sssw@10.253.4.17 "cat $REMOTE_MBUILDCLIENT_VERSION" > $LOCAL_MBUILDCLIENT_REMOTEVERSION

if [ $? != 0 ];then
	echo "ssh error"
	exit 3
fi

remote_client_version=`cat "$LOCAL_MBUILDCLIENT_REMOTEVERSION"`
local_client_version=`cat "$LOCAL_MBUILDCLIENT_LOCALVERSION"`

echo "remote=$remote_client_version"
echo "local=$local_client_version"

if [ $remote_client_version != $local_client_version ]; then
	sshpass -p ss!@#$ scp sssw@10.253.4.17:$REMOTE_MBUILDCLIENT_CLIENT_PATH $LOCAL_MBUILDCLIENT_CLIENT_PATH
	echo $remote_client_version > $LOCAL_MBUILDCLIENT_LOCALVERSION
	echo "updating"
fi

rm -rf $LOCAL_MBUILDCLIENT_REMOTEVERSION