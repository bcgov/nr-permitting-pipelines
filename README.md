# nrm-permitting-pipelines

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

Create OpenShift ConfigMap Note: Make sure your json file is named extract.json or whatever matches the env variable the Python script.: 
```sh
oc create configmap <config map name> --from-file=extract.json
```

Get the latest SHA for the image: 
```sh
oc describe imagestream <pipeline name>
```

Deploy to OpenShift. Note: Make sure to update the deployment name, env (config maps, secrets), & image SHA in the .yaml file.: 
```sh
oc apply -f deployment.yaml
```
