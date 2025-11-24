#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
versao = "metricgpu-v5.16-PUB-2846410-240226"
###################################################################################################

import logging
import time
from lib import common as c

###################################################################################################
c.versionDict["metricgpu"] = versao
###################################################################################################

class gpu_exec:

    ################################################################################################
    # Função segura para leitura de valores com limpeza de unidade
    ################################################################################################
    @staticmethod
    def to_float(val, unit=None):
        """
        Converte string para float removendo unidade (W, C, %, MB)
        Aceita:
            "95.29 W"
            " 95.29 "
            "95.29C"
            "N/A"
            ""
        Se falhar, retorna 0.0
        """
        try:
            if val is None:
                return 0.0
            if not isinstance(val, str):
                return float(val)

            clean = val.strip()
            if unit:
                clean = clean.replace(unit, "")
            clean = clean.replace("C", "").replace("W", "").replace("%", "").strip()

            if clean in ["", "N/A", "NaN"]:
                return 0.0

            return float(clean)
        except:
            return 0.0

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

        # ==========================================================================================
        # Captura XML principal
        # ==========================================================================================
        if getGpu:
            if not c.logFirstRun:
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-metricgpu version: {versao}")

            try:
                out = c.exec_cmd(["nvidia-smi", "-x", "-q"], c.debugMode, "xml")
                gpuXML = out["output"]["nvidia_smi_log"]
            except Exception as e:
                gpuExecError = 1
                if not c.logFirstRun:
                    logging.error(f"[metricgpu] Erro XML nvidia-smi: {e}")

        if gpuXML != "":
            gpuMetrics = gpu_exec.gpu_metrics(gpuXML, gpuExecError, c.logFirstRun)

        gpuMetrics["gpuExecError"] = gpuExecError
        return gpuMetrics

    ################################################################################################
    # Parser XML → Dicionário final de métricas
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

        # ------------------------------------
        # DRIVER / CUDA
        # ------------------------------------
        resposta["driver"] = data.get("driver_version", "")
        resposta["cuda"]   = data.get("cuda_version", "")

        gpu = data.get("gpu", {})

        # ------------------------------------
        # INFOS PRINCIPAIS
        # ------------------------------------
        resposta["card"] = gpu.get("@id", "")
        resposta["gpuName"] = gpu.get("product_name", "")
        resposta["gpuBrand"] = gpu.get("product_brand", "")
        resposta["gpuArch"] = gpu.get("product_architecture", "")
        resposta["gpuDisplayMode"] = gpu.get("display_mode", "")
        resposta["gpuDisplayActive"] = gpu.get("display_active", "")
        resposta["multiGpu"] = gpu.get("multigpu_board", "")
        resposta["performanceState"] = gpu.get("performance_state", "")

        # Virtualização
        try:
            resposta["virtMode"] = gpu["gpu_virtualization_mode"]["virtualization_mode"]
        except:
            resposta["virtMode"] = ""

        # ------------------------------------
        # FAN SPEED
        # ------------------------------------
        resposta["fanSpeed"] = gpu_exec.to_float(gpu.get("fan_speed", "0%"))

        # ------------------------------------
        # MEMÓRIA FB
        # ------------------------------------
        fb = gpu.get("fb_memory_usage", {})
        resposta["memReserved"] = gpu_exec.to_float(fb.get("reserved", "0MB"))
        resposta["memUsed"]     = gpu_exec.to_float(fb.get("used", "0MB"))
        resposta["memFree"]     = gpu_exec.to_float(fb.get("free", "0MB"))
        resposta["memTotal"]    = gpu_exec.to_float(fb.get("total", "0MB"))

        # ------------------------------------
        # TEMPERATURAS
        # ------------------------------------
        t = gpu.get("temperature", {})

        resposta["temperature"] = gpu_exec.to_float(t.get("gpu_temp", "0C"))
        resposta["tempMax"]     = gpu_exec.to_float(t.get("gpu_temp_max_threshold", "0C"))
        resposta["tempSlowDn"]  = gpu_exec.to_float(t.get("gpu_temp_slow_threshold", "0C"))

        target = gpu.get("supported_gpu_target_temp", {})
        resposta["tempTarget"]  = gpu_exec.to_float(target.get("gpu_target_temp_max", "0C"))

        # ------------------------------------
        # UTILIZAÇÃO
        # ------------------------------------
        u = gpu.get("utilization", {})
        resposta["gpuUtil"] = gpu_exec.to_float(u.get("gpu_util", "0%"))
        resposta["memUtil"] = gpu_exec.to_float(u.get("memory_util", "0%"))

        # ------------------------------------
        # POWER (PRINCIPAL)
        # ------------------------------------
        p = gpu.get("power_readings", {})

        # XML → float
        resposta["powerDraw"] = gpu_exec.to_float(p.get("power_draw", "0W"))
        resposta["powerLimit"] = gpu_exec.to_float(p.get("power_limit", "0W"))
        resposta["powerMax"] = gpu_exec.to_float(p.get("max_power_limit", "0W"))

        # ------------------------------------
        # FALLBACK SE inner XML FALHAR EM powerDraw
        # ------------------------------------
        if resposta["powerDraw"] == 0.0:
            try:
                out = c.exec_cmd(
                    ["nvidia-smi", "--query-gpu=power.draw", "--format=csv,noheader,nounits"],
                    c.debugMode
                )["output"]
                resposta["powerDraw"] = float(out.strip().splitlines()[0])
            except Exception as e:
                if not logFirstRun:
                    logging.error(f"[metricgpu] Fallback powerDraw error: {e}")
                resposta["powerDraw"] = 0.0

        return resposta

###################################################################################################
