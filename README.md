# Kubernetes Memory-Based Horizontal Pod Autoscaling

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Nginx](https://img.shields.io/badge/Nginx-009639?style=for-the-badge&logo=nginx&logoColor=white)

A hands-on Kubernetes project demonstrating **memory-based Horizontal Pod Autoscaling (HPA)** using a custom Python application.

The project demonstrates how Kubernetes automatically adjusts the number of application pods based on memory utilization, helping maintain application availability under changing resource demands.

## Project Overview

This project explores Kubernetes resource management and automatic scaling through two workloads:

- **Python Memory Workload:** A custom HTTP application that allocates memory on demand to simulate memory-intensive workloads.
- **Nginx Workload:** An additional deployment demonstrating standard Kubernetes application deployment and resource configuration.

The primary experiment focuses on the Python application and its memory-based HPA configuration.

## Architecture

```text
                 Kubernetes Cluster
                    (Minikube)
                         |
                  Namespace: hpa-lab
                         |
              +----------+----------+
              |                     |
       Python Memory Workload     Nginx
              |                     |
         Deployment             Deployment
              |                     |
          Service                Service
              |
       Memory-based HPA
              |
       Metrics Server
              |
       Memory Utilization
              |
       Automatic Pod Scaling
```

The Metrics Server collects resource utilization metrics from Kubernetes Pods and provides them to the Horizontal Pod Autoscaler (HPA).

The HPA uses memory utilization metrics to determine whether the Python Memory Workload needs additional replicas or can scale down. The Service provides network access to the application Pods.

## Technologies Used

- Kubernetes
- Minikube
- kubectl
- Docker
- Python 3.12
- Nginx
- Metrics Server
- Horizontal Pod Autoscaler (HPA)

## Repository Structure

```text
k8s-hpa-memory-autoscaling/
├── app/
│   ├── Dockerfile
│   └── server.py
│
├── kubernetes/
│   ├── namespace.yaml
│   ├── deployment.yaml
│   ├── service.yaml
│   ├── hpa.yaml
│   ├── memory-deployment.yaml
│   ├── memory-service.yaml
│   └── memory-hpa.yaml
│
├── screenshots/
│   └── autoscaling/
│       ├── 01-Memory Usage.png
│       ├── 02-HPA Status.png
│       ├── 03-Pod Scaling.png
│       └── 04-Scaling Event.png
│
└── README.md
```

## Kubernetes Configuration

The Python memory workload is configured with the following resource settings:

| Configuration | Value |
|---|---:|
| Initial replicas | 2 |
| Minimum replicas | 2 |
| Maximum replicas | 5 |
| Memory request | 100Mi |
| Memory limit | 200Mi |
| CPU request | 100m |
| CPU limit | 200m |
| HPA memory target | 75% |

The HPA uses the `autoscaling/v2` API.

### Scaling Behavior

**Scale-up**
- Stabilization window: 0 seconds
- Maximum additional pods: 2 per 30 seconds
- Maximum scaling percentage: 100% per 30 seconds

**Scale-down**
- Stabilization window: 300 seconds
- Maximum reduction: 1 pod per 30 seconds

These settings allow the workload to scale up quickly while avoiding unnecessarily rapid scale-down operations.

## Memory Workload Application

The custom Python application provides three main endpoints:

| Endpoint | Description |
|---|---|
| `/health` | Health check endpoint |
| `/allocate?mb=10` | Allocates 10 MB of memory |
| `/reset` | Releases allocated memory |

The application includes:
- Thread-safe memory allocation.
- A maximum allocation limit of 100 MB per process.
- Input validation for allocation requests.
- Kubernetes readiness and liveness probes.

## Deployment Instructions

### 1. Clone the repository

```bash
git clone https://github.com/Kevin-2603/k8s-hpa-memory-autoscaling.git

cd k8s-hpa-memory-autoscaling
```

### 2. Start Minikube

```bash
minikube start
```

### 3. Enable Metrics Server

```bash
minikube addons enable metrics-server
```

Verify that metrics are available:

```bash
kubectl top nodes
```

### 4. Build the Python application image

```bash
minikube image build -t memory-workload:v2 ./app
```

The image is built directly into Minikube's image environment.

### 5. Create the namespace

```bash
kubectl apply -f kubernetes/namespace.yaml
```

### 6. Deploy Kubernetes resources

```bash
kubectl apply -f kubernetes/
```

### 7. Verify deployments and HPA

```bash
kubectl get deployments -n hpa-lab

kubectl get services -n hpa-lab

kubectl get hpa -n hpa-lab
```

Check pod resource utilization:

```bash
kubectl top pods -n hpa-lab
```

## Testing Memory Autoscaling

The memory workload can be tested by sending requests to an individual pod.

First, identify the memory workload pods:

```bash
kubectl get pods -n hpa-lab
```

Forward a local port to one of the pods:

```bash
kubectl port-forward pod/<pod-name> 8081:8080 -n hpa-lab
```

In another terminal, allocate memory:

```bash
curl "http://localhost:8081/allocate?mb=10"
```

Repeat the request to increase memory consumption on that pod.

Monitor memory utilization:

```bash
kubectl top pods -n hpa-lab
```

Monitor HPA behavior:

```bash
kubectl get hpa -n hpa-lab -w
```

Inspect scaling events:

```bash
kubectl describe hpa memory-workload-hpa -n hpa-lab
```

## Experimental Results

The memory-based HPA experiment successfully demonstrated automatic pod scaling.

| Metric | Observed Result |
|---|---|
| Initial replicas | 2 |
| Replicas after scaling | 3 |
| Memory utilization | 80% |
| HPA target | 75% |
| Scaling event | SuccessfulRescale |

The HPA detected memory utilization above the configured target and increased the number of replicas from 2 to 3.

This demonstrates how Kubernetes HPA can respond to memory pressure using resource utilization metrics.

## Screenshots

### 1. Memory Usage

![Memory Usage](screenshots/autoscaling/01-Memory%20Usage.png)

### 2. HPA Status

![HPA Status](screenshots/autoscaling/02-HPA%20Status.png)

### 3. Pod Scaling

![Pod Scaling](screenshots/autoscaling/03-Pod%20Scaling.png)

### 4. Scaling Event

![Scaling Event](screenshots/autoscaling/04-Scaling%20Event.png)

## Cleanup

To remove all project resources from the Kubernetes cluster:

```bash
kubectl delete namespace hpa-lab
```

To stop Minikube and release local resources:

```bash
minikube stop
```

## Key Learnings

Through this project, I gained practical experience with:

- Deploying containerized applications to Kubernetes.
- Configuring CPU and memory requests and limits.
- Implementing memory-based Horizontal Pod Autoscaling.
- Understanding how Metrics Server provides resource metrics.
- Monitoring pod utilization with `kubectl top`.
- Observing automatic scaling events.
- Building and managing custom container images with Minikube.

---

**Project Focus:** Kubernetes Resource Management & Memory-Based Autoscaling  
**Environment:** Local Kubernetes Cluster using Minikube
