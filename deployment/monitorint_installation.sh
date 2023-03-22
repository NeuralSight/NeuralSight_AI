# first install kubectl, docker.
# After that install helm then add the foolowing repos for monitoring


# add prometheus  community repo to helm.
# We used this becuase it comes with all the grafana, prometheus and k8s scraping tools for prometheus
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# update the repo
helm repo update
# update the values of default prometheus
helm inspect values prometheus-community/kube-prometheus-stack > /tmp/kube-prometheus-stack.values


# create and deploy the services for monitoring
helm install prometheus-community/kube-prometheus-stack \
--create-namespace --namespace prometheus \
--generate-name \
--values /tmp/kube-prometheus-stack.values \
--set prometheus.service.type=LoadBalancer \
--set prometheus.prometheusSpec.serviceMonitorSelectorNilUsesHelmValues=false \
--set grafana.service.type=LoadBalancer
