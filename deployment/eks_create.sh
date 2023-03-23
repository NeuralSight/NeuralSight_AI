# THis CODE IS RUN ON THE MACHINE DOING THE INSTALLATION.
# YOU MUST HAVE ALREADY INSTALLED KUBECTL AND DOCKER.


# create cluster and configure it (by default it has 2 nodes)
eksctl create cluster --name Nlabs --region us-west-2
# eksctl create cluster --name Nlabs  --region us-west-2 --nodegroup-name MyNlabs --node-type t2.large --nodes 1 --nodes-min 1 --nodes-max 1

# update config with the name of the eks cluster we created above
aws eks update-kubeconfig --region us-west-2 --name Nlabs

# cluster identity detail
oidc_id=$(aws eks describe-cluster --name Nlabs --query "cluster.identity.oidc.issuer" --output text | cut -d '/' -f 5)
aws iam list-open-id-connect-providers | grep $oidc_id

# set associate iam
eksctl utils associate-iam-oidc-provider --cluster Nlabs --approve

# policy templater
curl -o iam_policy.json https://raw.githubusercontent.com/kubernetes-sigs/aws-load-balancer-controller/v2.4.4/docs/install/iam_policy.json

# update the policy template
aws iam create-policy \
    --policy-name AWSLoadBalancerControllerIAMPolicy \
    --policy-document file://iam_policy.json

# create iam role for the cluster
eksctl create iamserviceaccount \
  --cluster=Nlabs \
  --namespace=kube-system \
  --name=aws-load-balancer-controller \
  --role-name "AmazonEKSLoadBalancerControllerRole" \
  --attach-policy-arn=arn:aws:iam::xxxxxxxx:policy/AWSLoadBalancerControllerIAMPolicy \
  --approve

# helm for load balancer
sudo yum install openssl -y
curl https://raw.githubusercontent.com/helm/helm/master/scripts/get-helm-3 > get_helm.sh
chmod 700 get_helm.sh
./get_helm.sh


# add eks chart
helm repo add eks https://aws.github.io/eks-charts
helm repo update

# install lb
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=Nlabs \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller


# create  deployments and ns
kubectl get deployment -n kube-system aws-load-balancer-controller


# run your deployment files next
