# How install metrics collector on Edge Station
Metric collector is the agent to gather metric information from Ubuntu Station, monitored by Grafana stack.
The agent can be configured as an Exporter (preferred) or in some cases push to Prometheus TSDB through Pushgateway 
You need these requirements to accomplish the desired results:
  - Need to know how set collector-config parameters (check details at:)
    > https://github.com/Eyeflow-AI/station-monitoring/tree/main/install/metric-collector
  - Station's login credentials - user: eyeflow and its password
  - If not done yet, set the host's FQDN to include **group** and **customer**
    Example: hostname.subsidiary.company (edge-1.mainline.mycompany)

To install the monitoring agent, scrap station's data and send to Prometheus, follow these steps. If you want to UPGRADE an existing installation, check below.
- New installation:

- Log into the Ubuntu Station as superuser **eyeflow** make sure eyeflow user is configured as sudoer;
  > ssh eyeflow@<station's IP address>
- If DOCKER is used on the station, make sure eyeflow user is in Docker's group;
  > groups eyeflow
- For systems where (NVIDIA) GPU is available, make sure NVIDIA package and nvidia-smi are installed and run with no errors;
  > nvidia-smi
- Download the installation script at home folder;
  > wget --no-cookies --no-cache https://raw.githubusercontent.com/snsergio/agent/main/install/install-monitor.sh
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

To upgrade Metric Collector:
- Log into the Ubuntu Station as superuser **eyeflow** make sure eyeflow user is configured as sudoer;
  > ssh eyeflow@<station's IP address>
- Download the installation script at home folder;
  > wget --no-cookies --no-cache https://raw.githubusercontent.com/snsergio/agent/main/install/upgrade-monitor.sh
- Make sure the script has execution rights:
  > chmod +x upgrade-monitor.sh
- Run the script as SUDO:
  > sudo ./upgrade-monitor.sh
- Enter the eyeflow user's password to authorize elevation;
- Check screen messages, if any action is required, just keep all default and hit 'OK' usually navigate with 'TAB' and select with 'ENTER'
- Wait for the end of execution message with instructions
- Go to Eyeflow's monitor folder:
  > cd /opt/eyeflow/monitor
- Edit Metric Collector's configuration file and fill data as appropriate. This is an YAML file and must follow the required syntax
  > sudo nano collector-config-v5.yaml
- Update the collector-config-v5.yaml file with contents of the previous configuration file, some new variables are added:
  > customerName: <Use this field to specify customer's name>
  > stationName: <Use this field to specify a group of servers - Specific server name will be set at hostname>
  > metricMethod: <Use the default 'exporter' option, in this case no pushURL information is required>
- When using EXPORTER method, proxy service may be required, pleasse check details ahead
- After edit the configuration file, proceed with the following steps if required:
- Stop collector service if it's running:
  > sudo systemctl stop metric-collector.service
- Make sure you have the correct service file installed:
  > sudo cp metric-collector.service /etc/systemd/system
- Enable metric collector service if you have not did so:
  > sudo systemctl enable metric-collector.service
  > sudo systemctl daemon-reload
- Start metric collector service and check its status:
  > sudo systemctl start metric-collector.service
  > sudo systemctl status metric-collector.service
- Configure host's FQDN to reflect customer's information or to differentiate from other stations
  > Example: host: edge-1 => should be set to FQDN: edge-1.company.com *or* edge-1.company.line1
- To change FQDN - replace "edge-1.company.line1" as appropriate:
  > sudo hostnamectl set-hostname edge-1.company.line1
- Edit /etc/hosts to reflect host's FQDN and short name:
  > sudo nano /etc/hosts
  > Check if host name is set to the format below:
  > ....
  > 192.168.100.101    edge-1.company.line1    edge-1
  > ....
- If you select 'exporter' method, the status should not show any "Push" errors, in case of this errors, stop and restart the service
- Edit the proxy-exporter.service file and replace the PROXY URL to reflect the correct URL for the customer:
  > Line 11 should have something like this:
  
  > ExecStart=/opt/eyeflow/monitor/lib/pushprox-client --proxy-url=https://proxy.CUSTOMER.eyeflow.ai/
  
  > ----------------------------------------------- replace CUSTOMER as appropriate ^
- Stop proxy service if it's running:
  > sudo systemctl stop proxy-exporter.service
- Make sure you have the correct service file installed:
  > sudo cp proxy-exporter.service /etc/systemd/system
- Enable proxy exporter service if you have not did so:
  > sudo systemctl enable proxy-exporter.service
  > sudo systemctl daemon-reload
- Start proxy exporter service and check its status:
  > sudo systemctl start proxy-exporter.service
  > sudo systemctl status proxy-exporter.service
- Update prometheus with host's FQDN. Ask for support if required
