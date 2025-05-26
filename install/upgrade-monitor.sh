#!/bin/bash
# LOG file at /opt/eyeflow/install/monitor-install-<date time>.log
# wget --no-cookies --no-cache https://raw.githubusercontent.com/snsergio/agent/main/install/upgrade-monitor.sh
# chmod +x upgrade-monitor.sh
# sudo ./upgrade-monitor.sh
##### Install Monitor Upgrade v5.11
set -eo pipefail
VALIDDIR="home"
WORKDIR=$(pwd)
if [[ "$WORKDIR" != *"$VALIDDIR"* ]]; then
  echo "Please start the script at user's home directory"
  exit
fi
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi
LOGFILE="/opt/eyeflow/monitor/install/upgrade-monitor.log"
if [ -d /opt/eyeflow/monitor ]; then
    mv /opt/eyeflow/monitor /opt/eyeflow/monitor-old
fi
if [ -f /opt/eyeflow/monitor-old/collector-config-v4.yaml ]; then
    VERSAO="v4"
elif [ -f /opt/eyeflow/monitor-old/collector-config-v5.yaml ]; then
    VERSAO="v5"
else
    VERSAO="none"
fi
if [ "$VERSAO" != "none" ]; then
    mkdir -p /opt/eyeflow/monitor/install
else
    echo "Previous version not found... Exiting"
    exit
fi
touch /opt/eyeflow/monitor/install/upgrade-monitor.log
echo "----- Starting Metric Collector Upgrade -----" | sudo tee -a $LOGFILE
date | sudo tee -a $LOGFILE
echo "Previous metric collector version '$VERSAO'" | sudo tee -a $LOGFILE
echo "----- Installing initial packages -----" | sudo tee -a $LOGFILE
apt install -y curl lm-sensors sysstat ntpstat netcat iproute2 python3-requests python3-pip unzip
echo "----- Installing GIT -----" | sudo tee -a $LOGFILE
apt install -y git acl
echo "----- Install PIP packages -----" | sudo tee -a $LOGFILE
/usr/bin/python3 -m pip install xmltodict==0.13.0 \
    prometheus_client==0.16.0 \
    requests==2.28.2 \
    PyYAML
if [ $(uname -i) == "aarch64" ]; then
    echo "----- Installing ARM jetson-stats -----" | sudo tee -a $LOGFILE
    python3 -m pip install -U jetson-stats
    arch="arm"
else
    erch="x86"
fi


echo "----- Cloning Edge repo and setting rights -----" | sudo tee -a $LOGFILE
cd /opt/eyeflow/monitor/install
rm -rf /opt/eyeflow/monitor/install/agent
git clone https://github.com/snsergio/agent.git
if id "eyeflow" >/dev/null 2>&1; then
    chown -R eyeflow:users /opt/eyeflow/monitor
else
    echo "----- User eyeflow not present -----" | sudo tee -a $LOGFILE
fi
echo "----- Setting folder attributes -----" | sudo tee -a $LOGFILE
setfacl -dm u::rwx,g::rwx,o::rx /opt/eyeflow/monitor
chmod g+rwxs /opt/eyeflow/monitor
chmod 775 /opt/eyeflow/monitor
echo "----- Deleting unnecessary files -----" | sudo tee -a $LOGFILE
if [ $(uname -i) != "aarch64" ]; then
  rm -rf /opt/eyeflow/monitor/install/agent/jetson
fi
rm -rf /opt/eyeflow/monitor/install/agent/install
rm -rf /opt/eyeflow/monitor/install/agent/README*
rm -rf /opt/eyeflow/monitor/install/agent/grafana-stack
echo "----- Adding files -----" | sudo tee -a $LOGFILE
rsync -zvrh /opt/eyeflow/monitor/install/agent/* /opt/eyeflow/monitor
mv /opt/eyeflow/monitor/metric-collector/* /opt/eyeflow/monitor
rm -rf /opt/eyeflow/monitor/metric-collector
rm -rf /opt/eyeflow/monitor/prometheus-proxy
rm -rf /opt/eyeflow/monitor/install/agent
rm -rf /opt/eyeflow/monitor/README*
chmod +x /opt/eyeflow/monitor/lib/pushprox-client


echo "----- Preparing Collector -----" | sudo tee -a $LOGFILE
cp /opt/eyeflow/monitor/metric-collector.service /etc/systemd/system
cp /opt/eyeflow/monitor/proxy-exporter.service /etc/systemd/system
systemctl enable metric-collector.service
systemctl enable proxy-exporter.service
systemctl daemon-reload
echo "----- Host FQDN: '$(hostname --fqdn)' -----" | sudo tee -a $LOGFILE
clear
echo "+-------------------------------------------------------------------------------------------+"
echo "! Edit and configure collector-config.yaml file                                             !"
echo "! - The previous configuration file is at /opt/eyeflow/monitor-old                          !"
echo "!   saved version is '$VERSAO'                                                              !"
echo "! - If the collector will run as EXPORTER, configure Prometheus to scrape this host at:     !"
echo "!   FQDN: '$(hostname --fqdn)'                                                              !"
echo "! - Edit proxy-exporter.service to reflect the correct export URL - (correct customer name) !"
echo "! - Then start metric collector and proxy exporter:                                         !"
echo "!   sudo systemctl start proxy-exporter.service                                             !"
echo "!   sudo systemctl start metric-collector.service                                           !"
echo "! - Check if both run with no errors:                                                       !"
echo "!   sudo systemctl status proxy-exporter.service                                            !"
echo "!   sudo systemctl status metric-collector.service                                          !"
echo "+-------------------------------------------------------------------------------------------+"
rm -rf upgrade-monitor.sh
echo "end of script"
