#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricsensor-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricsensor"] = versao
#######################################################################################################################
class sensor_exec:
    # Execute LM-Sensors metric collector
    def collect_sensor(getSensor):
        sensorout, sensorExecError = "", 0
        if getSensor:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricsensor version: {versao}")
            try: sensorout = c.exec_cmd(["sensors"], c.debugMode)["output"].splitlines()
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.collect_sensor: Sensors execution error")
                sensorExecError = 1
        if sensorout != "": sensorMetrics = sensor_exec.sensor_metrics(sensorout, sensorExecError)
        else: sensorMetrics = 0
        return sensorMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def sensor_metrics(sensorOut, sensorExecError):
        resposta = {
            "sensorExecError": sensorExecError,
            "pciPower": 0.0,      ##### (crit =  94.92 W)
            "vCore": 0.0,         ##### (min =  +0.80 V, max =  +1.60 V)
            "v3.3": 0.0,          ##### (min =  +2.97 V, max =  +3.63 V)
            "v5.0": 0.0,          ##### (min =  +4.50 V, max =  +5.50 V)
            "v12.0": 0.0,         ##### (min = +10.20 V, max = +13.80 V)
            "cpuFanRPM": 0,       ##### (min =  600 RPM, max = 7200 RPM)
            "chassisFanRPM": 0,   ##### (min =  600 RPM, max = 7200 RPM)
            "cpuTemp": 0.0,       ##### (high = +60.0°C, crit = +95.0°C)
            "mbTemp": 0.0,        ##### (high = +45.0°C, crit = +75.0°C)
            "pciTemp": 0.0,       ##### (high = +70.0°C, crit = +83.5°C, hyst = +80.5°C)
            "pciPowerMax": 94.92,
            "vCoreMax": 1.6,
            "v3.3Max": 3.63,
            "v5.0Max": 5.5,
            "v12.0Max": 13.8,
            "cpuFanRpmMax": 7200,
            "chassisFanRpmMax": 7200,
            "cpuTempMax": 95.0,
            "mbTempMax": 75.0,
            "pciTempMax": 83.5}
        tempCpuMax = 0
        critTemp = 0
        for item in range(len(sensorOut)):
            if ("CPU" in sensorOut[item] and "Temp" in sensorOut[item]) or "Package" in sensorOut[item] or "Core" in sensorOut[item]:
                try:
                    cpuTemp = float(sensorOut[item].split(":")[1].strip().split("(")[0].strip()[:-2].replace(',', '.'))
                    tempMax = float(sensorOut[item].rsplit("=", 1)[1][:-3].strip().replace("+", ""))
                except:
                    cpuTemp = 0.0
                    tempMax = 0.0
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in CPU Temperature")
                finally:
                    if resposta["cpuTemp"] < cpuTemp: resposta["cpuTemp"] = cpuTemp
                    if tempCpuMax < tempMax: tempCpuMax = tempMax
            if "Adapter" in sensorOut[item] and "PCI" in sensorOut[item]:
                contador = 1
                while (len(sensorOut) < (item + contador)) or (len(sensorOut[item + contador].strip()) > 0):
                    if any(word in sensorOut[item + contador] for word in ["Tctl", "Tccd1", "temp1", "loc2"]):
                        if ":" in sensorOut[item + contador].strip():
                            pciTemp = sensorOut[item + contador].strip().split(":")[1]
                            if "(" in pciTemp: 
                                try: pciTemp = float(pciTemp.strip().split("(")[0].strip()[:-2].replace(',', '.').replace("+", ""))
                                except:
                                    pciTemp = -1
                                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in PCI Temperature (1)")
                            else:
                                try: pciTemp = float(pciTemp.strip()[:-2].replace(',', '.').replace("+", ""))
                                except:
                                    pciTemp = -1
                                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in PCI Temperature (2)")
                            if resposta["pciTemp"] < pciTemp: resposta["pciTemp"] = pciTemp
                        critOffset = 1
                        while (len(sensorOut) < (item + contador + critOffset)) or (len(sensorOut[item + contador + critOffset].strip()) > 0):
                            if "crit" in sensorOut[item + contador + critOffset].strip():
                                if "," in sensorOut[item + contador + critOffset].strip(): a = sensorOut[item + contador + critOffset].strip().split(",")
                                for linha in a:
                                    if "crit" in linha:
                                        try: 
                                            pciTempMax = linha.split("crit =")[1][:-2]
                                            pciTempMax = float(pciTempMax.strip().replace(',', '.').replace("+", ""))
                                        except:
                                            pciTempMax = -1
                                            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in PCI Temperature (1)")
                                        if critTemp < pciTempMax: critTemp = pciTempMax
                            critOffset += 1
                    if "power" in sensorOut[item + contador]:
                        pciPwr = sensorOut[item + contador].split(":")
                        try: resposta["pciPower"] = float(pciPwr[1].split("(")[0].strip()[:-1])
                        except: 
                            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in PCI Power")
                        try: 
                            a = pciPwr[1].split("(")[1].strip()
                            if "crit" in a: resposta["pciPowerMax"] = float(a.split("=")[1][:-2])
                        except: 
                            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in PCI Power Max")
                    contador += 1    
            if "Adapter" in sensorOut[item] and "Virtual" in sensorOut[item]:
                contador = 1
                while (len(sensorOut) < (item + contador)) or (len(sensorOut[item + contador].strip()) > 0):
                    if "temp" in sensorOut[item + contador]:
                        try: 
                            mbTemp = float(sensorOut[item + contador].split(":")[1].strip()[:-2].replace(',', '.').replace("+", ""))
                        except: 
                            mbTemp = -1
                            if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in MB Temperature (1)")
                        if resposta["mbTemp"] < mbTemp: resposta["mbTemp"] = mbTemp
                    contador +=1
            if "Vcore" in sensorOut[item]:
                if "mV" in sensorOut[6].split(":")[1].strip(): vtag = "mV"
                else: vtag = "V"
                try: 
                    resposta["vCore"] = float(sensorOut[6].split(":")[1].strip().split(vtag)[0].strip().replace(',', '.'))
                    if vtag == "mV": resposta["vCore"] /= 1000
                except: 
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in vCore voltage")
            if "3.3V" in sensorOut[item]:
                try: resposta["v3.3"] = float(sensorOut[7].split(":")[1].strip().split("V")[0].strip().replace(',', '.'))
                except: 
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in v3.3 voltage")
            if "5V" in sensorOut[item]:
                try: resposta["v5.0"] = float(sensorOut[8].split(":")[1].strip().split("V")[0].strip().replace(',', '.'))
                except: 
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in v5.0 voltage")
            if "12V" in sensorOut[item]:
                try: resposta["v12.0"] = float(sensorOut[9].split(":")[1].strip().split("V")[0].strip().replace(',', '.'))
                except: 
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in v12.0 voltage")
            if "CPU Fan" in sensorOut[item]:
                try: resposta["cpuFanRPM"] = int(sensorOut[10].split(":")[1].strip().split("RPM")[0].strip().replace(',', '.'))
                except: 
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in CPU Fan RPM")
            if "Chassis Fan" in sensorOut[item]:
                try: resposta["chassisFanRPM"] = int(sensorOut[11].split(":")[1].strip().split("RPM")[0].strip().replace(',', '.'))
                except: 
                    if not c.logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-sensor_exec.sensor_metrics: Error in Chassis Fan RPM")
        if tempCpuMax > 0: resposta["cpuTempMax"] = tempCpuMax
        if critTemp > 0: resposta["pciTempMax"] = critTemp
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
