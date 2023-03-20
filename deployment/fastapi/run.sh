echo "Running Deployment Files for Backend Service"
kubectl apply -f fastapi/ns.yaml
kubectl apply -f fastapi/dep.yaml
kubectl apply -f fastapi/svc.yaml
