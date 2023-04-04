# Clone staging database

This doc help you to download and seed your database by staging database, so that you won't need to import the data by running long time command `import_data`.

## Prerequisites
- You need to have the access to the GCS project and have enough permission to access to the Staging Cloud SQL.

## How to
- First, visit [Google Cloud SQL Console](https://console.cloud.google.com/sql/instances) and select the staging db.
- In the overview tab, click on export and choose the following options:
  - File format: SQL
  - Data to export: `your current database`
  - Destination: `Your target bucket` and modify the filename as you want.
- Then click `Export` and wait for the database export process.
- After the export process has been done, you can click on the link of the notification or visit the bucket, then select the file which have the filename you modified above and click download.
- Move the downloaded file to the `IPNO-backend` project and rename it as `db.pgsql`
- Down all the docker containers & volumes by calling: `docker-compose down --volumes`
- Run `docker-compose up db` to re-create the db container.
- Run this command to import the data from `db.pgsql` to our pg database:
```bash
docker-compose exec -T db psql -U ipno ipno < db.pgsql
```
- After that you can run `bin/manage.sh migrate` to update the schema to the latest version.