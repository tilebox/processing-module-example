# demo-worker

Demo-worker is a demonstration project showing how to create a service and Docker image
that can act as a worker in the Tilebox processing module.

The required binaries are installed through Poetry, tasks are created recursively, forming a
directed acyclic graph (DAG) in the shape of a binary tree.

## Demo setup

To run the demo locally create a namespace, then open the `poetry shell`, and start a worker. Replace
the `<description>`
fields with your own values.

```commandline
pyenv-init
pyenv shell 3.8-dev
poetry shell

CACHE_DIRECTORY=<cache_directory> tilebox-processing node \
    --tilebox-processing-namespace-id <namespace_id> \
    --tilebox-processing-namespace-token <namespace_token>
```

Then submit a job to the namespace.

```commandline
tilebox processing jobs create --namespace-id <namespace_id> --description julia900 -- calculate-julia 900 0 900 ../julia-900.png
```

## Using Docker

Build the Docker container by running `docker build --build-arg TILEBOX_API_KEY=$TILEBOX_API_KEY . -t demo-worker`,
substituting
your TILEBOX_API_KEY`.

Then start the worker by calling the following command, substituting or adjusting the parameters as needed.

```commandline
docker run --rm -it --env TILEBOX_PROCESSING_NAMESPACE_ID=<namespace> --env TILEBOX_PROCESSING_NAMESPACE_TOKEN=<namespace_token> -v (pwd)/cache:/cache --env CACHE_DIRECTORY=/cache -v (pwd)/output:/output demo-worker:latest
```

A command can be issued by calling e.g.

```commandline
tilebox processing jobs create --namespace-id <namespace> --description julia700 -- calculate-julia 700 0 700 /output/julia-700.png
```
