# Common Issues & Solutions: 

### Not able to pull from Docker Hub:
**Solution 1:** Use Artifactory remote proxy
```sh 
    image: artifacts.developer.gov.bc.ca/docker-remote/openmetadata/server
    imagePullSecrets:
        - name: artifactory-pull
```    
**Solution 2:** Use GitHub container registry
```sh 
  image:
    registry: ghcr.io
    repository: bcgov/nr-containers/[your app]/[container]
    tag: [tag from FROM line in Dockerfile]
```

### Dir permission denied:
**Error Example:** unable to create open /etc/temporal/config/docker.yaml: permission denied 
**Solution 1:** Mount a volume for the file path
```sh 
  extraVolumeMounts:
    - name: dir
      mountPath: /tmp

  extraVolumes:
    - name: dir
      emptyDir: {}
```
**Solution 2:** Edit Dockerfile to explicitly grant permission
```sh 
RUN chmod -R g+rwX /dir
```

### Service account permissions:
**Error example:**
roles.rbac.authorization.k8s.io "airbyte-admin-test" is forbidden (groups=["system:authenticated:oauth" "system:authenticated"]) is attempting to grant RBAC permissions not currently held

**Solution:** created Role and Role Binding (assign needed permissions to Service Account)

### Binding to privileged ports as non-root user
**Error example:** "[emerg] bind() to 0.0.0.0:80 failed (13: Permission denied)"

**Solution:** Set container port to 8080 instead of 80. Service ports can be 80. 

### Some built-in init process is failing 
**Solution:** Use LifeCycle Hooks
```sh 
  lifecycle:
    postStart:
      exec:
        command: ["/bin/bash", "-c", "source /opt/bitnami/airflow/venv/bin/activate &&  pip install  --trusted-host artifacts.developer.gov.bc.ca --index-url=https://artifacts.developer.gov.bc.ca/artifactory/pypi-remote  apache-airflow-providers-airbyte"]  
```
     
## Pod crashing with OOM error
**Solution:** Increase memory limit (keep requests as low as possible)

## Pods failing readiness and liveliness probes
**Solution:** Extend initalDelaySeconds. Usually just means the pod is taking a while to start up. 

# Artifactory Notes

## Docker login for BC Gov Artifactory
```sh
docker login https://artifacts.developer.gov.bc.ca/artifactory
```

## Create secret with docker login:
```sh 
oc create secret docker-registry artifactory `
    --docker-server=artifacts.developer.gov.bc.ca `
    --docker-username=default-a1b9b0-sroovq `
    --docker-password=<password> `
    --docker-email=default-a1b9b0-sroovq@a1b9b0-tools.local
```

## Pass secret to service accounts:
```sh
oc secrets link default artifactory
```

## Helpful Helm commands

## Sourcing charts
```sh
helm repo add airbyte https://airbytehq.github.io/helm-chart
```
```sh
helm pull airbyte/airbyte 
```
```sh 
helm repo update airbyte
```
```sh
helm package airbyte --version 0.48.0 
```

## Configuring values.yaml
```sh
helm show values airbyte/airbyte > values.yaml
```

```sh
helm upgrade --install abi-test-release-ab airbyte/airbyte -n a1b9b0-tools -f values.yaml --debug      
```

## Deploying to OpenShift
```sh
helm install abi-test-release-ab .
```


