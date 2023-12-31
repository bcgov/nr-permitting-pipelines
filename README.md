﻿# nr-permitting-pipelines

**Update Dec. 28**: Moved Docker image from OC Imagestream to GHCR to be accessed by Airflow DAG. 

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

