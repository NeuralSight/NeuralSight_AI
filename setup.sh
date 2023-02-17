
sudo apt-get update
sudo apt-get install -y apt-transport-https gnupg2
curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
echo 'deb https://apt.kubernetes.io/ kubernetes-xenial main' | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubectl kubeadm kubelet kubernetes-cni docker.io
sudo systemctl start docker
sudo systemctl enable docker
# docker to work without sudo
sudo usermod -aG docker $USER
newgrp docker

# update ip table to see bridged network
cat << EOF | sudo tee /etc/sysctl.d/k8s.conf
net.bridge.bridge-nf-call-ip6tables = 1
net.bridge.bridge-nf-call-iptables = 1
EOF
sudo sysctl — system


# FOR MASTER ONLY/...
# pull kubs image
sudo kubeadm config images pull

rm /etc/containerd/config.toml
sudo systemctl restart containerd
sudo kubeadm init --apiserver-advertise-address=172.31.29.37 --pod-network-cidr=10.244.0.0/16 # Use your master node’s private IP



sudo kubeadm join 172.31.29.37:6443 --token azbxsh.b2fuvh4fi3k74ogm \
	--discovery-token-ca-cert-hash sha256:853cf507cde912027d4fb1c38ab077b2fc204e9013133f85f58c704fff023885 
























# docker installation

sudo apt update
sudo apt install apt-transport-https ca-certificates curl software-properties-common -y
apt-get install -y containerd.io
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu focal stable"
apt-cache policy docker-ce
sudo apt install docker-ce -y
sudo systemctl status docker




# kubernets installation
sudo curl -fsSLo /etc/apt/keyrings/kubernetes-archive-keyring.gpg https://packages.cloud.google.com/apt/doc/apt-key.gpg
echo "deb [signed-by=/etc/apt/keyrings/kubernetes-archive-keyring.gpg] https://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee /etc/apt/sources.list.d/kubernetes.list
sudo apt-get update
sudo apt-get install -y kubelet kubeadm kubectl
sudo apt-mark hold kubelet kubeadm kubectl


# On each server, enable the use of iptables
echo "net.bridge.bridge-nf-call-iptables=1" | sudo tee -a /etc/sysctl.conf
sudo sysctl -p


# on master
rm /etc/containerd/config.toml
systemctl restart containerd
sudo kubeadm init --pod-network-cidr=10.244.0.0/16
# kubeadm init




# join the other workds run first as root..
rm /etc/containerd/config.toml
systemctl restart containerd
sudo kubeadm join 172.31.12.107:6443 --token 7as31g.h48xtlnibhsov98i \
	--discovery-token-ca-cert-hash sha256:e7401f04403f99fae02a783e8394ecaaa5069ba0421e6fb8c91cc713d89cbf2c

# sudo kubeadm init --apiserver-advertise-address=172.31.12.107 --pod-network-cidr=10.244.0.0/16 # Use your master node’s private IP



# resolve configs
mkdir -p $HOME/.kube
sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
sudo chown $(id -u):$(id -g) $HOME/.kube/config


#mkdir -p $HOME/.kube
#sudo cp -i /etc/kubernetes/admin.conf $HOME/.kube/config
#sudo chown $(id -u):$(id -g) $HOME/.kube/config
#export KUBECONFIG=/etc/kubernetes/admin.conf
#
# -------- root cause:
#export KUBECONFIG=/etc/kubernetes/admin.conf
# the owner of /etc/kubernetes/admin.conf is root.
#
# ------- workaround:
#export KUBECONFIG=$HOME/.kube/config
# or
export KUBECONFIG=/etc/kubernetes/admin.conf
