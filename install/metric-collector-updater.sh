#!/bin/bash
# LOG file updater.log
# wget --no-cookies --no-cache https://raw.githubusercontent.com/snsergio/agent/main/install/metric-collector-updater.sh
# chmod +x metric-collector-updater.sh
# sudo ./metric-collector-updater.sh
##### Metric Collector Updater v1.00
set -eo pipefail
if [ "$EUID" -ne 0 ]
    then echo "Please run as root"
    exit
fi
wget --no-cookies --no-cache https://raw.githubusercontent.com/snsergio/agent/main/install/metric-collector-updater.py
if [ -f ./metric-collector-updater.py ]; then
    python3 metric-collector-updater.py
    rm metric-collector-updater.py
fi
