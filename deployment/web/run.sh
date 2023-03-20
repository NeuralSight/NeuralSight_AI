echo "Running Website Deployment"

kubectl apply -f ./web/dep.yaml
kubectl apply -f ./web/svc.yaml
