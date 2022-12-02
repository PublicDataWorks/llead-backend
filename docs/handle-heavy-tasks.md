# Handle Heavy Tasks
Find more information about `Asynchronous Tasks With Django and Celery` in this [link](https://realpython.com/asynchronous-tasks-with-django-and-celery/)
## 1. Introduction
- In IPNO project, there are such long-running tasks such as rebuilding indexes. Normally, the execution of these works impacts
on the latency of API calls. To deal with this difficulty, the tasks should be processed asynchronously
- `Celery` is a task queue implementation for Python web applications. It is used to run the tasks asynchronously. 
Hence, `celery` can offload tasks from the main request/response cycle within `Django`.
- `Redis` works as a message broker between `Celery` and `Django`.

## 2. Celery and Redis
###a. Celery
- Task queue is generally a queue that contains multiple tasks we would like to perform respectively. The tasks are
usually considered to be heavy. Thus, they take time to process. A task queue’s input is a unit of work called a task. 
Dedicated worker processes constantly monitor task queues for new work to perform.
- Celery communicates via messages, usually using a broker to mediate between clients and workers. To initiate a task
the client adds a message to the queue, the broker then delivers that message to a worker.
- A Celery system can consist of multiple workers and brokers, giving way to high availability and horizontal scaling.

### b. Redis
- Redis is an in-memory data structure store, used as a distributed, in-memory key-value database, cache and message
broker, with optional durability.
- In IPNO project, `Redis` is used for message broker which serve for `Celery` and `Django`. We plan to implement
caching with `Redis` in near future
- IN Production, `Redis sentinel` is implemented to monitor redis servers. If one of them dies, `sentinel` will decide
which server will be the master.

## 3. Tasks
###Prerequisites: Install `Redis` and `Celery` (find the details in `setup-redis.md`)
a. Create tasks
- Create tasks in `tasks.py`
- Add `@run_task` and `@shared_task` decorators on each task. Make sure `@shared_task` should go first so that the task has property `delay`
- The purpose of `@run_task` is to make the task run synchronously if `celery` is not present

b. Test tasks
- Run command `docker-compose up celery` to open attach celery to watch celery's logs
- Run your task
- Check on terminal if your task is received and processed
