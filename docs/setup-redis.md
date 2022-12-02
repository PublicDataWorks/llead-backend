# Redis setup
## 1. Local setup
- Add `CELERY_BROKER_URL` into env (Optional)
- Run `bin/dev.sh` to install `celery` and `redis` packages

## 2. Kubernetes setup

### a. Staging (Standalone)
- Create namespace `redis-staging`
- Go to `redis-staging` namespace
- Run `helm install redis --set architecture=standalone bitnami/redis` to install standalone redis
- Follow the instruction on terminal to get redis `password` and test for connection to redis
- Update `broker-url` in celery `secret` of `ipno-staging` namespace so that the new redis password should be included. 
`broker-url` should look like `redis://default:{password}@redis.redis-staging:6379`
- Apply new `celery.yml`
- Check if the pod is up

### b. Production (Sentinel)
- Create namespace `redis-production`
- Go to `redis-production` namespace
- Run `helm install redis --set sentinel.enabled=true --set architecture=replication bitnami/redis` to install redis
 sentinel
- Follow the instruction on terminal to get redis `password` and test for connection to redis
- Update `broker-url`, `sentinel-master-name`, and `sentinel-password` in celery `secret` of `ipno-production` namespace
so that the new redis password should be included. `broker-url` should look like `sentinel://default:{password}@redis.redis-production:26379`
- Apply new `celery.yml`
- Check if the pod is up

## 3. Testing
- Go to `django-admin` page
- Change a department profile and try to save it
- Check logs of `celery` pod to see if the task is received and processed.
