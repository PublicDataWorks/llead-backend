#!/usr/bin/env bash
kubectl delete -f kubernetes/logging/fluentbit-daemonset.yaml
kubectl apply -f kubernetes/logging/fluentbit-configmap.yaml
kubectl apply -f kubernetes/logging/fluentbit-daemonset.yaml