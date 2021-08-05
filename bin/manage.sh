#!/usr/bin/env bash

set -e

if [ "$1" == "-h" -o "$1" == "--help" ]; then
    echo "Run manage command."
    echo ""
    echo "Usage: `basename $0` {--production|--staging|--dev(default)} <command>"
    echo "       `basename $0` {-h|--help}"
    exit 0
elif [ -z "$1" ]; then
    echo "Must specify command."
    exit 1
elif [ "$1" == "--production" ]; then
    NAMESPACE=default
elif [ "$1" == "--staging" ]; then
    NAMESPACE=ipno-staging
else
    if [ "$1" == "--dev" ]; then
        shift
    fi

    docker-compose run web ipno/manage.py $@
    exit 0
fi

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

cd $DIR/..

POD_NAME="$(kubectl get pods --selector=app=ipno-backend -n $NAMESPACE --output=jsonpath={.items[0].metadata.name})"
shift

echo "kubectl exec -it -n $NAMESPACE $POD_NAME -c ipno-backend-app -- ipno/manage.py $@"
kubectl exec -it -n $NAMESPACE $POD_NAME -c ipno-backend-app -- ipno/manage.py $@
