#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricping-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricping"] = versao
#######################################################################################################################
class ping_exec:
    # Execute Station Ping metric collector
    def collect_ping(getIpPing, ipPingList):
        pingout, pingExecError = {}, 0
        if getIpPing:
            if ipPingList not in [None, 0, ""]:
                if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricping version: {versao}")
                pingListCount = 0
                for item in ipPingList:
                    try: 
                        ipPing = c.exec_cmd(["ping", "-c", "2", item.strip()], c.debugMode)["output"].splitlines()
                    except:
                        if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-ping_exec.collect_ping: PS execution error")
                        pingExecError = 1
                    else:
                        pingout[pingListCount] = {"ipAddr": item, "resp": ping_exec.ping_metrics(ipPing)}
                        pingListCount += 1
        pingout["pingExecError"] = pingExecError
        return pingout
        #----------------------------------------------------------------------------------------------------------------------
    def ping_metrics(pingout):
        resposta = {
            "packLoss": 100,
            "execTime": 0}
        for item in range(len(pingout)):
            if pingout[item] != "":
                if "transmitted" in pingout[item]: 
                    a = pingout[item].split(",")
                    for n in range(len(a)):
                        if "time" in a[n]: resposta["execTime"] = float(a[n].split()[1].strip()[:-2])/1000
                        if "loss" in a[n]: resposta["packLoss"] = int(a[n].split()[0].strip()[:-1])
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
