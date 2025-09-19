#!/usr/bin/env python3
# -*- coding: utf-8 -*-
##################################################################################################
versao = "metric-collector-v5.38-final"
##################################################################################################
import logging
import time
import platform
import psutil   # ✅ para coletar CPU e memória reais
##################################################################################################
def get_metrics(configDict):
    """
    Coleta métricas e retorna dicionário completo com tipos corretos
    para o Pushgateway.
    """
    # Garante chaves essenciais
    for key, default in [("getGpuNvidia", 0), ("getJetson", 0)]:
        configDict.setdefault(key, default)

    # ---- sensorMetrics ----
    sensor_metrics_template = {
        "vCoreMax": 0, "vCore": 0,
        "v3.3Max": 0, "v3.3": 0,
        "v5.0Max": 0, "v5.0": 0,
        "v12.0Max": 0, "v12.0": 0,
        "sensorExecError": 0,
        "chassisFanRpmMax": 0, "chassisFanRPM": 0,
        "cpuFanRpmMax": 0, "cpuFanRPM": 0,
        "pciPowerMax": 0, "pciPower": 0,
        "cpuTempMax": 0, "cpuTemp": 0,
        "mbTempMax": 0, "mbTemp": 0,
        "pciTempMax": 0, "pciTemp": 0
    }

    # ---- serverMetrics ----
    server_metrics_template = {
        "loadAvg1m": 0,
        "loadAvg5m": 0,
        "loadAvg15m": 0,
        "cpuUser": 0,
        "cpuSys": 0,
        "cpuIdle": 0,
        "station_cores": 0,
        "taskTotal": 0,
        "taskSleeping": 0,
        "taskZombie": 0,
        "taskRunning": 0,
        "taskStopped": 0,
        "cpuCores": 0,
        "memFree": 0,
        "memCached": 0,
        "memTotal": 0,
        "memUsed": 0,
        "serverExecError": 0,
        "serverUp": "",
        "servertime": 0,
        "servertimeUTC": 0
    }

    top_metrics_template = {"topExecError": 0}

    resposta = {
        "apiGetMetrics": 0,
        "bkpMetrics": 0,
        "camMetrics": 0,
        "diskMetrics": {"diskDfExecError": 0, "diskExecError": 0},
        "dockerMetrics": 0,
        "gpuMetrics": 0,
        "jetsonMetrics": 0,
        "pingMetrics": [],
        "monOsProcMetrics": [],
        "netMetrics": {"netexecerror": 0},
        "remoteOpenMetrics": 0,
        "selfIpMetrics": [],
        "sensorMetrics": sensor_metrics_template,
        "serverMetrics": server_metrics_template,
        "sysAgentMetrics": 0,
        "topMetrics": top_metrics_template
    }
    collLatency = {}

    # --- GPU / Jetson ---
    if configDict.get("getGpuNvidia", 0) >= 1:
        from lib import metricgpu as gpu
        inicio = time.time()
        resposta["gpuMetrics"] = gpu.gpu_exec.collect_gpu(configDict.get("getGpuNvidia", 0))
        collLatency["gpuMetrics"] = time.time() - inicio
    elif configDict.get("getJetson", 0) >= 1:
        from lib import metricjetson as jet
        inicio = time.time()
        resposta["jetsonMetrics"] = jet.jetson_exec.collect_jetson(configDict.get("getJetson", 0))
        collLatency["jetsonMetrics"] = time.time() - inicio

    # --- Disco ---
    if configDict.get("getDisk", 0):
        from lib import metricdisk as dsk
        inicio = time.time()
        try:
            resposta["diskMetrics"] = dsk.disk_exec.collect_disk(configDict.get("getDisk", 0))
        except Exception as e:
            logging.error(f"Erro na coleta de disco: {e}")
        collLatency["diskMetrics"] = time.time() - inicio

    # --- Ping ---
    if configDict.get("getIpPing", 0):
        from lib import metricping as ip
        inicio = time.time()
        try:
            resposta["pingMetrics"] = ip.ping_exec.collect_ping(
                configDict.get("getIpPing", 0),
                configDict.get("ipPingList", [])
            )
        except Exception as e:
            logging.error(f"Erro na coleta de ping: {e}")
        collLatency["pingMetrics"] = time.time() - inicio

    # --- Monitoração de processos OS ---
    if configDict.get("getMonOsProc", 0):
        from lib import metricmonosproc as mop
        inicio = time.time()
        try:
            resposta["monOsProcMetrics"] = mop.mon_os_proc_exec.collect_mon_os_proc(
                configDict.get("getMonOsProc", 0),
                configDict.get("monitoredOsProcList", [])
            )
        except Exception as e:
            logging.error(f"Erro na coleta MonOsProc: {e}")
        collLatency["monOsProcMetrics"] = time.time() - inicio

    # --- CPU e Memória reais ---
    try:
        # Núcleos
        cores = psutil.cpu_count(logical=True) or 0
        resposta["serverMetrics"]["cpuCores"] = cores
        resposta["serverMetrics"]["station_cores"] = cores

        # Uso CPU
        cpu_times = psutil.cpu_times_percent(interval=1)
        resposta["serverMetrics"]["cpuUser"] = cpu_times.user
        resposta["serverMetrics"]["cpuSys"] = cpu_times.system
        resposta["serverMetrics"]["cpuIdle"] = cpu_times.idle

        # Memória
        vm = psutil.virtual_memory()
        resposta["serverMetrics"]["memTotal"] = round(vm.total / (1024 * 1024))
        resposta["serverMetrics"]["memFree"] = round(vm.available / (1024 * 1024))
        resposta["serverMetrics"]["memUsed"] = round(vm.used / (1024 * 1024))
        resposta["serverMetrics"]["memCached"] = round(getattr(vm, "cached", 0) / (1024 * 1024))
    except Exception as e:
        logging.error(f"Falha ao coletar CPU/Memória: {e}")

    from lib import common as c
    if c.logFirstRun == 0:
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-Latency info: {collLatency}")
    return resposta
