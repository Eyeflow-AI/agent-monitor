#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "common-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import subprocess
import time
#######################################################################################################################
# logFileName: Default log file name. Typically 'monitoring.log'
#   log file will be saved to 'path/logPath' defined in configuration file or defaults to './'
# logFirstRun: Run debug logs once
# debugMode: Default debug mode (false)
#######################################################################################################################
__all__ = [
    "configFileName", 
    "logPath",
    "logFileName", 
    "scriptPath",
    "logFirstRun", 
    "debugMode", 
    "cameraCount", 
    "sysAgentCount", 
    "versionDict", 
    "updateList", 
    "updateRepo"]
configFileName = "collector-config-v5.yaml"
logFileName = "monitoring-v5.log"
logPath = "./"
scriptPath = "./"
logFirstRun = 0
debugMode = 0
cameraCount = 0
sysAgentCount = 0
versionDict = {}
updateList = []
updateRepo = ""
versionDict["common"] = versao
#######################################################################################################################
def exec_cmd(command, debugMode, outFormat = "text"):
    if outFormat != "text": import xmltodict
    resposta = {}
    if debugMode: logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-exec_cmd: {command}")
    try: result = subprocess.run(command, universal_newlines= True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as resulterror:
        logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-exec_cmd: {resulterror}")
        resposta["returnCode"] = resulterror.returncode
        resposta["output"] = resulterror.stdout
        resposta["errorOutput"] = resulterror.stderr
        resposta["version"] = versao
    else:
        resposta["returnCode"] = result.returncode
        resposta["errorOutput"] = result.stderr
        if result.returncode != 0: resposta["output"] = result.stdout
        else:
            if outFormat == "xml": resposta["output"] = xmltodict.parse(result.stdout)
            else: resposta["output"] = result.stdout
    return resposta
#######################################################################################################################
# Executa comando no OS com pipe
def exec_pipe(command1, command2, outFormat = "filt"):
    resposta = {}
    try:
        result1 = subprocess.Popen(command1, stdout=subprocess.PIPE)
        result2 = subprocess.Popen(command2, stdin=result1.stdout, stdout=subprocess.PIPE)
    except subprocess.CalledProcessError as resulterror:
        logging.debug(f"Error at exec_pipe: {resulterror}")
        resposta["returnCode"] = resulterror.returncode
        resposta["output"] = resulterror.stdout
        resposta["errorOutput"] = resulterror.stderr
        resposta["version"] = versao
    else:
        if outFormat.lower() == "raw":
            for s in (str(result2.communicate())[3:-10]).split('\\n'):
                resposta["output"] = s
            resposta["returnCode"] = result2.returncode
            resposta["errorOutput"]  = result2.stderr
        else:
            for s in (str(result2.communicate())[3:-10]).split('\\n'): pscount = int(s)
            resposta["returnCode"] = result2.returncode
            if result2.returncode != 0:
                resposta["output"] = result2.stdout
                resposta["errorOutput"]  = result2.stderr
            else:
                resposta["output"] = pscount
                resposta["errorOutput"] = result2.stderr
            del result1, result2
    return resposta
#######################################################################################################################
