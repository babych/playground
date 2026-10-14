# BasicKube

[![Tests](https://github.com/Babych/BasicKube/actions/workflows/tests.yml/badge.svg?branch=main)](https://github.com/Babych/BasicKube/actions/workflows/tests.yml)
[![CI/CD](https://github.com/Babych/BasicKube/actions/workflows/cicd.yml/badge.svg?branch=main&event=workflow_dispatch)](https://github.com/Babych/BasicKube/actions/workflows/cicd.yml) 


# Basickube Deployment on AKS with TLS (nip.io)

This project demonstrates a simple Kubernetes deployment on AKS, exposed via an Ingress using **nip.io**, with automatic TLS certificates issued by **cert-manager** and Let's Encrypt (staging or production).

---

## Features

- Kubernetes Deployment
- Ingress with nip.io domain
- TLS via cert-manager
- Optional self-signed certificates for local development
- GitHub Actions compatible for CI/CD deployment

---

## Prerequisites

- Azure Kubernetes Service (AKS) cluster
- `kubectl` configured for the cluster
- NGINX Ingress Controller installed
- cert-manager installed in the cluster

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/latest/download/cert-manager.yaml
GitHub Actions runner (optional for CI/CD)
```

Deployment Steps
1. ClusterIssuer (Let's Encrypt staging)
Create a ClusterIssuer for staging certificates:

Copy code: [https://github.com/Babych/BasicKube/blob/main/deploy/ingress%20configs/cluster-issuer.yaml](https://github.com/Babych/BasicKube/blob/main/deploy/ingress%20configs/cluster-issuer.yaml)

```bash
kubectl apply -f cluster-issuer.yaml
```

2. Deployment & Service
Create your Deployment and Service for basickube:

[https://github.com/Babych/BasicKube/blob/main/deploy/deployment.yaml](https://github.com/Babych/BasicKube/blob/main/deploy/deployment.yaml)
[https://github.com/Babych/BasicKube/blob/main/deploy/service.yaml](https://github.com/Babych/BasicKube/blob/main/deploy/service.yaml)
[https://github.com/Babych/BasicKube/blob/main/deploy/ingress.yaml](https://github.com/Babych/BasicKube/blob/main/deploy/ingress.yaml)

Apply them in CI/CD: [https://github.com/Babych/BasicKube/blob/main/.github/workflows/cicd.yml](https://github.com/Babych/BasicKube/blob/main/.github/workflows/cicd.yml)

Check certificate status:

Copy code
```bash
kubectl describe certificate basickube-tls -n basickube-ns
kubectl get secret basickube-tls -n basickube-ns
```

3. Access the Application
HTTPS: [https://basickube.172.199.209.31.nip.io/weatherforecast/temperature?lat=50.44&lon=30.52](https://basickube.172.199.209.31.nip.io/weatherforecast/temperature?lat=50.44&lon=30.52)

Swagger: [https://basickube.172.199.209.31.nip.io/swagger/index.html](https://basickube.172.199.209.31.nip.io/swagger/index.html)

Chrome may show "Not Secure" if using url with IP adress. Edge may display it as secure.
