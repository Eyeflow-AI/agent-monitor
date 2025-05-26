#!/bin/bash
currentscript="$0"
function finish {
    echo "Securely shredding ${currentscript}"; shred -u ${currentscript};
}
clear
set -eo pipefail
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit
fi
if [ ! -f /opt/eyeflow/monitor/metric-collector-v5.py ]; then
    echo "There is no metric-collector-v5.py file in this folder, exiting..."
    exit
else
    rm -f /opt/eyeflow/monitor/metric-collector-v5.py
    wget -P /opt/eyeflow/monitor/ https://raw.githubusercontent.com/snsergio/agent/main/metric-collector/metric-collector-v5.py
fi
if [ ! -f /opt/eyeflow/monitor/lib/metricexporter.py ]; then
    echo "There is no metricexporter.py file in this folder, exiting..."
    exit
else
    rm -f /opt/eyeflow/monitor/lib/metricexporter.py
    wget -P /opt/eyeflow/monitor/lib/ https://raw.githubusercontent.com/snsergio/agent/main/metric-collector/lib/metricexporter.py
fi
systemctl restart metric-collector.service
systemctl status metric-collector.service --no-pager
echo "DONE!"
trap finish EXIT