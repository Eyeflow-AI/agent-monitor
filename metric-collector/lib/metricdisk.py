#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricdisk-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricdisk"] = versao
#######################################################################################################################
class disk_exec:
    # Execute disk metric collector
    def collect_disk(getDisk):
        diskout, diskDfExecError, diskStatExecError = "", 0, 0
        if getDisk:
            orderList = {}
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricdisk version: {versao}")
            try: diskdf = c.exec_cmd(["df"], c.debugMode)["output"].splitlines()
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-disk_exec.collect_disk: DF execution error")
                diskDfExecError = 1
                diskdf = []
            try: diskstat = c.exec_cmd(["iostat", "-dx", "-k"], c.debugMode)["output"].splitlines()
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-disk_exec.collect_disk: IOSTAT execution error")
                diskStatExecError = 1
            if len(diskstat) > 2:
                a = diskstat[2].split()
                orderList = {"device": 0, "rrps": 0, "wrps": 0, "rrqps": 0, "wrqps": 0, "rawait": 0, "wawait": 0, "aql": 0}
                for element in range(len(a)):
                    if "Device" in a[element]: orderList["device"] = element
                    if "r/s" in a[element]: orderList["rrps"] = element
                    if "w/s" in a[element]: orderList["wrps"] = element
                    if "rrqm/s" in a[element]: orderList["rrqps"] = element
                    if "wrqm/s" in a[element]: orderList["wrqps"] = element
                    if "r_await" in a[element]: orderList["rawait"] = element
                    if "w_await" in a[element]: orderList["wawait"] = element
                    if "aqu-sz" in a[element]: orderList["aql"] = element
            diskout = {"df": diskdf, "stat": diskstat, "order": orderList}
        if diskout != "": diskMetrics = disk_exec.disk_metrics(diskout, c.logFirstRun, c.debugMode)
        diskMetrics["diskDfExecError"] = diskDfExecError
        diskMetrics["diskExecError"] = diskStatExecError
        return diskMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def disk_metrics(diskData, logFirstRun, debugMode):
        resposta, volNum = {}, 0
        for unit in range(1, len(diskData["df"])):
            if not any(novol in diskData["df"][unit] for novol in ["loop", "snap"]):
                try: resposta[volNum] = {
                    "volume": diskData["df"][unit].split()[5], 
                    "size": float(diskData["df"][unit].split()[1].replace(',', '.')),
                    "used": float(diskData["df"][unit].split()[2].replace(',', '.')),
                    "usedPct": float(diskData["df"][unit].split()[4].split("%")[0].replace(',', '.'))}
                except: 
                    resposta[volNum] = {"volume": "", "size": "", "used": "", "usedPct": 0}
                    if not logFirstRun: logging.warning(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-disk_exec.disk_metrics: Cannot get Disk df info")
                volNum += 1
        for unit in range(1, len(diskData["stat"])):
            if "loop" not in diskData["stat"][unit] and "Device" not in diskData["stat"][unit] and diskData["stat"][unit] != "":
                try: resposta[volNum] = {
                    "device": diskData["stat"][unit].split()[diskData["order"]["device"]],
                    "rrps": float(diskData["stat"][unit].split()[diskData["order"]["rrps"]].replace(',', '.')),
                    "wrps": float(diskData["stat"][unit].split()[diskData["order"]["wrps"]].replace(',', '.')),
                    "rrqps": float(diskData["stat"][unit].split()[diskData["order"]["rrqps"]].replace(',', '.')),
                    "wrqps": float(diskData["stat"][unit].split()[diskData["order"]["wrqps"]].replace(',', '.')),
                    "rawait": float(diskData["stat"][unit].split()[diskData["order"]["rawait"]].replace(',', '.')),
                    "wawait": float(diskData["stat"][unit].split()[diskData["order"]["wawait"]].replace(',', '.')),
                    "aql": float(diskData["stat"][unit].split()[diskData["order"]["aql"]].replace(',', '.'))}
                except: 
                    resposta[volNum] = {"device": "", 
                                        "rrps": 0, 
                                        "wrps": 0, 
                                        "rrqps": 0, 
                                        "wrqps": 0, 
                                        "rawait": 0, 
                                        "wawait": 0, 
                                        "aql": 0}
                    if not logFirstRun: logging.warning(
                        f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-disk_exec.disk_metrics: Cannot get Disk stat info")
                volNum += 1
        if volNum == 0:
            resposta = 0
            if not logFirstRun: logging.warning(
                f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-disk_exec.disk_metrics: No active Disks")
        if debugMode: logging.debug(
            f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-disk_exec.disk_metrics: Active Volumes: {volNum}")
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
