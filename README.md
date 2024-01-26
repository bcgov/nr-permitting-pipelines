# nr-permitting-pipelines

##  Use of GHCR
Container images are built automatically and pushed to the GHCR any time there is a push or PR to the **main** branch. Images are named according to the file path and tagged with the branch name. Use the image name in an Airflow DAG to create a job using the nr-permitting-pipelines container. See Airflow example here: [permitting_pipeline_ats.py](https://github.com/bcgov/nr-airflow/blob/e45c83f933d1f96e479a36a3e765dabd61e1ff2e/dags/permitting_pipeline_ats.py#L18C16-L18C58) 

Usage example: 
```sh
docker pull ghcr.io/bcgov/nr-permitting-pipelines:main
```

Alternatively, there is this manual workflow: 

Build locally: 
```sh
docker build -t image-registry.apps.emerald.devops.gov.bc.ca/a1b9b0-dev/<pipeline name>:<tag> .
```

Push to OpenShift Image Registry: 
```sh
oc registry login
```
```sh
docker push image-registry.apps.emerald.devops.gov.bc.ca/a1b9b0-dev/<pipeline name>:<tag>
```

Deploy to OpenShift. Note: Make sure to update the deployment name, env (config maps, secrets), & image SHA in the .yaml file.: 
```sh
oc apply -f deployment.yaml
```

Note: If you add a new Dockerfile, a new GitHub Actions workflow needs to be created to publish the container to the GHCR.



