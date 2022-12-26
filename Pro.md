<!-- NODE EXPORTER -->


<!-- install node export -->
wget https://github.com/prometheus/node_exporter/releases/download/v1.5.0/node_exporter-1.5.0.linux-amd64.tar.gz
<!-- extract -->

tar xvfz node_exporter-1.5.0.linux-amd64.tar.gz

<!-- move to extracted folder -->
sudo mv node_exporter-1.1.2.linux-amd64 node_exporter

<!-- change dire -->
cd node_exporter
<!-- run make -->
./node_exporter





<!-- PROMITHIUS  -->
wget https://github.com/prometheus/prometheus/releases/download/v2.40.7/prometheus-2.40.7.linux-amd64.tar.gz

<!-- extract -->
sudo tar xvfz prometheus-2.40.7.linux-amd64.tar.gz

<!-- rename -->
sudo mv prometheus-2.40.7.linux-amd64 /opt/prometheus

<!-- move to opt -->
cd /opt/prometheus/

<!-- edit some item in yaml file -->
sudo vi prometheus.yml

<!-- run -->
sudo ./prometheus --config.file=./prometheus.yml



















<!-- grafana -->
sudo apt-get install -y apt-transport-https
sudo apt-get install -y software-properties-common wget
wget -q -O - https://packages.grafana.com/gpg.key | sudo apt-key add -
sudo add-apt-repository "deb https://packages.grafana.com/oss/deb stable main"
sudo apt-get update
sudo apt-get install grafana
sudo systemctl daemon-reload



<!-- start grafana service -->
sudo systemctl start grafana-server

<!-- booting at start time -->
sudo systemctl enable grafana-server.service


<!-- configuration of nbginx -->
server{
        server_name 3.83.165.209;
        location / {
                proxy_pass http://localhost:3000;
        }
}
