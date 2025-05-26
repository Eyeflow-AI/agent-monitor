#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricgpu-v5.10-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricgpu"] = versao
#######################################################################################################################
class gpu_exec:
    # Execute Nvidia GPU metric collector
    def collect_gpu(getGpu):
        gpuMetrics = {"gpuExecError":0,
            "card": "",
            "driver": "",
            "cuda": "",
            "gpuName": "",
            "multiGpu": "",
            "performanceState": "",
            "virtMode": "",
            "memTotal": 0,
            "gpuUtil": 0,
            "memUtil": 0,
            "powerDraw": 0,
            "temperature": 0,
            "gpuBrand": "",
            "gpuArch": "",
            "gpuDisplayMode": "",
            "gpuDisplayActive": "",
            "fanSpeed": 0,
            "memReserved": 0,
            "memUsed": 0,
            "memFree": 0,
            "tempMax": 0,
            "tempSlowDn": 0,
            "tempTarget": 0,
            "powerLimit": 0,
            "powerMax": 0}
        gpuout, gpuExecError = "", 0
        if getGpu:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricgpu version: {versao}")
            try: 
                gpuout = c.exec_cmd(["nvidia-smi", "-x", "-q"], c.debugMode, "xml")["output"]["nvidia_smi_log"]
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-gpu_exec.collect_gpu: SMI execution error")
                gpuExecError = 1
        if gpuout != "": gpuMetrics = gpu_exec.gpu_metrics(gpuout, gpuExecError, c.logFirstRun)
        gpuMetrics["gpuExecError"] = gpuExecError
        return gpuMetrics
        #----------------------------------------------------------------------------------------------------------------------
    def gpu_metrics(gpuData, gpuExecError, logFirstRun):
        resposta = {
            "gpuExecError": gpuExecError,
            "card": "",
            "driver": "",
            "cuda": "",
            "gpuName": "",
            "multiGpu": "",
            "performanceState": "",
            "virtMode": "",
            "memTotal": 0,
            "gpuUtil": 0,
            "memUtil": 0,
            "powerDraw": 0,
            "temperature": 0,
            "gpuBrand": "",
            "gpuArch": "",
            "gpuDisplayMode": "",
            "gpuDisplayActive": "",
            "fanSpeed": 0,
            "memReserved": 0,
            "memUsed": 0,
            "memFree": 0,
            "tempMax": 0,
            "tempSlowDn": 0,
            "tempTarget": 0,
            "powerLimit": 0,
            "powerMax": 0}
        try: cardName = c.exec_cmd(["nvidia-smi", "-L"], c.debugMode)["output"]
        except:
            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-gpu_exec.gpu_metrics: SMI list card error")
            resposta["gpuExecError"] = 1
        else:
            resposta["gpuExecError"] = 0
            try: resposta["card"] = str(gpuData["gpu"]["@id"])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Card info")
            try: resposta["driver"] = gpuData["driver_version"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No driver info")
            try: resposta["cuda"] = gpuData["cuda_version"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No CUDA info")
            gpuData = gpuData["gpu"]
            try: resposta["gpuName"] = gpuData["product_name"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Product Name info")
            try: resposta["gpuBrand"] = gpuData["product_brand"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Product Brand info")
            try: resposta["gpuArch"] = gpuData["product_architecture"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Product Architecture info")
            try: resposta["gpuDisplayMode"] = gpuData["display_mode"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Display Mode info")
            try: resposta["gpuDisplayActive"] = gpuData["display_active"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Display Active info")
            try: resposta["fanSpeed"] = float(gpuData["fan_speed"].split("%")[0].strip())
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Fan Speed info")
            try: resposta["memReserved"] = int(gpuData["fb_memory_usage"]["reserved"].split()[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No FB Reserved Memory info")
            try: resposta["memUsed"] = int(gpuData["fb_memory_usage"]["used"].split()[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No FB Used Memory info")
            try: resposta["memFree"] = int(gpuData["fb_memory_usage"]["free"].split()[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No FB Free Memory info")
            try: resposta["tempMax"] = float(gpuData["temperature"]["gpu_temp_max_threshold"].split("C")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Temperature Max Tres info")
            try: resposta["tempSlowDn"] = float(gpuData["temperature"]["gpu_temp_slow_threshold"].split("C")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Temperature Slow Tres info")
            try: resposta["tempTarget"] = float(gpuData["supported_gpu_target_temp"]["gpu_target_temp_max"].split("C")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Temperature Target info")
            try: resposta["powerLimit"] = float(gpuData["power_readings"]["power_limit"].split("W")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Power Limit info")
            try: resposta["powerMax"] = float(gpuData["power_readings"]["max_power_limit"].split("W")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Max Power Limit info")
            try: resposta["multiGpu"] = gpuData["multigpu_board"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Multi-GPU info")
            try: resposta["performanceState"] = gpuData["performance_state"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Performance State info")
            try: resposta["virtMode"] = gpuData["gpu_virtualization_mode"]["virtualization_mode"]
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Virtualization Mode info")
            try: resposta["memTotal"] = int(gpuData["fb_memory_usage"]["total"].split()[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No Total Memory info")
            try: resposta["gpuUtil"] = float(gpuData["utilization"]["gpu_util"].split("%")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Utilization info")
            try: resposta["memUtil"] = float(gpuData["utilization"]["memory_util"].split("%")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Memory Utilization info")
            try: resposta["powerDraw"] = float(gpuData["power_readings"]["power_draw"].split("W")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Power Draw info")
            try: resposta["temperature"] = float(gpuData["temperature"]["gpu_temp"].split("C")[0])
            except: 
                if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No GPU Temperature info")
            if not logFirstRun: logging.warning(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-GPU Metrics: No NVIDIA-SMI app")
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
