#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricremote-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricremote"] = versao
#######################################################################################################################
class remote_open_exec: 
    # Execute Remote check for Open Port metric collector
    def collect_remote_open(getRemoteOpen, remoteOpenList):
        remoteopenout, remoteOpenMetrics, remoteOpenExecError = "", {}, 0
        if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricapiget version: {versao}")
        if getRemoteOpen:
            if remoteOpenList != None:
                if (len(remoteOpenList) > 0):
                    remoteOpenCount = 0
                    for remoteOpenItem in remoteOpenList:
                        remoteTemp = {}
                        if ":" in remoteOpenItem:
                            ipUrl = remoteOpenItem.split(":")[0]
                            portUrl = remoteOpenItem.split(":")[1]
                            try: remoteopenout = c.exec_cmd(["nc", "-zvw5", str(ipUrl), str(portUrl)], c.debugMode)["output"]
                            except:
                                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-remote_open_exec.collect_remote_open: Get IP:PORT data error")
                                remoteOpenExecError = 1
                        else:
                            try: remoteopenout = c.exec_cmd(["nc", "-zvw5", str(remoteOpenItem)], c.debugMode)["output"]
                            except:
                                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-remote_open_exec.collect_remote_open: Get URL data error")
                                remoteOpenExecError = 1
                        if remoteopenout != "":
                            remoteTemp["remoteOpenUrl"] = remoteOpenItem
                            remoteTemp.update(remote_open_exec.remote_open_metrics(remoteopenout))
                        else:
                            remoteTemp["remoteOpenUrl"] = remoteOpenItem
                            remoteTemp["remoteOpenStatus"] = 0
                            remoteTemp["remoteOpenResponse"] = "not_found"
                        remoteOpenMetrics[remoteOpenCount] = remoteTemp
                        remoteOpenCount += 1
        remoteOpenMetrics["remoteOpenExecError"] = remoteOpenExecError
        return remoteOpenMetrics
        #----------------------------------------------------------------------------------------------------------------------
    # Prepare API GET metrics data
    def remote_open_metrics(remoteopenout):
        resposta = {}
        try: remoteOpenData = remoteopenout.splitlines()
        except: remoteOpenData = 0
        else:
            if len(remoteOpenData) > 0:
                resposta = {
                    "remoteOpenStatus": 0,
                    "remoteOpenResponse": ""
                }
                for item in remoteOpenData:
                    if "refused" in item: resposta["apiGetStatus"] = 1
                    if item[:4] == "HTTP":
                        apiGetStatus = item.split()
                        if (apiGetStatus[-1].strip().isnumeric()): resposta["remoteOpenStatus"] = int(apiGetStatus[-1].strip())
                        elif (apiGetStatus[-2].strip().isnumeric()): resposta["remoteOpenStatus"] = int(apiGetStatus[-2].strip())
                        else: resposta["remoteOpenStatus"] = 0
                resposta["remoteOpenResponse"] = remoteOpenData[-1]
            else: resposta = 0
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
