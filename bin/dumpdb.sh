#!/usr/bin/env bash
set -e

dct="docker-compose -f docker-compose-itest.yml"
# export current dev db for backup
echo "Start to create dev backup"
docker-compose exec -T db pg_dump -U ipno ipno > backup.pgsql

# clean up integration test env
echo "Clean up test environment"
$dct down --volumes

# start integration db
echo "Start to test db"
$dct up --detach db-test

sleep 2

# dumb dev db to test db
echo "Start to dump dev db to test db"
$dct exec -T db-test psql -U ipno ipno < backup.pgsql

# run script to modify current database : clean up & transform
echo "Start to clean up test db"
$dct run --rm web ipno/manage.py prepare_test_db

mkdir -p temp-integration

# export database for testing
echo "Start to export test db"
$dct exec -T db-test pg_dump -U ipno ipno > temp-integration/testing.pgsql

# export database for interactive testing
echo "Start to export clean test db"
$dct exec -T db-test pg_dump -c -U ipno ipno > temp-integration/data.pgsql

# upload db files to cloud storage
CIRCLE_BRANCH=$(git rev-parse --abbrev-ref HEAD)

gsutil cp -r temp-integration/** gs://llead-integration-db/"${CIRCLE_BRANCH}"/

# clean up
rm -rf temp-integration/
