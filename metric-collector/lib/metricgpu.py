#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
versao = "metricgpu-v5.15-PUB-2846410-240225"
###################################################################################################

import logging
import time
from lib import common as c

###################################################################################################
c.versionDict["metricgpu"] = versao
###################################################################################################

class gpu_exec:

    ################################################################################################
    # Função segura para acessar campos do XML
    ################################################################################################
    @staticmethod
    def safe_get(func, default=None, strip_unit=None):
        try:
            v = func()
            if strip_unit and isinstance(v, str):
                v = v.replace(strip_unit, "").strip()
            return v
        except:
            return default

    ################################################################################################
    # Coleta principal
    ################################################################################################
    def collect_gpu(getGpu):
        gpuMetrics = {
            "gpuExecError": 0,
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
            "powerDraw": 0.0,
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
            "powerLimit": 0.0,
            "powerMax": 0.0
        }

        gpuXML = ""
        gpuExecError = 0

        if getGpu:
            if not c.logFirstRun:
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-metricgpu version: {versao}")

            # Tenta obter XML
            try:
                out = c.exec_cmd(["nvidia-smi", "-x", "-q"], c.debugMode, "xml")
                gpuXML = out["output"]["nvidia_smi_log"]
            except Exception as e:
                gpuExecError = 1
                if not c.logFirstRun:
                    logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-SMI XML error: {e}")

        if gpuXML != "":
            gpuMetrics = gpu_exec.gpu_metrics(gpuXML, gpuExecError, c.logFirstRun)

        gpuMetrics["gpuExecError"] = gpuExecError
        return gpuMetrics

    ################################################################################################
    # Processa XML
    ################################################################################################
    def gpu_metrics(data, gpuExecError, logFirstRun):

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
            "powerDraw": 0.0,
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
            "powerLimit": 0.0,
            "powerMax": 0.0
        }

        # Driver / CUDA
        resposta["driver"] = gpu_exec.safe_get(lambda: data["driver_version"]) or ""
        resposta["cuda"]   = gpu_exec.safe_get(lambda: data["cuda_version"]) or ""

        # Node GPU
        gpu = data.get("gpu", {})

        resposta["card"] = gpu_exec.safe_get(lambda: gpu["@id"]) or ""
        resposta["gpuName"] = gpu_exec.safe_get(lambda: gpu["product_name"]) or ""
        resposta["gpuBrand"] = gpu_exec.safe_get(lambda: gpu["product_brand"]) or ""
        resposta["gpuArch"] = gpu_exec.safe_get(lambda: gpu["product_architecture"]) or ""
        resposta["gpuDisplayMode"] = gpu_exec.safe_get(lambda: gpu["display_mode"]) or ""
        resposta["gpuDisplayActive"] = gpu_exec.safe_get(lambda: gpu["display_active"]) or ""
        resposta["multiGpu"] = gpu_exec.safe_get(lambda: gpu["multigpu_board"]) or ""
        resposta["performanceState"] = gpu_exec.safe_get(lambda: gpu["performance_state"]) or ""
        resposta["virtMode"] = gpu_exec.safe_get(
            lambda: gpu["gpu_virtualization_mode"]["virtualization_mode"]) or ""

        # Fan
        resposta["fanSpeed"] = float(gpu_exec.safe_get(lambda: gpu["fan_speed"].split("%")[0]) or 0)

        # Memória FB
        fb = gpu.get("fb_memory_usage", {})
        resposta["memReserved"] = int(gpu_exec.safe_get(lambda: fb["reserved"].split()[0]) or 0)
        resposta["memUsed"]     = int(gpu_exec.safe_get(lambda: fb["used"].split()[0]) or 0)
        resposta["memFree"]     = int(gpu_exec.safe_get(lambda: fb["free"].split()[0]) or 0)
        resposta["memTotal"]    = int(gpu_exec.safe_get(lambda: fb["total"].split()[0]) or 0)

        # Temperatura
        t = gpu.get("temperature", {})
        resposta["temperature"] = float(gpu_exec.safe_get(lambda: t["gpu_temp"], "0C", "C") or 0)
        resposta["tempMax"]     = float(gpu_exec.safe_get(lambda: t["gpu_temp_max_threshold"], "0C", "C") or 0)
        resposta["tempSlowDn"]  = float(gpu_exec.safe_get(lambda: t["gpu_temp_slow_threshold"], "0C", "C") or 0)

        target = gpu.get("supported_gpu_target_temp", {})
        resposta["tempTarget"] = float(gpu_exec.safe_get(lambda: target["gpu_target_temp_max"], "0C", "C") or 0)

        # Power
        p = gpu.get("power_readings", {})

        ###########################################################################
        # POWER DRAW – Fallback automático
        ###########################################################################
        power_val = gpu_exec.safe_get(lambda: p["power_draw"], "").replace("W", "").strip() if "power_draw" in p else ""

        if power_val not in ["", "N/A", "NaN"]:
            try:
                resposta["powerDraw"] = float(power_val)
            except:
                resposta["powerDraw"] = 0.0

        # Se ainda 0 → fallback REAL
        if resposta["powerDraw"] == 0.0:
            try:
                out = c.exec_cmd(
                    ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                    c.debugMode
                )["output"]
                resposta["powerDraw"] = float(out.strip().splitlines()[0])
            except Exception as e:
                if not logFirstRun:
                    logging.error(f"Power Draw fallback error: {e}")
                resposta["powerDraw"] = 0.0

        ###########################################################################
        # POWER LIMIT & MAX LIMIT
        ###########################################################################
        try:
            resposta["powerLimit"] = float(p["power_limit"].replace("W", "").strip())
        except:
            resposta["powerLimit"] = 0.0

        try:
            resposta["powerMax"] = float(p["max_power_limit"].replace("W", "").strip())
        except:
            resposta["powerMax"] = 0.0

        # Utilização
        u = gpu.get("utilization", {})
        resposta["gpuUtil"] = float(gpu_exec.safe_get(lambda: u["gpu_util"].split("%")[0]) or 0)
        resposta["memUtil"] = float(gpu_exec.safe_get(lambda: u["memory_util"].split("%")[0]) or 0)

        return resposta

###################################################################################################
