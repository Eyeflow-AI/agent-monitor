#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricserver-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
import os
from lib import common as c
from datetime import datetime, timezone
#######################################################################################################################
c.versionDict["metricserver"] = versao
#######################################################################################################################
class server_exec:
    # Execute Server metric collector
    def collect_server(getServer):
        serverout, serverExecError = "", 0
        if getServer:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricserver version: {versao}")
            try: serverout = c.exec_cmd(["top", "-b", "-n", "1"], c.debugMode)["output"].splitlines()
            except:
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.collect_server: TOP execution error")
                serverExecError = 1
        if serverout != "": serverMetrics = server_exec.server_metrics(serverout, serverExecError)
        else: serverMetrics = 0
        return serverMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def server_metrics(osData, serverExecError):
        resposta = {
            "serverExecError": serverExecError,
            "cpuCores": 0,
            "servertime": 0,
            "servertimeUTC": 0,
            "serverUp": 0,
            "loadAvg1m": 0,
            "loadAvg5m": 0,
            "loadAvg15m": 0,
            "taskTotal": 0,
            "taskRunning": 0,
            "taskSleeping": 0,
            "taskStopped": 0,
            "taskZombie": 0,
            "cpuUser": 0,
            "cpuSys": 0,
            "cpuIdle": 0,
            "memTotal": 0,
            "memFree": 0,
            "memCached": 0,
            "memUsed": 0}
        pid = os.getpid()
        if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: PID: {pid}")
        for item in range(len(osData)):
            if osData[item] != "":
                if str(pid) in osData[item].split()[0]:
                    try: 
                        a = osData[item]
                        b = osData[item].split()
                        resposta["selfCpuUsage"] = float(osData[item].split()[8].replace(',', '.'))
                        resposta["selfMemUsage"] = float(osData[item].split()[9].replace(',', '.'))
                    except: 
                        resposta["selfCpuUsage"] = 0
                        resposta["selfMemUsage"] = 0
                        if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Self Metrics")
        if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: SelfCPU: {resposta['selfCpuUsage']}")
        if c.debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: SelfMEM: {resposta['selfMemUsage']}")
        try: resposta["cpuCores"] = int(c.exec_cmd(["nproc"], c.debugMode)["output"].splitlines()[0])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get CPU Cores Info")
            resposta["serverExecError"] = 1
        try: 
            horaLoc = osData[0].split("up", 1)[0].strip()[-8:]
            dataLoc = datetime.today()
            dt = datetime.combine(dataLoc, datetime.strptime(horaLoc, '%H:%M:%S').time())
            resposta["servertime"] = dt.timestamp()
            resposta["servertimeUTC"] = dt.replace(tzinfo=timezone.utc).timestamp()
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Server Time Info")
        try: 
            resposta["serverUp"] = ','.join(osData[0].split("up", 1)[1].split("user", 1)[0].split(",")[:-1])
            if resposta["serverUp"][-1].isnumeric(): resposta["serverUp"] = resposta["serverUp"] + "h"
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Uptime Info")
        try: getLoad = osData[0].split("average", 1)[1][1:].strip().split(" ")
        except: getLoad = 0
        try: resposta["loadAvg1m"] = float(getLoad[0][:-1].replace(",", "."))/float(resposta["cpuCores"])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Load Avg 1m Info")
        try: resposta["loadAvg5m"] = float(getLoad[1][:-1].replace(",", "."))/float(resposta["cpuCores"])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Load Avg 5m Info")
        try: resposta["loadAvg15m"] = float(getLoad[2].replace(",", "."))/float(resposta["cpuCores"])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Load Avg 15m Info")
        try: taskout = osData[1].split(":")[1].split(",")
        except: taskout = ""
        try: resposta["taskTotal"] = int(taskout[0].strip().split()[0].strip())
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Tasks Total Info")
        try: resposta["taskRunning"] = int(taskout[1].strip().split()[0])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Tasks Running Info")
        try: resposta["taskSleeping"] = int(taskout[2].strip().split()[0])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Tasks Sleeping Info")
        try: resposta["taskStopped"] = int(taskout[3].strip().split()[0])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Tasks Stopped Info")
        try: resposta["taskZombie"] = int(taskout[4].strip().split()[0])
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Tasks Zombie Info")
        try: cpuout = osData[2].split(":")[1].strip()
        except: cpuout = ""
        if "sy" in cpuout: systag = "sy"
        else: systag = "sis"
        if "id" in cpuout: idltag = "id"
        else: idltag = "oc"
        try: resposta["cpuUser"] = float(cpuout.split("us")[0].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get User CPU Info")
        try: cpuout = cpuout.split("us")[1][1:].strip()
        except: cpuout = ""
        try: resposta["cpuSys"] = float(cpuout.split(systag)[0].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get System CPU Info")
        try: cpuout = cpuout.split(systag)[1][1:].strip()
        except: cpuout = ""
        try: resposta["cpuUser"] += float(cpuout.split("ni")[0].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get CPU User 2 Info")
        try: cpuout = cpuout.split("ni")[1][1:].strip()
        except: cpuout = ""
        try: resposta["cpuIdle"] = float(cpuout.split(idltag)[0].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get CPU Idle Info")
        try: cpuout = cpuout.split(idltag)[1][1:].strip()
        except: cpuout = ""
        if "ih" in cpuout: sitag = "ih"
        else: sitag = "hi"
        try: cpuout = cpuout.split(sitag)[1][1:].strip()
        except: cpuout = ""
        if "is" in cpuout: sitag = "is"
        else: sitag = "si"
        try: resposta["cpuSys"] += float(cpuout.split(sitag)[0].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get CPU System 2 Info")
        try: getMem = c.exec_cmd("free", c.debugMode)["output"].splitlines()[1].split(":")[1].split()
        except:
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get FREE Info")
            resposta["serverExecError"] = 1
        try: resposta["memTotal"] = float(getMem[0].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Total Memory Info")
        try: resposta["memFree"] = float(getMem[2].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Free Memory Info")
        try: resposta["memUsed"] = float(getMem[1].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Used Memory Info")
        try: resposta["memCached"] = float(getMem[4].strip().replace(",", "."))
        except: 
            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-server_exec.server_metrics: Cannot get Cached Memory Info")
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
