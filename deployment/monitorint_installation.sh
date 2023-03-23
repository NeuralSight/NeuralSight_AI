# first install kubectl, docker.


# # Install Docker
# apt-get update && apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
# curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
# add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
# apt-get update && apt-get install -y docker-ce docker-ce-cli containerd.io
#
# # Install Kubernetes
# curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key add -
# echo "deb https://apt.kubernetes.io/ kubernetes-xenial main" | tee /etc/apt/sources.list.d/kubernetes.list
# apt-get update && apt-get install -y kubelet kubeadm kubectl


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
