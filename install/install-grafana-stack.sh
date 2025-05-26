#!/bin/bash
# LOG file at /opt/eyeflow/install/monitor-install-<date time>.log
set -eo pipefail
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi
apt install wget curl -y
mkdir -p /opt/eyeflow/install
LOGFILE="/opt/eyeflow/install/grafana-install.log"
touch /opt/eyeflow/install/grafana-install.log
echo "##### Installing Eyeflow Dashboard Stack on EDGE server #####" | sudo tee -a $LOGFILE
date | sudo tee -a $LOGFILE
if [ "$EUID" -ne 0 ]
    then echo "Please run as root" | sudo tee -a $LOGFILE
    exit
fi
lsb_release -si | sudo tee -a $LOGFILE
lsb_release -sr | sudo tee -a $LOGFILE
if [[ ! $PWD = /opt/eyeflow/install ]]; then
    cp ./install-grafana-stack.sh /opt/eyeflow/install/install-grafana-stack.sh
fi
echo "##### running installation script.." | sudo tee -a $LOGFILE
if [ -x "$(command -v docker)" ]; then
    echo "##### Docker present #####" | sudo tee -a $LOGFILE
else
    if [ $(uname -i) == "aarch64" ]; then
        if [ -f /sys/firmware/devicetree/base/model ]; then
            isRaspi=$(cat /sys/firmware/devicetree/base/model | grep -c "Raspberry")
            if [ $isRaspi != 0 ]; then
                apt install linux-modules-extra-raspi -y
                echo "##### Raspberry Pi - Installing dependencies" | sudo tee -a $LOGFILE
            fi
        fi
        curl -fsSL https://get.docker.com -o get-docker.sh
        bash get-docker.sh
        docker network create --subnet 172.18.0.0/16 --gateway 172.18.0.1 -o com.docker.network.bridge.enable_icc=false -o com.docker.network.bridge.name=docker_gwbridge docker_gwbridge
    else
        echo "##### Install docker required libraries #####" | sudo tee -a $LOGFILE
        apt install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            software-properties-common \
            gnupg
        echo "#####      Install docker keyring       #####" | sudo tee -a $LOGFILE
        install -m 0755 -d /etc/apt/keyrings
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
        chmod a+r /etc/apt/keyrings/docker.gpg
        echo "deb [arch="$(dpkg --print-architecture)" signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu "$(. /etc/os-release && echo "$VERSION_CODENAME")" stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        echo "#####         Install docker            #####" | sudo tee -a $LOGFILE
        apt-get update
        apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    fi
fi
usermod -aG docker eyeflow
echo "##### Installing GIT:" | sudo tee -a $LOGFILE
apt install -y git acl
echo "##### Creating required folders" | sudo tee -a $LOGFILE
mkdir -p /opt/eyeflow/monitor/stack
echo "##### Cloning Edge repo and setting rights" | sudo tee -a $LOGFILE
cd /opt/eyeflow/install
rm -rf /opt/eyeflow/install/agent
git clone https://github.com/snsergio/agent.git
chown -R eyeflow:users /opt/eyeflow/monitor
setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow/monitor
chmod g+rwxs /opt/eyeflow/monitor
chmod 775 /opt/eyeflow/monitor
rm -rf /opt/eyeflow/install/agent/lib
rm -rf /opt/eyeflow/install/agent/promtail
rm -rf /opt/eyeflow/install/agent/lib
rm -rf /opt/eyeflow/install/agent/README*
rm -rf /opt/eyeflow/install/agent/collector*
rm -rf /opt/eyeflow/install/agent/metric*
rm -rf /opt/eyeflow/install/agent/install*
rsync -zvrh /opt/eyeflow/install/agent/* /opt/eyeflow/monitor
cd /opt/eyeflow/monitor/stack
if [ -x "$(docker info --format '{{.Swarm.ControlAvailable}}')" ]; then
    echo "##### Swarm initialized #####" | sudo tee -a $LOGFILE
else
    selfIp=$(hostname  -I | cut -f1 -d' ')
    echo "##### Initializing Swarm #####" | sudo tee -a $LOGFILE
    docker swarm init --advertise-addr $selfIp --listen-addr $selfIp:2377
fi
docker stack deploy -c docker-stack.yml prom
echo "########################################################" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "#####   end of Grafana Stack installation script   #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "#####   To access Grafana dashboard, navigate to:  #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "#####   http://localhost:3000                      #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "#####   User: admin, Password: slai.slai           #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "#####                                              #####" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "##### Finished at: $(date)" | sudo tee -a /opt/eyeflow/install/edge-install.log
echo "##### REBBOOTING for changes to take effect        #####"
sleep 5
rm -f /opt/eyeflow/install/install-grafana-stack.sh
rm -rf /opt/eyeflow/install/stack
rm -f /home/eyeflow/install-grafana-stack.sh
reboot