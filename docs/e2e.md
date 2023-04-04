# SET UP E2E TESTING SERVER 

## Prerequisites
- Prepare stable data, you can clone from staging database by following [this doc](./clone_staging_db.md).
- Assume you already set up for the local environment follow the `readme.md` doc.

## Note
- If you haven't done it before, it'd better to check out to the new branch rather than use the dev or the current branch because we will upload our database later, and it can override our own database file, which can lead to fail test on our CI.

## Set up
- Run this command to prepare test data and save it to cloud for CI testing:
```shell
bin/manage.sh prepare_test_db
```
- This command should be run everytime the data schema change so that the cloud data file uses for the FE can be updated.

## Run test server
- Run this command to start the test server for the FE integration test:
```shell
docker-compose -f docker-compose-itest.yml up
```
- You will see the app start at the http://0.0.0.0:9000/
