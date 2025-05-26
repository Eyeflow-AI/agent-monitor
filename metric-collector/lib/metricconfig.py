#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricconfig-v5.14-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricconfig"] = versao
#######################################################################################################################
class config_setup:
    # SETUP ---------------------------------------------------------------------------------------------------------------
    #######################################################################################################################
    # configFileName: Default configuration file name. Typically 'collector-config.yaml'
    #   Edit the configuration file accordingly to reflect metrics to collect at the station being executed
    #   Path to Configuration file is set by environment variable $CONFIGPATH or defaults to './'
    #######################################################################################################################
    configDict = {}
    # Get config file
    def get_config():
        import os
        import yaml
        from pathlib import Path
        configPath = os.environ.get('CONFIGPATH')
        metric_attributes.resposta["cpuArch"] = "invalid"
        metric_attributes.resposta["cpuVendor"] = "invalid"
        metric_attributes.resposta["cpuModelName"] = "invalid"
        metric_attributes.resposta["hostName"] = "myhost"
        metric_attributes.resposta["ntpServerList"] = []
        metric_attributes.resposta["ntpIp"] = "none"
        metric_attributes.resposta["ntpTimeDiscrepancy"] = 0
        metric_attributes.resposta["ntpPollingPeriod"] = 0
        metric_attributes.resposta["ntpStatus"] = 0
        configExecError = 0
        if configPath == None: 
            logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: Env var CONFIGPATH not set, changing to CWD")
            configPath = "./"
        if configPath[-1:] != "/": configPath += "/"
        if os.path.isfile(configPath + c.configFileName): config_setup.configDict = yaml.safe_load(Path(configPath + c.configFileName).read_text())
        else: 
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: {c.configFileName} not found at {configPath}")
            print(f"[ERROR] {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: {c.configFileName} not found at {configPath}")
            exit(1)
        try: 
            c.logPath = config_setup.configDict["agentPath"]["logPath"]
            c.scriptPath = config_setup.configDict["agentPath"]["scriptPath"]
        except: 
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: Setup path information not correctly set")
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: Setup file agentPath/logPath set to {c.logPath}")
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: Setup file agentPath/scriptPath set to {c.scriptPath}")
            c.logPath = configPath
        if c.logPath[-1:] != "/": c.logPath += "/"
        try: metric_attributes.resposta["hostName"] = os.uname()[1].split(".")[0]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: Hostname not defined, set to {metric_attributes.resposta['hostName']}")
        if metric_attributes.resposta["hostName"] == None or metric_attributes.resposta["hostName"] == "": metric_attributes.resposta["hostName"] = "notset"
        try: infoout = c.exec_cmd(["lscpu"], c.debugMode)["output"].splitlines()
        except: 
            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: CPU Arch error")
            configExecError = 1
            infoout = 0
        if infoout != 0:
            for item in range(len(infoout)):
                if "Architecture" in infoout[item]: metric_attributes.resposta["cpuArch"] = infoout[item].split(":")[1].strip()
                if "Vendor ID" in infoout[item]: metric_attributes.resposta["cpuVendor"] = infoout[item].split(":")[1].strip()
                if "Model name" in infoout[item]: metric_attributes.resposta["cpuModelName"] = infoout[item].split(":")[1].strip()
        try: bitout = c.exec_cmd(["getconf", "LONG_BIT"], c.debugMode)["output"]
        except: 
            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-config_setup.get_config: CPU Bit lenght error")
            configExecError = 1
            bitout = 0
        if bitout != 0: metric_attributes.resposta["cpuBit"] = int(bitout)
        else: metric_attributes.resposta["cpuBit"] = 0
        metric_attributes.resposta["configExecError"] = configExecError
        del os, yaml, Path
        return metric_attributes.validate(config_setup.configDict)
        #----------------------------------------------------------------------------------------------------------------------
