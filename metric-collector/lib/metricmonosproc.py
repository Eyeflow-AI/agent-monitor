#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricmonosproc-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricmonosproc"] = versao
#######################################################################################################################
class mon_os_proc_exec:
    # Execute Monitored Ubuntu Processes metric collector
    def collect_mon_os_proc(getMonOsProc, monOsProcList):
        processout, monosprocExecError = "", 0
        if getMonOsProc:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricprocess version: {versao}")
            try: processout = c.exec_cmd(["ps", "-fA"], c.debugMode)["output"].splitlines()
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Get Metrics: PS execution error")
                monosprocExecError = 1
        if processout != "": processMetrics = mon_os_proc_exec.mon_os_proc_metrics(processout, monOsProcList)
        monosprocExecError = monosprocExecError or processMetrics["detailExecError"]
        processMetrics["monosprocExecError"] = monosprocExecError
        return processMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def mon_os_proc_metrics(processData, osProcessList):
        resposta = {"missingProcess": ""}
        processCount, runProcess, processPID, execError = 0, [], [], 0
        if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Process Metrics: Process List: {osProcessList}")
        if osProcessList != 0:
            if osProcessList != None:
                for task in range(len(osProcessList)):
                    procTemp = {}
                    procTemp = {
                        "processCfg": osProcessList[task],
                        "user": "none",
                        "pid": 0,
                        "cpu": 0.0,
                        "mem": 0.0,
                        "time": 0.0,
                        "processActive": 0,
                        "cmd": "none"}
                    for element in range(1, len(processData)):
                        evalProcess = processData[element].split()
                        hourItem = 0
                        for item in range(len(evalProcess)):
                            if evalProcess[item].count(":") >= 2:
                                break
                            hourItem += 1
                        procCmd = ' '.join(evalProcess[hourItem + 1:])
                        if osProcessList[task] in procCmd:
                            runProcess.append(osProcessList[task])
                            if evalProcess[1] not in set(processPID):
                                try: pTime = evalProcess[hourItem].split(":")
                                except: pTime = [0]
                                try: pData = c.exec_cmd(["ps", "-p", evalProcess[1], "-o", "%cpu,%mem"], c.debugMode)["output"].splitlines()[1].split()
                                except: 
                                    pData = [0, 0]
                                    execError = 1
                                if pTime[0].count("-") > 0:
                                    timeVal = pTime[0].split("-")
                                    if timeVal[0].isnumeric: dd = int(timeVal[0])*24
                                    if timeVal[1].isnumeric: dd += int(timeVal[1])
                                elif pTime[0].isnumeric: dd = int(pTime[0])
                                else: dd = 0
                                try: mVal = int(pTime[1])*60
                                except: mVal = 0
                                try: sVal = int(pTime[2])
                                except: sVal = 0
                                try: cpuVal = str(pData[0]).replace(',', '.')
                                except:
                                    if pData[0].isnumeric: cpuVal = float(pData[0])
                                    else: cpuVal = 0
                                try: memVal = str(pData[1]).replace(',', '.')
                                except:
                                    if pData[1].isnumeric: memVal = float(pData[1])
                                    else: memVal = 0
                                procTemp = {
                                    "processCfg": osProcessList[task],
                                    "user": evalProcess[0],
                                    "pid": int(evalProcess[1]),
                                    "cpu": float(cpuVal),
                                    "mem": float(memVal),
                                    "time": dd*3600 + mVal*60 + sVal,
                                    "processActive": 1,
                                    "cmd": procCmd}
                                processPID.append(evalProcess[1])
                    resposta[processCount] = procTemp
                    processCount += 1
        if osProcessList != None:
            if len(osProcessList) > 0: 
                if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Process Metrics: No active Processes")
            if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Process Metrics: Active Processes: {processCount}")
            resposta["missingProcess"] = list((set(osProcessList).difference(set(runProcess))))
        resposta["detailExecError"] = execError
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
