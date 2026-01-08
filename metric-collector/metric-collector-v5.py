#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
versao = "metric-collector-v5.15-PUB-2846410-240226"
###################################################################################################

import logging
import time
from datetime import datetime
from lib import common as c
from lib import metricconfig as mc
from lib import versioncontrol as vc
from lib import pushtogateway as pg

###################################################################################################
c.versionDict["metric-collector"] = versao
###################################################################################################

# ================================================================================================
# FUNÇÃO PRINCIPAL DE COLETA
# ================================================================================================
def get_metrics(configDict):
    resposta = {
        "apiGetMetrics": 0,
        "bkpMetrics": 0,
        "camMetrics": 0,
        "diskMetrics": 0,
        "dockerMetrics": 0,
        "gpuMetrics": 0,
        "jetsonMetrics": 0,
        "pingMetrics": 0,
        "monOsProcMetrics": 0,
        "netMetrics": 0,
        "remoteOpenMetrics": 0,
        "selfIpMetrics": 0,
        "sensorMetrics": 0,
        "serverMetrics": 0,
        "sysAgentMetrics": 0,
        "topMetrics": 0
    }

    collLatency = {k: 0 for k in resposta}

    # ---------------------------------------------
    # MÉTRICAS DE REDE (PRÉ E PÓS)
    # ---------------------------------------------
    if configDict["getNetwork"]:
        from lib import metricnet as mn
        net1 = mn.net_exec.get_net()
        net1start = time.time()

    # ---------------------------------------------
    # API GET
    # ---------------------------------------------
    if configDict["getApiGet"]:
        inicio = time.time()
        from lib import metricapiget as ag
        resposta["apiGetMetrics"] = ag.apiget_exec.collect_apiget(
            configDict["getApiGet"], configDict["apiUrl"])
        collLatency["apiGetMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # BACKUP
    # ---------------------------------------------
    if configDict["getBackup"]:
        inicio = time.time()
        from lib import metricbackup as bkp
        resposta["bkpMetrics"] = bkp.backup_exec.collect_backup(
            configDict["getBackup"],
            configDict["backupFolder"],
            configDict["backupPrefix"],
            configDict["backupSuffix"],
            configDict["backupFrequency"])
        collLatency["bkpMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # CÂMERAS
    # ---------------------------------------------
    if configDict["getCam"]:
        inicio = time.time()
        from lib import metriccam as cam
        resposta["camMetrics"] = cam.cam_exec.collect_cam(
            configDict["getCam"], configDict["camUrl"], configDict["camRestart"])
        collLatency["camMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # DISK
    # ---------------------------------------------
    if configDict["getDisk"]:
        inicio = time.time()
        from lib import metricdisk as dsk
        resposta["diskMetrics"] = dsk.disk_exec.collect_disk(configDict["getDisk"])
        collLatency["diskMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # DOCKER
    # ---------------------------------------------
    if configDict["getDocker"]:
        inicio = time.time()
        from lib import metricdocker as dock
        retorno = dock.docker_exec.collect_docker(
            configDict["getDocker"],
            configDict["dockerList"],
            configDict["dockerExceptList"])
        resposta["dockerMetrics"] = retorno
        collLatency["dockerMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # GPU / JETSON
    # ---------------------------------------------
    if configDict["getGpuNvidia"] >= 1:
        inicio = time.time()
        from lib import metricgpu as gpu
        resposta["gpuMetrics"] = gpu.gpu_exec.collect_gpu(configDict["getGpuNvidia"])
        resposta["jetsonMetrics"] = 0
        collLatency["gpuMetrics"] = time.time() - inicio

    elif configDict["getJetson"] >= 1:
        inicio = time.time()
        from lib import metricjetson as jet
        resposta["jetsonMetrics"] = jet.jetson_exec.collect_jetson(configDict["getJetson"])
        resposta["gpuMetrics"] = 0
        collLatency["gpuMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # PING
    # ---------------------------------------------
    if configDict["getIpPing"]:
        inicio = time.time()
        from lib import metricping as ip
        resposta["pingMetrics"] = ip.ping_exec.collect_ping(
            configDict["getIpPing"], configDict["ipPingList"])
        collLatency["pingMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # PROCESSOS OS
    # ---------------------------------------------
    if configDict["getMonOsProc"]:
        inicio = time.time()
        from lib import metricmonosproc as mop
        resposta["monOsProcMetrics"] = mop.mon_os_proc_exec.collect_mon_os_proc(
            configDict["getMonOsProc"], configDict["monitoredOsProcList"])
        collLatency["monOsProcMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # ARQUIVOS REMOTOS
    # ---------------------------------------------
    if configDict["getRemoteOpen"]:
        inicio = time.time()
        from lib import metricremote as mr
        resposta["remoteOpenMetrics"] = mr.remote_open_exec.collect_remote_open(
            configDict["getRemoteOpen"], configDict["remoteOpenList"])
        collLatency["remoteOpenMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # SELF IP
    # ---------------------------------------------
    if configDict["getSelfIp"]:
        inicio = time.time()
        from lib import metricnet as mnet
        resposta["selfIpMetrics"] = mnet.net_exec.collect_selfip(
            configDict["getSelfIp"], configDict["stationIpList"])
        collLatency["selfIpMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # SENSOR
    # ---------------------------------------------
    if configDict["getSensor"]:
        inicio = time.time()
        from lib import metricsensor as sensor
        resposta["sensorMetrics"] = sensor.sensor_exec.collect_sensor(configDict["getSensor"])
        collLatency["sensorMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # SERVER
    # ---------------------------------------------
    if configDict["getServer"]:
        inicio = time.time()
        from lib import metricserver as srv
        resposta["serverMetrics"] = srv.server_exec.collect_server(configDict["getServer"])
        collLatency["serverMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # SYSAGENT
    # ---------------------------------------------
    if configDict["getSysAgent"]:
        inicio = time.time()
        from lib import metricsysagent as sa
        resposta["sysAgentMetrics"] = sa.sys_agent_exec.collect_sys_agent(
            configDict["getSysAgent"], configDict["sysAgentRestart"])
        collLatency["sysAgentMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # TOP PROCESS
    # ---------------------------------------------
    if configDict["getTopProcess"]:
        inicio = time.time()
        from lib import metrictop as mtop
        resposta["topMetrics"] = mtop.top_exec.collect_top(
            configDict["getTopProcess"], configDict["topOsProcessCount"])
        collLatency["topMetrics"] = time.time() - inicio

    # ---------------------------------------------
    # REDE (diferença)
    # ---------------------------------------------
    if configDict["getNetwork"]:
        net2 = mn.net_exec.get_net()
        netInterval = time.time() - net1start
        resposta["netMetrics"] = mn.net_exec.net_metrics(net1, net2, netInterval)

    if c.logFirstRun == 0:
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-main.get_metrics: Latency info: {collLatency}")

    return resposta

###################################################################################################
# NTP
###################################################################################################
def get_ntp(configDict):
    cmd = ["grep", "^server", "/etc/ntp.conf"]
    ntp = c.exec_cmd(cmd, 0)
    if ntp["returnCode"] == 0:
        ntp = ntp["output"].splitlines()
        for srv in ntp:
            s = srv.split()
            if "." in s[1]:
                configDict["ntpServerList"].append(s[1])
            configDict["ntpStatus"] = 1

    cmd = ["ntpstat"]
    ntp = c.exec_cmd(cmd, 0)
    if ntp["returnCode"] == 0:
        ntp = ntp["output"].splitlines()
        for srv in ntp:
            if "(" in srv:
                configDict["ntpIp"] = srv.split("(")[1].split(")")[0]

    return

###################################################################################################
# Main 
if __name__ == "__main__":
    import time
    from datetime import datetime
    from lib import common as c
    from lib import metricconfig as mc
    from lib import pushtogateway as pg
    from lib import versioncontrol as vc
    c.versionDict["metric-collector"] = versao
    configDict = mc.config_setup.get_config()
    if configDict["getGpu"]:
        if configDict["cpuArch"] == "x86_64":
            configDict["getGpuNvidia"] = configDict["getGpu"]
            configDict["getJetson"] = 0
        elif configDict["cpuArch"] == "aarch64":
            configDict["getGpuNvidia"] = 0
            configDict["getJetson"] = configDict["getGpu"]
    else:
        configDict["getGpuNvidia"] = 0
        configDict["getJetson"] = 0
    logging.basicConfig(filename = c.logPath + c.logFileName, level=logging.DEBUG, force=True)
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Metric Method: {configDict['metricMethod']}")
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-update config: {configDict['autoUpdate']}")
    del mc
    if configDict['metricMethod'] == "push":
        vc.version_update.export_actual(configDict)
        while True:
            get_ntp(configDict)
            metrics = get_metrics(configDict)
            basic = pg.push_data(configDict, metrics)
            basic.set_data()
            basic.push_to_gateway()
            basic.clean_prom()
#            if updTime + 300 < datetime.timestamp(datetime.now()):
#                if configDict["autoUpdate"]:
#                    apiStatus = vc.version_update.export_actual(configDict)
#                    if apiStatus != 200: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Main-Export Actual Error: {apiStatus}")
#                    vc.version_update.check_outdated(configDict)
#                updTime = datetime.timestamp(datetime.now())
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version dictionary: {c.versionDict}")
            c.logFirstRun = 1
            time.sleep(configDict["captureInterval"])
    else:
        from prometheus_client import start_http_server
        from lib import metricexporter as me
        start_http_server(9089)
        basic = me.exporter(configDict)
        updTime = datetime.timestamp(datetime.now())
        vc.version_update.export_actual(configDict)
        while True:
            get_ntp(configDict)
            basic.metricDict = get_metrics(configDict)
            me.exporter.clean_prom(basic)
            me.exporter.set_data(basic)
            if updTime + 300 < datetime.timestamp(datetime.now()):
                if configDict["autoUpdate"]:
                    apiStatus = vc.version_update.export_actual(configDict)
                    if apiStatus != 200: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-Main-Export Actual Error: {apiStatus}")
                    vc.version_update.check_outdated(configDict)
                updTime = datetime.timestamp(datetime.now())
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version dictionary: {c.versionDict}")
            c.logFirstRun = 1
            time.sleep(configDict["captureInterval"])
#######################################################################################################################
