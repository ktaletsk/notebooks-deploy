#!/usr/bin/env bash

export $(egrep -v '^#' .env)

# Backup file extension required to support Mac versions of sed
sed -i.bak \
    -e "s/SHARED_STORAGE_VALUE/${SHARED_STORAGE}/g" \
    -e "s/STORAGE_CLASS_VALUE/${STORAGE_CLASS}/g" \
    deploy/kubernetes/storage.yaml
rm deploy/kubernetes/storage.yaml.bak

sed -i.bak \
    -e "s/BASE_STACK_VALUE/${BASE_STACK}/g" \
    -e "s/STACKS_VALUE/${STACKS}/g" \
    -e "s/STACKS_NAMES_VALUE/${STACKS_NAMES}/g" \
    -e "s/STORAGE_CLASS_VALUE/${STORAGE_CLASS}/g" \
    -e "s/STORAGE_PER_USER_VALUE/${STORAGE_PER_USER}/g" \
    -e "s/WIPP_STORAGE_PVC_VALUE/${WIPP_STORAGE_PVC}/g" \
    -e "s|WIPP_UI_VALUE|${WIPP_UI}|g" \
    -e "s|WIPP_API_INTERNAL_VALUE|${WIPP_API_INTERNAL}|g" \
    -e "s|WIPP_NOTEBOOKS_PATH_VALUE|${WIPP_NOTEBOOKS_PATH}|g" \
    deploy/kubernetes/jupyterhub-config.py
rm deploy/kubernetes/jupyterhub-config.py.bak

CONFIG_HASH=$(shasum deploy/kubernetes/jupyterhub-configs.yaml | cut -d ' ' -f 1 | tr -d '\n')

sed -i.bak \
    -e "s/HUB_VERSION_VALUE/${HUB_VERSION}/g" \
    -e "s/CONFIG_HASH_VALUE/${CONFIG_HASH}/g" \
    deploy/kubernetes/jupyterhub-deployment.yaml
rm deploy/kubernetes/jupyterhub-deployment.yaml.bak

sed -i.bak \
    -e "s|JUPYTERHUB_URL_VALUE|${JUPYTERHUB_URL}|g" \
    -e "s|ARGO_URL_VALUE|${ARGO_URL}|g" \
    -e "s|ROOK_CEPH_URL_VALUE|${ROOK_CEPH_URL}|g" \
    deploy/kubernetes/jupyterhub-services.yaml
rm deploy/kubernetes/jupyterhub-services.yaml.bak

kubectl apply --kubeconfig=${KUBECONFIG} -f deploy/kubernetes/jupyterhub-predefined.yaml
kubectl apply --kubeconfig=${KUBECONFIG} -f deploy/kubernetes/storage.yaml
kubectl create configmap jupyterhub-config --from-file=deploy/kubernetes/jupyterhub-config.py -o yaml --dry-run | kubectl apply --kubeconfig=${KUBECONFIG} -f -
kubectl create configmap cull-idle-servers --from-file=deploy/kubernetes/cull-idle-servers.py -o yaml --dry-run | kubectl apply --kubeconfig=${KUBECONFIG} -f -
kubectl apply --kubeconfig=${KUBECONFIG} -f deploy/kubernetes/jupyterhub-services.yaml
kubectl apply --kubeconfig=${KUBECONFIG} -f deploy/kubernetes/jupyterhub-deployment.yaml