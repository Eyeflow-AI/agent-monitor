#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metrictop-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metrictop"] = versao
#######################################################################################################################
class top_exec:
    # Execute Top Memory Processes metric collector
    def collect_top(getTopProc, topCount):
        topprocout, topExecError = "", 0
        if getTopProc:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metrictop version: {versao}")
            try: topprocout = c.exec_cmd(["ps", "-eo", "pid,%mem,%cpu,cmd", "--sort=-%mem"], c.debugMode)["output"].splitlines()
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-top_exec.collect_top: PS Top Offender execution error")
                topExecError = 1
        if topprocout != "": topProcMetrics = top_exec.top_proc_metrics(topprocout, topCount, topExecError)
        else: topProcMetrics = 0
        return topProcMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def top_proc_metrics(topprocout, numProcs, topExecError):
        global logErrorFirstRun
        resposta, topProcCount = {}, 0
        if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-top_exec.top_proc_metrics: Process Qty: {numProcs}")
        if numProcs > 0:
            if len(topprocout) > numProcs: countLimit = numProcs
            else: countLimit = len(topprocout)
            for task in range(1, countLimit + 1):
                resposta[topProcCount] = {
                    "pid": int(topprocout[task].split()[0]),
                    "mem": float(topprocout[task].split()[1].replace(',', '.')),
                    "cpu": float(topprocout[task].split()[2].replace(',', '.')),
                    "rank": task,
                    "cmd": ' '.join(topprocout[task].split()[3:])}
                topProcCount += 1
        resposta["topExecError"] = topExecError
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
