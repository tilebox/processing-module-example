# demo-worker

Demo-worker is a demonstration project showing how to create a service and Docker image
that can act as a worker in the Tilebox processing module.

The required binaries are installed through Poetry, tasks are created recursively, forming a
directed acyclic graph (DAG) in the shape of a binary tree.

## Demo setup

To run the demo locally create a namespace, then open the `poetry shell`, and start a worker. Replace the `<description>`
fields with your own values.

```commandline
pyenv-init
pyenv shell 3.8-dev
poetry shell

CACHE_DIRECTORY=<cache_directory>
    tilebox-processing node \
    --tilebox-processing-namespace-id <namespace_id> \
    --tilebox-processing-namespace-token <namespace_token>
```

Then submit a job to the namespace.

```commandline
tilebox processing jobs create --namespace-id <namespace_id> --description julia900 -- calculate-julia 900 0 900 julia-900.png
```
