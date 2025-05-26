# How install metrics collector on Edge Station
Metric collector is the agent to gather metric information from Ubuntu Station, push to Prometheus TSDB and monitored by Grafana stack.
You need these requirements to accomplish the desired results:
  - Need to know how set collector-config parameters (check details at:)
    > https://github.com/Eyeflow-AI/station-monitoring/tree/main/metric-collector
  - Station's eyeflow user password

To install the monitoring agent, scrap station's data and send to Prometheus, follow these steps:
- Log into the Ubuntu Station as superuser **eyeflow** make sure eyeflow user is configured as sudoer;
  > ssh eyeflow@<station's IP address>
- If DOCKER is used on the station, make sure eyeflow user is in Docker's group;
  > groups eyeflow
- For systems where (NVIDIA) GPU is available, make sure NVIDIA package and nvidia-smi are installed and run with no errors;
  > nvidia-smi
- Download the installation script at home folder;
  > wget https://raw.githubusercontent.com/snsergio/agent/main/install/install-monitor.sh
- Make sure the script has execution rights:
  > chmod +x install-monitor.sh
- Run the script as SUDO:
  > sudo ./install-monitor.sh
- Enter the eyeflow user's password to authorize elevation;
- Check screen messages, if any action is required, just keep all default and hit 'OK' usually navigate with 'TAB' and select with 'ENTER'
- Wait for the following message to edit collector-config:
  > Editing monitoring agent configuration file
  > 
  > Edit Monitoring Agent configuration file to reflect Edge Station requirements
  >
  > Press 'ENTER' to edit or 'CTRL-C' to cancel Monitoring Agent instalation 
  >  
- Save changes to the file:
  > 'ctrl-x', 'ENTER', 'y'
- Wait for the following message:
  >  
  > end of Metric Collector installation script
  > 
  > 'DATE' 'TIME'
  >  
  >  LOG file at: /opt/eyeflow/install/monitor-install-'date time'.log 
  >  
- Then check metric collector service status. Service should be running with no errors or warnings
  > sudo systemctl status metric-collector.service
- You may check metric collector's log file
  > cat /opt/eyeflow/monitor/monitoring-v5.log
