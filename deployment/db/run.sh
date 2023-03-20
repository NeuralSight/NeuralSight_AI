echo "Running Deployment Files for DB Service"
kubectl apply -f db/ns.yaml
kubectl apply -f db/secret.yaml
kubectl apply -f db/configmap.yaml
kubectl apply -f db/pv.yaml
kubectl apply -f db/dep.yaml
# kubectl apply -f db/job.yaml
kubectl apply -f db/svc.yaml
