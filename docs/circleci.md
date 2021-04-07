# Circleci

## Environment Variables
### COVERALLS_REPO_TOKEN
- Configuration for coveralls

### DJANGO_SECRET_KEY
- Django secret key to run tests

### GCLOUD_SERVICE_KEY_BASE64
- Using for google oauth
- Create a service account -> download the JSON-formatted key file
- cat <gcloud-credentials.json> | base64