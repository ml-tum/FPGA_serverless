# OpenFaas installation


## Prerequisite
Make sure that the private repo is configured


## Install Arkade
```
curl -sLS https://get.arkade.dev | sudo sh
arkade get faas-cli helm 
sudo mv /home/ubuntu/.arkade/bin/faas-cli /usr/local/bin/
sudo mv /home/ubuntu/.arkade/bin/helm /usr/local/bin/
```

## OpenFaas
```
git clone https://github.com/openfaas/faas-netes.git
cd faas-netes
kubectl apply -f namespaces.yml
helm repo add openfaas https://openfaas.github.io/faas-netes/
helm upgrade openfaas --install openfaas/openfaas --namespace openfaas -f chart/openfaas/values.yaml
```

## Use patched OpenFaas (supports setting RuntimeClass)
```
cd faas-netes
nano chart/openfaas/values.yaml
```
Under `faasnetes:` replace the image 
`  image: ghcr.io/openfaas/faas-netes:0.17.1`
by
`  image: docker.io/ccgroup47/myrepo:faas-netes-rtc`

Update the cluster deployment:
`helm upgrade openfaas --install openfaas/openfaas --namespace openfaas -f chart/openfaas/values.yaml`


## Apply profile
nano ~/fpga/openfaas_profiles.yaml
```
kind: Profile
apiVersion: openfaas.com/v1
metadata:
    name: kata-urunc
    namespace: openfaas
spec:
    runtimeClassName: kata-urunc

---

kind: Profile
apiVersion: openfaas.com/v1
metadata:
    name: kata
    namespace: openfaas
spec:
    runtimeClassName: kata
```
Then 
```
kubectl apply -f ~/k8s/kata-runtimeClass.yaml 
kubectl apply -f ~/trans/kata_urunc_runtimeClass.yaml
kubectl apply -f ~/fpga/openfaas_profiles.yaml
```



## Access the API
The API is accessible from inside the pod network. It requires a password, which has already been generated.
In order to access the API from outside the pod network we can hook up a port forward to the gateway pod.
```
kubectl port-forward -n openfaas svc/gateway 8080:8080 &
kubectl get secret -n openfaas basic-auth -o jsonpath="{.data.basic-auth-password}" | base64 --decode | faas-cli login --username admin --password-stdin
```