##################################################################################################
def get_ntp(configDict):
    from lib import common as c
    cmd = ["grep", "^server", "/etc/ntp.conf"]
    ntp = c.exec_cmd(cmd, 0)
    if ntp["returnCode"] == 0:
        for svr in ntp["output"].splitlines():
            parts = svr.split()
            if len(parts) > 1 and "." in parts[1]:
                configDict.setdefault("ntpServerList", []).append(parts[1])
                configDict["ntpStatus"] = 1
    cmd = ["ntpstat"]
    ntp = c.exec_cmd(cmd, 0)
    if ntp["returnCode"] == 0:
        for line in ntp["output"].splitlines():
            if "(" in line:
                configDict["ntpIp"] = line.split("(", 1)[1].split(")")[0]
##################################################################################################
if __name__ == "__main__":
    from datetime import datetime
    from lib import common as c
    from lib import metricconfig as mc
    from lib import pushtogateway as pg
    from lib import versioncontrol as vc

    c.versionDict["metric-collector"] = versao
    configDict = mc.config_setup.get_config()

    # --- Auto detectar arquitetura ---
    raw_gpu = configDict.get("getGpu")
    if raw_gpu is None and "gpu" in configDict:
        val = configDict["gpu"]
        raw_gpu = 1 if val is True else int(val) if isinstance(val, (int, str)) else 0
        configDict["getGpu"] = raw_gpu
    cpu_arch = configDict.get("cpuArch")
    if not cpu_arch or cpu_arch.lower() == "invalid":
        cpu_arch = platform.machine()
    configDict["cpuArch"] = cpu_arch

    # --- Definir flags GPU ---
    if configDict.get("getGpu", 0):
        if cpu_arch == "x86_64":
            configDict["getGpuNvidia"] = configDict["getGpu"]
            configDict["getJetson"] = 0
        elif cpu_arch == "aarch64":
            configDict["getGpuNvidia"] = 0
            configDict["getJetson"] = configDict["getGpu"]
        else:
            configDict["getGpuNvidia"] = 0
            configDict["getJetson"] = 0
    else:
        configDict["getGpuNvidia"] = 0
        configDict["getJetson"] = 0

    logging.basicConfig(filename=c.logPath + c.logFileName, level=logging.DEBUG, force=True)
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-Metric Method: {configDict.get('metricMethod')}")
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-GPU flags: getGpu={configDict.get('getGpu')} "
                 f"getGpuNvidia={configDict.get('getGpuNvidia')} getJetson={configDict.get('getJetson')} "
                 f"cpuArch={configDict.get('cpuArch')}")

    # --- Loop principal ---
    if configDict.get('metricMethod') == "push":
        vc.version_update.export_actual(configDict)
        while True:
            get_ntp(configDict)
            metrics = get_metrics(configDict)
            configDict.setdefault("getGpuNvidia", 0)
            configDict.setdefault("getJetson", 0)
            basic = pg.push_data(configDict, metrics)
            basic.set_data()
            basic.push_to_gateway()
            basic.clean_prom()
            time.sleep(configDict.get("captureInterval", 60))
    else:
        from prometheus_client import start_http_server
        from lib import metricexporter as me
        start_http_server(int(configDict.get("exporterPort", 9089)))
        basic = me.exporter(configDict)
        updTime = datetime.timestamp(datetime.now())
        vc.version_update.export_actual(configDict)
        while True:
            get_ntp(configDict)
            basic.metricDict = get_metrics(configDict)
            me.exporter.clean_prom(basic)
            me.exporter.set_data(basic)
            if updTime + 300 < datetime.timestamp(datetime.now()):
                if configDict.get("autoUpdate"):
                    vc.version_update.export_actual(configDict)
                updTime = datetime.timestamp(datetime.now())
            if not c.logFirstRun:
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-version dictionary: {c.versionDict}")
            c.logFirstRun = 1
            time.sleep(configDict.get("captureInterval", 60))
##################################################################################################

