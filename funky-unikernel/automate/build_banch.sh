#!/bin/bash

OUT_DIR="images"
GIT_USER=""
GIT_TOKEN=""
INUSER=$USER
BASE=0
ALL=0

usage()
{ 
	echo "Build a unikernel image for the specified benchmarks"
	echo "Usage:./build_bench.sh [-d] -u <git_username> -y <git_token> <list_of_benchmarks>"
	echo "	-h	Display this help message"
	echo "	-d	Directory to save the images (default: images)"
	echo "	-a	Build all benchmarks"
	echo "	-b	Build base docker image"
	echo "	-u	Directory to save the images (required if -b)"
	echo "	-t	Directory to save the images (required if -b)"
	exit 1
}

while getopts "ahbd:u:t:" flag
do
	case "$flag" in
		h)
			usage
		;;
		a)
			ALL=1
		;;
		b)
			BASE=1
		;;
		d)
			OUT_DIR=$OPTARG
		;;
		u)
			GIT_USER=$OPTARG
		;;
		t)
			GIT_TOKEN=$OPTARG
		;;
	esac
done

if [ "$BASE" -eq "1" ]
then
	if [ -z "$GIT_USER" ] || [ -z "$GIT_TOKEN" ]
	then
		echo "ERROR: git username or token has not been set"
		echo "Please define git username and token"
		usage
	fi
	sudo DOCKER_BUILDKIT=1 docker build --network=host -t funky/base \
		--build-arg "USER=$GIT_USER" --build-arg "TOKEN=$GIT_TOKEN" \
		-f Dockerfile .
fi

if [ "$ALL" -eq "1" ]
then
	sudo DOCKER_BUILDKIT=1 docker build --network=host -t funky/benchs \
		-f Dockerfile.all \
		--target artifacts --output type=local,dest=$OUT_DIR .
	exit 0
fi

shift $((OPTIND -1))

while test $# -gt 0; do
	echo $1
	sudo DOCKER_BUILDKIT=1 docker build --network=host -t funky/benchs \
		--build-arg "BENCH=$1" -f Dockerfile.benchs \
		--target artifacts --output type=local,dest=$OUT_DIR .
	shift
	sudo chown -R $INUSER:$INUSER $OUT_DIR
done

##sudo DOCKER_BUILDKIT=1 docker build --network=host -t funky/benchs \
##	--build-arg "USER=$GIT_USER" --build-arg "TOKEN=$GIT_TOKEN" \
##	--target artifacts --output type=local,dest=$OUT_DIR .

