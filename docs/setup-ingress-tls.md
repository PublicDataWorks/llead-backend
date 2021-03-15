# Setup Gke Ingress with letsencrypt SSL

## Setup SSL certificate
- Install cert manager
    - `kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.16.1/cert-manager.crds.yaml`
- Create ClusterIssuer
```yaml
apiVersion: cert-manager.io/v1alpha2
kind: ClusterIssuer
metadata:
  name: [letsencrypt-name]
  labels:
    name: letsencrypt
spec:
  acme:
    email: EMAIL_ADDRESS
    privateKeySecretRef:
      name: letsencrypt
    server: https://acme-v02.api.letsencrypt.org/directory
    solvers:
    - http01:
        ingress:
          class: gce
```
- Apply change
    - `kubectl apply -f [ClusterIssuer-file-name].yaml`

## Setup Ingress
- Create static ip address
  - `gcloud compute addresses create [static-ip-address-name] --global`
- Set metadata for Ingress
```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: INGRESS_NAME
  annotations:
    kubernetes.io/ingress.class: gce
    kubernetes.io/ingress.global-static-ip-name: [static-ip-address-name]
    kubernetes.io/tls-acme: "true"
    cert-manager.io/cluster-issuer: [letsencrypt-name]
spec:
```
- Apply Ingress
    - `kubectl apply -f [Ingress-file-name].yml`
- Check to see if Certificates work
    - Run `kubectl get certificaterequests` to see all CertificateRequests
    - If `status.Conditions.Reason` is not `Issued`
        - Run `kubectl get challenges` to check for fail reasons