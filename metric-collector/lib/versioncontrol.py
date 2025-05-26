#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "versioncontrol-v5.08-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import requests
import json
from lib import common as c
#######################################################################################################################
c.versionDict["versioncontrol"] = versao
#######################################################################################################################
# get version
# Check for metric collector version update
class version_update:
    def check_outdated(configDict):
        import os
        import sys
        import time
        import importlib
        if configDict["updateUrl"] != "":
            updated = False
            needRestart = False
            for element in c.versionDict:
                libVersion, libFullVersion, libDevVersion, libName = "", "", "", ""
                tempName = c.versionDict[element].split("-")
                libVersion = tempName[-1]
                if len(libVersion) == 14: libVersion = libVersion[2:12]
                if version_update.is_hex(tempName[-2]): libFullVersion = str(tempName[-2]) + "-" + str(libVersion)
                else: libFullVersion = ""
                if libFullVersion == "test" and tempName[-2] == "beta": libFullVersion = "PUB-2846410-2310272107"
                libName = tempName[0]
                if any(v in tempName[1] for v in ["v5", "v6", "v7", "v8"]): libDevVersion = tempName[1]
                else: 
                    libName = libName + "-" + tempName[1]
                    if any(v in tempName[2] for v in ["v5", "v6", "v7", "v8"]): 
                        libDevVersion = tempName[2]
                        libName = libName + "-" + libDevVersion.split(".")[0]
                apiURL = configDict["updateUrl"] + "/inbound/" + libName + ".py"
                try: 
                    apiData = json.loads(requests.get(apiURL).text)["0"]
                    gitInfo = {
                        'lastVersion': apiData[0],
                        'libFolder': apiData[1],
                        'fullName': apiData[2],
                        'libName': apiData[3],
                        'libVersion': apiData[4],
                        'libDevVersion': libDevVersion,
                        'updateTimestamp': float(apiData[6]),
                        'validLib': apiData[7]}
                except Exception as error: 
                    gitInfo = {}
                    logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: API inbound GET error: {error}")
                if len(gitInfo) > 0:
                    if gitInfo["libVersion"] != libFullVersion:
                        try:
                            gitVer = int(gitInfo["libVersion"].split("-")[1])
                            if libVersion.isnumeric(): localLib = int(libVersion)
                            else: localLib = 0
                        except Exception as error:
                            gitVer = 0    
                            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: GIT Version error: {error}")
                        if gitVer > localLib:
                            if gitInfo["libFolder"] == "root": gitInfo["libFolder"] = ""
                            if not os.path.isdir(c.scriptPath + "/" + gitInfo["libFolder"]): 
                                os.mkdir(c.scriptPath + "/" + gitInfo["libFolder"])
                                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: creating modules folder: {c.scriptPath + '/' + gitInfo['libFolder']}")
                            fn = c.scriptPath + "/" + gitInfo["libFolder"] + "/" + libName + ".py"
                            apiURL = configDict["updateUrl"] + "/outbound/" + libName + ".py"
                            try: newFile = requests.get(apiURL)
                            except Exception as error:
                                newFile = ""
                                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: API outbound GET error: {error}")
                            if newFile != "":
                                os.rename(fn, fn + ".vcb")
                                with open(fn, 'w') as f:
                                    f.write(newFile.text)
                                if gitInfo["libFolder"] != "": 
                                    sys.path.append(gitInfo["libFolder"])
                                    newLib = __import__(libName)
                                    importlib.reload(newLib)
                                    sys.path.pop()
                                    updated = True
                                    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: module {libName} updated")
                                    try:
                                        if c.versionDict[libName].split("-")[-1] > libVersion:
                                            os.remove((fn + ".vcb"))
                                        else:
                                            os.remove((fn))
                                            os.rename(fn + ".vcb", fn)
                                            sys.path.append(gitInfo["libFolder"])
                                            newLib = __import__(libName)
                                            importlib.reload(newLib)
                                            sys.path.pop()
                                            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: Failed to load new module {gitInfo['libFolder']}")
                                    except Exception as error:
                                        logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: Failed to remove backup module {gitInfo['libFolder']} - Error: {error}")
                            else: needRestart = True
            if updated: apiStatus = version_update.export_actual(configDict)
        if needRestart: 
            resposta = version_update.restart_service()
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: Metric-collector service restart: {resposta}")
        return
    ###################################################################################################
    def is_hex(num):
        for x in num:
            if not x.isalnum(): return False
        return True
    ###################################################################################################
    def export_actual(configDict):
        import time
        if configDict["updateUrl"] in ["", None]:
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.export_actual: Failed to export: NO update URL in Config File")
            return "no API URL"
        else:
            for element in c.versionDict:
                actualData = {}
                libVersion, libFullVersion, libName = "", "", ""
                tempName = c.versionDict[element].split("-")
                libVersion = tempName[-1]
                if version_update.is_hex(tempName[-2]): libFullVersion = str(tempName[-2]) + "-" + str(libVersion)
                else: libFullVersion = ""
                if libFullVersion == "test" and tempName[-2] == "beta": libFullVersion = "PUB-2846410-2310272107"
                if any(v in tempName[1] for v in ["v5", "v6", "v7", "v8"]):
                    libName = "lib/" + tempName[0] + ".py"
                    actualData["libDevVersion"] = tempName[1]
                else: 
                    libName = tempName[0] + "-" + tempName[1]
                    if any(v in tempName[2] for v in ["v5", "v6", "v7", "v8"]):
                        libName = libName + "-" + tempName[2].split(".")[0]
                        actualData["libDevVersion"] = tempName[2]
                    libName = libName + ".py"
                actualData['customer'] = configDict["customerName"]
                actualData['station'] = configDict["stationName"]
                actualData['host'] = configDict["hostName"]
                actualData['libName'] = libName
                actualData['libVersion'] = libFullVersion
                apiURL = configDict["updateUrl"] + "/history"
                updateResp = requests.post(apiURL, json=actualData)
                if updateResp.status_code != 200: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.export_actual: Failed to POST: Response = {updateResp.status_code}")
        if updateResp.status_code == 200 and c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.export_actual: Export to API successful: Response = {updateResp.status_code}")
        return updateResp.status_code
    ###################################################################################################
    def get_actual(configDict):
        import time
        payload = configDict["customerName"] + "&" + configDict["stationName"] + "&" + configDict["hostName"]
        apiURL = configDict["updateUrl"] + "/history/" + payload
        getResp = requests.get(apiURL, params=payload)
        if getResp.status_code == 200: getResp = getResp.json()
        else: 
            getResp = []
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.get_actual: Failed to GET: Response = {getResp.status_code}")
        return getResp
    ###################################################################################################
    def restart_service():
        import subprocess
        import time
        try: subprocess.call('systemctl restart metric-collector.service', shell = True)
        except: 
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sys_agent_exec.sysagent_restart: Error restarting sysagent")
            resposta = "error"
        else: resposta = "success"
        return resposta
    ###################################################################################################
