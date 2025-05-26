#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricjetson-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
import os
from lib import common as c
from jtop import jtop, JtopException
#######################################################################################################################
c.versionDict["metricjetson"] = versao
#######################################################################################################################
class jetson_exec:
    def collect_jetson(getJetson):
        jetsonout, jetsonExecError = {}, 0
        jetsonMetrics = {}
        if getJetson:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricjetson version: {versao}")
            jetsonPath = "/usr/local/cuda/samples/1_Utilities/deviceQuery/deviceQuery"
            jetsonPath2 = "/opt/eyeflow/monitor/jetson/deviceQuery"
            if os.path.exists(jetsonPath):
                try: 
                    jetsonout = c.exec_cmd([jetsonPath], c.debugMode)["output"].splitlines()
                except Exception as e: 
                    if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-jetson_exec.collect_jetson: Device Query execution error {e}")
                    jetsonExecError = 1

            elif os.path.exists(jetsonPath2):
                try: jetsonout = c.exec_cmd([jetsonPath2], c.debugMode)["output"].splitlines()
                except Exception as e: 
                    if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-jetson_exec.collect_jetson: Device Query execution error on path2 {e}")
                    jetsonExecError = 1
        jetsonMetrics = jetson_exec.jetson_metrics(jetsonout, jetsonExecError)
        return jetsonMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def collect_tegrastats(resposta):
        def get_ram(resposta, tegraVal):
            if tegraVal not in [None, "", 0]:
                used = tegraVal.split("/")[0]
                if used.isnumeric(): resposta["ramUsed"] = int(used)
                mtot = tegraVal.split("/")[1]
                if len(mtot) > 2:
                    if str(mtot[-2:]).lower() == "mb":
                        if mtot[:-2].isnumeric(): tegraRamTotal = int(mtot[:-2])
                    elif str(mtot[-2:]).lower() == "gb":
                        if mtot[:-2].isnumeric(): resposta["tegraRamTotal"] = int(mtot[:-2]) * 1024
            if resposta["memTotalMB"] != tegraRamTotal: resposta["memTotalMB"] = max(resposta["memTotalMB"], tegraRamTotal)
            return resposta
            #----------------------------------------------------------------------------------------------------------------------
        def get_cpu(resposta, tegraVal):
            if tegraVal not in [None, "", 0]:
                if len(tegraVal) > 2:
                    if tegraVal[:1] == "[": tegraVal = tegraVal[1:]
                    if tegraVal[-1:] == "]": tegraVal = tegraVal[:-1]
                    used = tegraVal.split(",")
                    resposta["cpuTotalCount"] = len(used)
                    avgCpu, maxCpu, activeCpu = 0, 0, 0
                    for item in range(len(used)):
                        if "%@" in used[item]:
                            activeCpu += 1
                            cpuUsed = used[item].split("%@")[0]
                            if cpuUsed.isnumeric(): cpuUsed = int(cpuUsed)
                            else: cpuUsed = 0
                            avgCpu += cpuUsed
                            if maxCpu < cpuUsed: maxCpu = cpuUsed
                        if activeCpu == 0: activeCpu = 10
                        avgCpu = float(avgCpu) / activeCpu
            resposta["cpuAvgUse"] = avgCpu
            resposta["cpuMaxUse"] = maxCpu
            resposta["cpuActiveCount"] = activeCpu
            return resposta
            #----------------------------------------------------------------------------------------------------------------------
        def get_temp(tempVal):
            tempRet = 0
            if "@" in tempVal:
                tempVal = tempVal.split("@")[1]
                if tempVal[-1].lower() == "c":
                    if tempVal[:-1].replace(".", "").isnumeric(): 
                        tempRet = float(tempVal[:-1])
                elif tempVal[-1].lower() == "f":
                    if tempVal[:-1].isnumeric(): tempRet = (float(tempVal[:-1]) - 32.0) * 5 / 9
            return tempRet
            #----------------------------------------------------------------------------------------------------------------------
        resposta["cpuTotalCount"] = 0
        resposta["cpuActiveCount"] = 0
        resposta["ramUsed"] = 0
        resposta["cpuAvgUse"] = 0
        resposta["cpuMaxUse"] = 0
        resposta["gpuUse"] = 0
        resposta["tempCPU"] = 0
        resposta["tempGPU"] = 0
        resposta["tempBoard"] = 0
        resposta["powerThermal"] = 0
        resposta["tempWifi"] = 0
        a=c.exec_pipe(["tegrastats"], ["head", "-n 1"], "raw")["output"]
        if len(a) > 0: a = a.split()
        for item in range(len(a)):
            if "ram" in a[item].lower(): resposta = get_ram(resposta, a[item + 1])
            if "cpu" in a[item].lower() and "cpu@" not in a[item].lower(): resposta = get_cpu(resposta, a[item + 1])
            if "gr3d" in a[item].lower():
                if a[item + 1][-1] == "%":
                    if a[item + 1][:-1].isnumeric(): resposta["gpuUse"] = int(a[item + 1][:-1])
            if "cpu@" in a[item].lower(): resposta["tempCPU"] = get_temp(a[item])
            if "gpu@" in a[item].lower(): resposta["tempGPU"] = get_temp(a[item])
            if "tboard@" in a[item].lower(): resposta["tempBoard"] = get_temp(a[item])
            if "thermal@" in a[item].lower(): resposta["powerThermal"] = get_temp(a[item])
            if "iwlwifi@" in a[item].lower(): resposta["tempWifi"] = get_temp(a[item])
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def get_info(resposta):
        JETSON_SOC, jetsonInfoError = "", 0
        if os.path.isfile("/proc/device-tree/compatible"):
            f = open("/proc/device-tree/compatible", "r")
            JETSON_SOC = f.read().lower()
        if "2180" in JETSON_SOC: resposta["gpuName"]="TX1"
        if "p3310" in JETSON_SOC: resposta["gpuName"]="TX2"
        if "p3489-0080" in JETSON_SOC: resposta["gpuName"]="TX2 4GB"
        if "p3489" in JETSON_SOC: resposta["gpuName"]="TX2i"
        if "p2888-0006" in JETSON_SOC: resposta["gpuName"]="AGX Xavier [8GB]"
        if "p2888-0001" in JETSON_SOC or "p2888-0004" in JETSON_SOC: resposta["gpuName"]="AGX Xavier [16GB]"
        if "p2888" in JETSON_SOC: resposta["gpuName"]="AGX Xavier [32GB]"
        if "p3448-0002" in JETSON_SOC: resposta["gpuName"]="Nano"
        if "p3448" in JETSON_SOC: resposta["gpuName"]="Nano (Developer Kit Version)"
        if "p3668-0001" in JETSON_SOC: resposta["gpuName"]="Xavier NX"
        if "p3668" in JETSON_SOC: resposta["gpuName"]="Xavier NX (Developer Kit Version)"
        if "*" in JETSON_SOC: resposta["gpuName"]=""
        try: nvp = c.exec_cmd(["/usr/sbin/nvpmodel", "-q"], c.debugMode)["output"].splitlines()
        except:
            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-jetson_exec.get_info: NVP execution error")
            jetsonInfoError = 1
        else:
            if len(nvp) > 0:
                resposta["nvpModel"] = ""
                for item in nvp:
                    if "power" in item.lower() and "mode" in item.lower(): resposta["nvpModel"] = item.split(":")[1].strip()
        try: fan = c.exec_cmd(["cat", "/sys/devices/platform/pwm-fan/hwmon/hwmon3/pwm1"], c.debugMode)["output"].splitlines()
        except:
            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-jetson_exec.get_info: FAN execution error")
            jetsonInfoError = 1
        else:
            if len(fan) > 0: 
                if fan[0].replace(".", "").isnumeric(): fan = float(fan[0])
                else: fan = 0
                resposta["fanPercent"] = fan
        resposta["jetsonExecError"] = max(resposta["jetsonExecError"], jetsonInfoError)
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def jetson_metrics(jetsonData, jetsonExecError):
        a = {}
        resposta = {
            "jetsonExecError": jetsonExecError,
            "card": "",
            "driver": "",
            "cuda": "",
            "gpuName": "",
            "memTotalMB": 0}
        for item in range(len(jetsonData)):
            if (4 <= item <= 7) and ("Device" in jetsonData[item]): resposta["card"] = jetsonData[item].split(":")[0].split()[-1].strip()
            if (5 <= item <= 8) and ("Driver" in jetsonData[item]) and ("CUDA" in jetsonData[item]): resposta["driver"] = jetsonData[item].split()[-1].strip()
            if (5 <= item <= 8) and ("Driver" in jetsonData[item]) and ("CUDA" in jetsonData[item]): resposta["cuda"] = jetsonData[item].split("/")[1].split()[-1]
            if (5 <= item <= 7) and ("Device" in jetsonData[item]): resposta["gpuName"] = str(jetsonData[item].split(":")[-1].strip().replace("'","").replace('"', ''))
            if (5 <= item <= 10) and ("amount" in jetsonData[item]) and ("global" in jetsonData[item]): resposta["memTotalMB"] = int(jetsonData[item].split(":")[1].split()[0])
        try: a = jetson_exec.collect_tegrastats(resposta)
        except Exception as e: 
            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-jetson_exec.jetson_metrics: collect_tegra execution error {e}")
            resposta["jetsonExecError"] = 1
        else: resposta.update(a)
        resposta = jetson_exec.get_info(resposta)
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
