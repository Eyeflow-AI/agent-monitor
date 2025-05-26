#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricnet-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricnet"] = versao
#######################################################################################################################
class net_exec:
    # Execute Network metric collector
    def collect_selfip(getSelfIP, selfIpList):
        if getSelfIP:
            net1 = net_exec.get_net()
            resposta = {}
            ipItem = 0
            if selfIpList != 0 and len(net1) > 0:
                for item in range(len(selfIpList)):
                    selfIpTemp = {
                        "ip": selfIpList[item],
                        "present": 0}
                    for element in range(len(net1["netaddr"])):
                        if selfIpTemp["ip"] in net1["netaddr"][element]: selfIpTemp["present"] = 1
                    resposta[ipItem] = selfIpTemp
                    ipItem += 1
        resposta["netExecError"] = net1["netexecerror"]
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def get_net():
        if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricnet version: {versao}")
        resposta = {
            "netout": "",
            "netaddr": "",
            "netexecerror": 0}
        try: resposta["netout"] = c.exec_cmd(["ip", "-s", "link"], c.debugMode)["output"].splitlines()
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-net_exec.get_net: Cannot get Network Metrics")
            resposta["netexecerror"] = 1
        try: resposta["netaddr"] = c.exec_cmd(["ip", "-4", "addr"], c.debugMode)["output"].splitlines()
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-net_exec.get_net: Cannot get Network Address")
            resposta["netexecerror"] = 1
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def net_metrics(measure1, measure2, timeInt):
        resposta, activeNic = {}, 0
        nicName, nicIP = "nonic", "0.0.0.0"
        for netCount in range(len(measure2["netout"])):
            if "state UP" in measure2["netout"][netCount]:
                nicName = measure2["netout"][netCount].split(":")[1].strip()
                rxBytes2 = int(measure2["netout"][netCount + 3].split()[0].strip())
                txBytes2 = int(measure2["netout"][netCount + 5].split()[0].strip())
                for nameCount in range(len(measure1["netaddr"])):
                    if nicName in measure1["netaddr"][nameCount] and "inet" in measure1["netaddr"][nameCount]:
                        nicIP = measure1["netaddr"][nameCount].split()[1]
                for contador in range(len(measure1["netout"])):
                    if nicName in measure1["netout"][contador]:
                        if len(measure1["netout"]) >= netCount + 5:
                            rxBytes1 = int(measure1["netout"][netCount + 3].split()[0].strip())
                            txBytes1 = int(measure1["netout"][netCount + 5].split()[0].strip())
                        else: 
                            rxBytes1 = 0
                            txBytes1 = 0
                if rxBytes2 - rxBytes1 >= 0:
                    resposta[activeNic] = {
                        "name": nicName,
                        "ipAddr": nicIP,
                        "rxBps": (rxBytes2 - rxBytes1) / timeInt,
                        "txBps": (txBytes2 - txBytes1) / timeInt}
                    activeNic += 1
        if activeNic == 0:
            resposta["netexecerror"] = 0
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-net_exec.net_metrics: No active NICs")
        if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-net_exec.net_metrics: Active NICs: {activeNic}")
        resposta["netexecerror"] = int(measure1["netexecerror"] or measure2["netexecerror"])
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
