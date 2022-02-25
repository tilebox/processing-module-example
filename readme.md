# demo-worker

Demo-worker is a demonstration project showing how to create a service and Docker image
that can act as a worker in the adler-x processing module.

The required binaries are installed through Poetry, tasks are created recursively, forming a
directed acyclic graph (DAG) in the shape of a binary tree.

## Demo setup

To run the demo locally, first open the `poetry shell`, and start a test-worker.

```commandline
pyenv-init
pyenv shell 3.8-dev
poetry shell

adler-x-task test-worker \
   --adler-x-working-directory (realpath .) \
   --host localhost \
   --port 8086 \
   --adler-x-cache-directory ~/scratch/test-adler-x-task-worker/cache
```

Then submit a job to the test-worker.

```commandline
adler-x-task create-job \
    --description "Julia test" \
    --worker-pool-url "http://localhost:8086" \
    --adler-x-task-server-url "http://localhost:8086" \
    -- calculate-julia 2000 0 2000
```