class metric_attributes:
    resposta = {}
    # Get customer information from configuration file
    def get_station_id(configDict):
        metric_attributes.resposta["customerName"] = "nocustomername"
        metric_attributes.resposta["stationName"] = "nostationname"
        metric_attributes.resposta["stationIpList"] = []
        ipSelf = []
        if configDict["stationID"]["customerName"] != None:
            try: metric_attributes.resposta["customerName"] = configDict["stationID"]["customerName"]
            except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_station_id: stationID/customerName not set. Assuming 'nocustomername'")
        if configDict["stationID"]["stationName"] != None:
            try: metric_attributes.resposta["stationName"] = configDict["stationID"]["stationName"]
            except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_station_id: stationID/stationName not set. Assuming 'nostationname'")
        if configDict["stationID"]["StationIP"] != None:
            try: ipSelf = configDict["stationID"]["StationIP"]
            except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_station_id: stationID/stationIP not set")
        if isinstance(ipSelf, str): 
            if "," in ipSelf:
                metric_attributes.resposta["stationIpList"] = ipSelf.split(",")
            else: metric_attributes.resposta["stationIpList"].append(ipSelf)
        else: metric_attributes.resposta["stationIpList"] = ipSelf
        tmpList = []
        if metric_attributes.resposta["stationIpList"] != None:
            for sIp in range(len(metric_attributes.resposta["stationIpList"])):
                if not metric_attributes.validate_ip(metric_attributes.resposta["stationIpList"][sIp].strip()):
                    logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_station_id: stationID/stationIP not valid: {sIp}")
                else: tmpList.append(metric_attributes.resposta["stationIpList"][sIp].strip())
            metric_attributes.resposta["stationIpList"] = tmpList
        else: metric_attributes.resposta["stationIpList"] = ""
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Get RTDB information from configuration file
    def get_rtdb(configDict):
        metric_attributes.resposta["metricMethod"] = "push"
        metric_attributes.resposta["pushUrl"] = None
        metric_attributes.resposta["pushUrl2"] = None
        try: metric_attributes.resposta["metricMethod"] = configDict["metricMethod"].lower()
        except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_rtdb: metricMethod not set")
        try: metric_attributes.resposta["pushUrl"] = configDict["prometheusPush"]["pushUrl"]
        except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_rtdb: prometheusPush/pushUrl not set")
        try: metric_attributes.resposta["pushUrl2"] = configDict["prometheusPush"]["pushUrl2"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_rtdb: prometheusPush/pushUrl2 not set")
        if metric_attributes.resposta["metricMethod"] == None: metric_attributes.resposta["metricMethod"] = "push"
        if metric_attributes.resposta["pushUrl"] in [None, ""] and metric_attributes.resposta["pushUrl2"] in [None, ""]: metric_attributes.resposta["metricMethod"] = "exporter"
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Get TLS information from configuration file
    def get_tls(configDict):
        metric_attributes.resposta["tls1"] = False
        metric_attributes.resposta["tls2"] = False
        metric_attributes.resposta["user1"] = ""
        metric_attributes.resposta["user2"] = ""
        metric_attributes.resposta["pass1"] = ""
        metric_attributes.resposta["pass2"] = ""
        import base64
        try: metric_attributes.resposta["tls1"] = configDict["tls"]["pushUrl_TLS"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl_TLS not set")
        try: metric_attributes.resposta["tls2"] = configDict["tls"]["pushUrl2_TLS"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl2_TLS not set")
        if metric_attributes.resposta["tls1"]:
            try: metric_attributes.resposta["user1"] = configDict["tls"]["pushUrl_TLS_Username"]
            except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl_TLS_Username not set, Setting TLS1 to FALSE")
            try: metric_attributes.resposta["pass1"] = base64.b64decode(configDict["tls"]["pushUrl_TLS_Password"]).decode("utf-8")
            except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl_TLS_Password not set, Setting TLS1 to FALSE")
            if metric_attributes.resposta["user1"] == None or metric_attributes.resposta["user1"] == "":
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl_TLS_Username not set, disabling TLS")
                metric_attributes.resposta["tls1"], metric_attributes.resposta["user1"] = 0, ""
            if metric_attributes.resposta["pass1"] == None or metric_attributes.resposta["pass1"] == "":
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl_TLS_Password not set, disabling TLS")
                metric_attributes.resposta["tls1"], metric_attributes.resposta["pass1"] = 0, ""
        if metric_attributes.resposta["tls2"]:
            try: metric_attributes.resposta["user2"] = configDict["tls"]["pushUrl2_TLS_Username"]
            except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl2_TLS_Username not set, Setting TLS1 to FALSE")
            try: metric_attributes.resposta["pass2"] = base64.b64decode(configDict["tls"]["pushUrl2_TLS_Password"]).decode("utf-8")
            except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl2_TLS_Password not set, Setting TLS1 to FALSE")
            if metric_attributes.resposta["user2"] == None or metric_attributes.resposta["user2"] == "":
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl2_TLS_Username not set, disabling TLS")
                metric_attributes.resposta["tls2"], metric_attributes.resposta["user2"] = 0, ""
            if metric_attributes.resposta["pass2"] == None or metric_attributes.resposta["pass2"] == "":
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_tls: tls/pushUrl2_TLS_Password not set, disabling TLS")
                metric_attributes.resposta["tls2"], metric_attributes.resposta["pass2"] = 0, ""
        del base64
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Get mescelaneous information from configuration file
    def get_misc(configDict):
        metric_attributes.resposta["metricDetails"] = "light"
        metric_attributes.resposta["debugMode"] = False
        try: metric_attributes.resposta["metricDetails"] = configDict["metricDetails"].lower()
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_misc: metricDetails not set")
        try: metric_attributes.resposta["debugMode"] = bool(configDict["debugMode"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_misc: debugMode not set. Assuming false")
        if metric_attributes.resposta["metricDetails"] == "full": metric_attributes.resposta["metricDetails"] = True
        elif metric_attributes.resposta["metricDetails"] == "light": metric_attributes.resposta["metricDetails"] = False
        else:
            metric_attributes.resposta["metricDetails"] = False
            logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_misc: metricDetails invalid set. Assuming 'light'")
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Get restart information from configuration file
    def get_restart(configDict):
        import os
        metric_attributes.resposta["camRestart"] = False
        metric_attributes.resposta["sysAgentRestart"] = False
        metric_attributes.resposta["suAccess"] = False
        try: metric_attributes.resposta["camRestart"] = bool(configDict["restart"]["camRestart"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: restart/camRestart not set")
        try: metric_attributes.resposta["sysAgentRestart"] = bool(configDict["restart"]["sysAgentRestart"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: restart/sysAgentRestart not set")
        try: os.environ["SAMON"] = configDict["restart"]["suAccess"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: restart/suAccess not set")
        if (metric_attributes.resposta["camRestart"] == True) or (metric_attributes.resposta["sysAgentRestart"] == True) and (configDict["restart"]["suAccess"] in [None, ""]):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Setup: required restart/suAccess not set. Forcing restart to FALSE")
            metric_attributes.resposta["camRestart"] = False
            metric_attributes.resposta["sysAgentRestart"] = False
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Get update information from configuration file
    def get_update(configDict):
        metric_attributes.resposta["autoUpdate"] = False
        metric_attributes.resposta["autoRestart"] = False
        metric_attributes.resposta["updateUrl"] = ""
        metric_attributes.resposta["updateAccessToken"] = ""
        try: metric_attributes.resposta["autoUpdate"] = bool(configDict["update"]["autoUpdate"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: update/autoUpdate not set")
        try: metric_attributes.resposta["autoRestart"] = bool(configDict["update"]["autoRestart"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: update/autoRestart not set")
        try: metric_attributes.resposta["updateUrl"] = configDict["update"]["updateUrl"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}- metric_attributes.get_update: update/updateUrl not set")
        try: metric_attributes.resposta["updateAccessToken"] = configDict["update"]["updateAccessToken"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_update: update/updateAccessToken not set")
        if metric_attributes.resposta["autoUpdate"] or metric_attributes.resposta["autoRestart"]:
            if metric_attributes.resposta["updateUrl"] in [None, ""]:
                logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}- metric_attributes.get_update: updateUrl not set, disabling Auto Update")
                metric_attributes.resposta["autoUpdate"] = False
                metric_attributes.resposta["autoRestart"] = False
            elif metric_attributes.resposta["updateAccessToken"] in [None, ""]:
                logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}- metric_attributes.get_update: AccessToken not set")
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Get capture_metrics information from configuration file
    def get_capture(configDict):
        metric_attributes.resposta["captureInterval"] = 15
        metric_attributes.resposta["getApiGet"] = 0
        metric_attributes.resposta["getBackup"] = 0
        metric_attributes.resposta["getCam"] = 0
        metric_attributes.resposta["getDisk"] = 0
        metric_attributes.resposta["getDocker"] = 0
        metric_attributes.resposta["getGpu"] = 0
        metric_attributes.resposta["getIpPing"] = 0
        metric_attributes.resposta["getMonOsProc"] = 0
        metric_attributes.resposta["getNetwork"] = 0
        metric_attributes.resposta["getRemoteOpen"] = 0
        metric_attributes.resposta["getSelfIp"] = 0
        metric_attributes.resposta["getSensor"] = 0
        metric_attributes.resposta["getServer"] = 0
        metric_attributes.resposta["getSysAgent"] = 0
        metric_attributes.resposta["getTopProcess"] = 0
        metric_attributes.resposta["apiUrl"] = []
        metric_attributes.resposta["camUrl"] = []
        metric_attributes.resposta["dockerList"] = []
        metric_attributes.resposta["dockerExceptList"] = []
        metric_attributes.resposta["ipPingList"] = []
        metric_attributes.resposta["monitoredOsProcList"] = []
        metric_attributes.resposta["remoteOpenList"] = []
        metric_attributes.resposta["topOsProcessCount"] = 0
        try: metric_attributes.resposta["captureInterval"] = configDict["captureMetrics"]["captureInterval"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/captureInterval not set")
        if not isinstance(metric_attributes.resposta["captureInterval"], int):
            if metric_attributes.resposta["captureInterval"][-1:] == "s": 
                metric_attributes.resposta["captureInterval"] = metric_attributes.resposta["captureInterval"][:-1]
        if str(metric_attributes.resposta["captureInterval"]).isdigit(): 
            metric_attributes.resposta["captureInterval"] = int(metric_attributes.resposta["captureInterval"])
        else: 
            logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/captureInterval must be in format: <seconds[s]>. Assuming 30s")
            metric_attributes.resposta["captureInterval"] = 30
        if metric_attributes.resposta["captureInterval"] < 5: 
            logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/captureInterval must be >= 5s. Assuming 5s")
            metric_attributes.resposta["captureInterval"] = 5
        try: metric_attributes.resposta["getApiGet"] = metric_attributes.validate_capture(configDict["captureMetrics"]["apiGet"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/apiGet not set. Assuming 'false'")
        try: metric_attributes.resposta["getBackup"] =metric_attributes.validate_capture(configDict["captureMetrics"]["backup"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/backup not set. Assuming 'false'")
        try: metric_attributes.resposta["getCam"] = metric_attributes.validate_capture(configDict["captureMetrics"]["cameraApi"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/cameraApi not set. Assuming 'false'")
        try: metric_attributes.resposta["getDisk"] = metric_attributes.validate_capture(configDict["captureMetrics"]["disk"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/disk not set. Assuming 'false'")
        try: metric_attributes.resposta["getDocker"] = metric_attributes.validate_capture(configDict["captureMetrics"]["docker"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/docker not set. Assuming 'false'")
        try: metric_attributes.resposta["getGpu"] = metric_attributes.validate_capture(configDict["captureMetrics"]["gpu"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/gpu not set. Assuming 'false'")
        try: metric_attributes.resposta["getIpPing"] = metric_attributes.validate_capture(configDict["captureMetrics"]["ipPing"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/ipPing not set. Assuming 'false'")
        try: metric_attributes.resposta["getMonOsProc"] = metric_attributes.validate_capture(configDict["captureMetrics"]["monitoredOsProcess"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/monitoredOsProcess not set. Assuming 'false'")
        try: metric_attributes.resposta["getNetwork"] = metric_attributes.validate_capture(configDict["captureMetrics"]["network"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/network not set. Assuming 'false'")
        try: metric_attributes.resposta["getRemoteOpen"] = metric_attributes.validate_capture(configDict["captureMetrics"]["remoteOpenStatus"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/remoteOpenStatus not set. Assuming 'false'")
        try: metric_attributes.resposta["getSelfIp"] = metric_attributes.validate_capture(configDict["captureMetrics"]["selfIP"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/selfIP not set. Assuming 'false'")
        try: metric_attributes.resposta["getSensor"] = metric_attributes.validate_capture(configDict["captureMetrics"]["sensor"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/sensor not set. Assuming 'false'")
        try: metric_attributes.resposta["getServer"] = metric_attributes.validate_capture(configDict["captureMetrics"]["server"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/server not set. Assuming 'false'")
        try: metric_attributes.resposta["getSysAgent"] = metric_attributes.validate_capture(configDict["captureMetrics"]["sysAgent"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/sysAgent not set. Assuming 'false'")
        try: metric_attributes.resposta["getTopProcess"] = metric_attributes.validate_capture(configDict["captureMetrics"]["topOsProcess"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/topOsProcess not set. Assuming 'false'")
        # Additional Information
        try: urlTemp = configDict["apiUrl"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/apiUrl not set")
        if isinstance(urlTemp, str): 
            if "," in urlTemp:
                metric_attributes.resposta["apiUrl"] = urlTemp.split(",")
            else: metric_attributes.resposta["apiUrl"].append(urlTemp)
        else: metric_attributes.resposta["apiUrl"] = urlTemp
        if (metric_attributes.resposta["getApiGet"] > 0) and ((metric_attributes.resposta["apiUrl"] in [None, ""]) or (len(metric_attributes.resposta["apiUrl"]) == 0)):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/apiGet True but no URL. Disabling Get API")
            metric_attributes.resposta["getApiGet"] = 0
        try: urlTemp = configDict["camUrl"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/camUrl not set")
        if isinstance(urlTemp, str): 
            if "," in urlTemp:
                metric_attributes.resposta["camUrl"] = urlTemp.split(",")
            else: metric_attributes.resposta["camUrl"].append(urlTemp)
        else: metric_attributes.resposta["camUrl"] = urlTemp
        if (metric_attributes.resposta["getCam"] > 0) and ((metric_attributes.resposta["camUrl"] in [None, ""]) or (len(metric_attributes.resposta["camUrl"]) == 0)):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/getCam True but no URL. Disabling Get CAM")
            metric_attributes.resposta["getCam"] = 0
        try: urlTemp = configDict["dockerList"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: dockerList not set")
        if isinstance(urlTemp, str): 
            if "," in urlTemp:
                metric_attributes.resposta["dockerList"] = urlTemp.split(",")
            else: metric_attributes.resposta["dockerList"].append(urlTemp)
        else: metric_attributes.resposta["dockerList"] = urlTemp
        if (metric_attributes.resposta["getDocker"] > 0) and ((metric_attributes.resposta["dockerList"] in [None, ""]) or (len(metric_attributes.resposta["dockerList"]) == 0)):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/getDocker True but no LIST. Disabling Get Docker")
            metric_attributes.resposta["getDocker"] = 0
        try: metric_attributes.resposta["dockerExceptList"] = configDict["dockerExceptList"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: dockerExceptList not set")
        try: urlTemp = configDict["ipPingList"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: ipPingList not set")
        if isinstance(urlTemp, str): 
            if "," in urlTemp:
                metric_attributes.resposta["ipPingList"] = urlTemp.split(",")
            else: metric_attributes.resposta["ipPingList"].append(urlTemp)
        else: metric_attributes.resposta["ipPingList"] = urlTemp
        if (metric_attributes.resposta["getIpPing"] > 0) and ((metric_attributes.resposta["ipPingList"] in [None, ""]) or (len(metric_attributes.resposta["ipPingList"]) == 0)):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/getIpPing True but no LIST. Disabling Get IpPing")
            metric_attributes.resposta["getIpPing"] = 0
        try: urlTemp = configDict["monitoredOsProcessList"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: monitoredOsProcessList not set")
        if isinstance(urlTemp, str): 
            if "," in urlTemp:
                metric_attributes.resposta["monitoredOsProcList"] = urlTemp.split(",")
            else: metric_attributes.resposta["monitoredOsProcList"].append(urlTemp)
        else: metric_attributes.resposta["monitoredOsProcList"] = urlTemp
        if (metric_attributes.resposta["getMonOsProc"] > 0) and ((metric_attributes.resposta["monitoredOsProcList"] in [None, ""]) or (len(metric_attributes.resposta["monitoredOsProcList"]) == 0)):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/getMonOsProc True but no LIST. Disabling Get MonOsProc")
            metric_attributes.resposta["getMonOsProc"] = 0
        try: urlTemp = configDict["remoteOpenList"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: remoteOpenList not set")
        if isinstance(urlTemp, str): 
            if "," in urlTemp:
                metric_attributes.resposta["remoteOpenList"] = urlTemp.split(",")
            else: metric_attributes.resposta["remoteOpenList"].append(urlTemp)
        else: metric_attributes.resposta["remoteOpenList"] = urlTemp
        if (metric_attributes.resposta["getRemoteOpen"] > 0) and ((metric_attributes.resposta["remoteOpenList"] in [None, ""]) or (len(metric_attributes.resposta["remoteOpenList"]) == 0)):
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/getRemoteOpen True but no LIST. Disabling Get RemoteOpen")
            metric_attributes.resposta["getRemoteOpen"] = 0
        try: urlTemp = int(configDict["topOsProcessCount"])
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: topOsProcessCount not set")
        if isinstance(urlTemp, int): metric_attributes.resposta["topOsProcessCount"] = urlTemp
        else:
            try: metric_attributes.resposta["topOsProcessCount"] = int(urlTemp)
            except:
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_capture: captureMetrics/getTopProcess True but no Count. Defaulting number of processes to 3")
                metric_attributes.resposta["topOsProcessCount"] = 3
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Validate IP Address
    def validate_ip(ipAddress):
        a = ipAddress.split('.')
        if len(a) != 4:
            return False
        for x in a:
            if not x.isdigit():
                return False
            i = int(x)
            if i < 0 or i > 255:
                return False
        return True        
        #----------------------------------------------------------------------------------------------------------------------
    # Get backup information from configuration file
    def get_backup(configDict):
        metric_attributes.resposta["backupFolder"] = "./"
        metric_attributes.resposta["backupPrefix"] = ""
        metric_attributes.resposta["backupSuffix"] = ""
        metric_attributes.resposta["backupFrequency"] = "1m"
        try: metric_attributes.resposta["backupFolder"] = configDict["backup"]["folder"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: backup/folder not set")
        try: metric_attributes.resposta["backupPrefix"] = configDict["backup"]["filePrefix"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: backup/filePrefix not set")
        try: metric_attributes.resposta["backupSuffix"] = configDict["backup"]["fileSuffix"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: backup/fileSuffix not set")
        try: metric_attributes.resposta["backupFrequency"] = configDict["backup"]["frequency"]
        except: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.get_restart: backup/frequency not set")
        return
        #----------------------------------------------------------------------------------------------------------------------
    # Capture metrics value conversion
    def validate_capture(inValue):
        resposta = 0
        if isinstance(inValue, str):
            if inValue.lower() in ["none", "0"]: resposta = 0
            elif inValue.lower() in ["light", "1"]: resposta = 1
            elif inValue.lower() in ["full", "2"]: resposta = 2
        elif isinstance(inValue, bool):
            if inValue == True: 
                if metric_attributes.resposta["metricDetails"] == 0: resposta = 1
                elif metric_attributes.resposta["metricDetails"] == 1: resposta = 2
            elif inValue == False: resposta = 0
        elif isinstance(inValue, (int, float)):
            if 0 <= int(inValue) <= 2: resposta = int(inValue)
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    # Validate configuration file paramenters
    def validate(configDict):
        metric_attributes.get_station_id(configDict)
        metric_attributes.get_rtdb(configDict)
        metric_attributes.get_tls(configDict)
        metric_attributes.get_misc(configDict)
        metric_attributes.get_restart(configDict)
        metric_attributes.get_update(configDict)
        metric_attributes.get_capture(configDict)
        metric_attributes.get_backup(configDict)
        metric_attributes.resposta["metricconfig_version"] = str(versao)
        if metric_attributes.resposta["debugMode"]:
            logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric_attributes.validate: configDict: {metric_attributes.resposta}")
        return metric_attributes.resposta
        #----------------------------------------------------------------------------------------------------------------------
