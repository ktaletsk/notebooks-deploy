# Argo Workflow

Argo Workflow is a cloud-native job scheduler built specifically for Kubernetes. 

## Usage

* Make sure you have a Kubernetes cluster deployed and the `kubectl` CLI locally installed and configured. 

### Workflow

Run `kubectl apply -f manifest.yaml` to deploy the Argo Workflow.

* This will deploy 3 custom resource definitions (CRDs): Workflow, Cron Workflow, and Workflow Template
* This will deploy the `workflow-manager` in the `argo` namespace with cluster level permissions to manage the above CRDs. 

### Server

The Argo Server provides an API interface to interact with Argo CRDs, as well as a client-facing UI interface to track, log, and submit Workflows. 

Before deploying the Argo Server, create the secret `argo-postgres-config` with keys `username` and `password` in the `argo` namespace. Run `kubectl apply -f server-manifest.yaml` to deploy the Argo Server. 

* This will deploy a PostgreSQL instance for persistence logging of Workflows.
* By default all Workflows will be logged in PostgreSQL. This can be changed in the `workflow-controller-configmap` by setting `persistence.archive` to `false`.