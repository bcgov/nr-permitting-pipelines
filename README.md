# nrm-permitting-pipelines

Build locally: 
```sh
docker build -t image-registry.apps.emerald.devops.gov.bc.ca/a1b9b0-dev/pipeline-test:<tag> .
```

Push to OpenShift Image Registry: 
```sh
oc registry login
```
```sh
docker push image-registry.apps.emerald.devops.gov.bc.ca/a1b9b0-dev/pipeline-test:<tag>
```

Create OpenShift ConfigMap: 
```sh
oc create configmap <config map name> --from-file=rrs_extract.json
```

Deploy: 
```sh
oc apply -f deployment.yaml
```
