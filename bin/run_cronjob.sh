#!/usr/bin/env bash

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Schedule the cronjobs on production or staging."
    echo ""
    echo "Usage: `basename $0` {--production|--staging} <backend_image_tag> <django_command> <schedule>"
    echo "       `basename $0` {-h|--help}"
    echo "Example:"
    echo "    $ `basename $0` --staging latest import_data @daily"
    exit 0
elif [ -z "$1" ]; then
    echo "Must specify either --production or --staging."
    exit 1
elif [ "$1" == "--production" ]; then
    NAMESPACE=default
elif [ "$1" == "--staging" ]; then
    NAMESPACE=ipno-staging
else
    echo "Unrecognized first argument. See help with --help"
    exit 1
fi

if [ -z "$2" ]; then
    echo "Must specify backend image tag as second argument."
    exit 1
else
    IMAGE_TAG="$2"
fi

if [ -z "$3" ]; then
    echo "Must specify backend image tag as third argument."
    exit 1
else
    CRONJOB_COMMAND="$3"
fi

if [ -z "$4" ]; then
    echo "Must specify cronjob schedule as fourth argument."
    exit 1
else
    CRONJOB_SCHEDULE="$4"
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd $DIR/..

CRONJOB_NAME="$(echo $CRONJOB_COMMAND | tr -s '_' | tr '_' '-')"

export BACKEND_IMAGE_TAG=$IMAGE_TAG
export CRONJOB_NAME=$CRONJOB_NAME
export CRONJOB_COMMAND=$CRONJOB_COMMAND
export CRONJOB_SCHEDULE=$CRONJOB_SCHEDULE

kubectl config set-context --current --namespace=$NAMESPACE

cat kubernetes/cronjob.yml | envsubst | kubectl apply -f - -n $NAMESPACE
kubectl get cronjobs -n $NAMESPACE
