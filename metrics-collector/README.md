# Metrics Collector

Service deployed on each node that receives FPGA usage metrics, including reconfigurations and deployed bitstreams. Metrics are aggregated and synchronized with Kubernetes through key-value annotations. This state is continuously updated and is used by the scheduler extension plugin to make informed scheduling decisions.

## Authentication with Kubernetes

Currently, the metrics collector uses the local kubeconfig file to authenticate with the Kubernetes API. This is done by setting the `KUBECONFIG` environment variable to the path of the kubeconfig file.

## Versioning

FPGA state is currently versioned to simplify migrations in the future. This is required to gracefully handle collector restarts and pick up on the recent metrics instead of starting at zero. The smaller the sliding window used by the FPGA usage tracker, the less important this is.

## Testing the system in Minikube (locally)

## Make custom scheduler image available in cluster

Follow the instructions in `fpgascheduling.go` in the Kubernetes scheduler plugin or [check the Minikube docs](https://minikube.sigs.k8s.io/docs/handbook/pushing/).

```
# don't assign final tag because used image cannot be overwritten by minikube
make scheduler
# or
docker build -t registry.k8s.io/kube-scheduler:tmp -f Dockerfile-scheduler .
minikube image load registry.k8s.io/kube-scheduler:tmp

minikube ssh

# once the image is moved, rename it to the final tag
docker image tag registry.k8s.io/kube-scheduler:tmp registry.k8s.io/kube-scheduler:v1.26.3

# then remove the old container and previous image
docker container rm -f <container_id> && docker image rm registry.k8s.io/kube-scheduler:tmpbuild

```

## Create cluster with multiple nodes

```
# prepare minikube cluster
minikube start
minikube node add
miniube node add
```

Make sure the nodes are all ready

```
NAME           STATUS   ROLES           AGE     VERSION
minikube       Ready    control-plane   18m     v1.26.3
minikube-m02   Ready    <none>          9m48s   v1.26.3
minikube-m03   Ready    <none>          9m23s   v1.26.3
```

## Start metrics collectors and push metrics

To populate each node with FPGA usage metrics, start up the metrics collector.

```
# start metrics collector "on" each node (just run multiple instances locally)
go run . --node minikube --port 8080
go run . --node minikube-m02 --port 8081
go run . --node minikube-m03 --port 8083
```

Next, you can either start real applications in Funky Monitor and point the metrics collector endpoint to the respective collector, or you can send mock requests manually like below if you cannot run Funky Monitor locally.

```
# send a request to control plane / primary node
curl --request POST \
  --url http://localhost:8080/ \
  --header 'Content-Type: application/x-www-form-urlencoded' \
  --data timestamp_ms=1689181419598 \
  --data reconfiguration_ms=10000 \
  --data bitstream_identifier=def

```

## Create workloads

Once metrics are in the system, invoke the scheduler by creating a new workload and enabling FPGA scheduling for it in the pod spec like this:

```
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        fpga-scheduling.io/enabled: "true"
    spec:
      containers:
      - name: nginx
        image: nginx:1.17.10
        ports:
        - containerPort: 80
```

Then create the workload:

```
kubectl apply -f workload.yaml
```
