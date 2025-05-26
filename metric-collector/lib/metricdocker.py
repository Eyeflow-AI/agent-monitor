#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricdocker-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricdocker"] = versao
#######################################################################################################################
class docker_exec:
    # Execute docker metric collector
    def collect_docker(getDocker, dockerList, dockerExceptList):
        resposta, dockerout, dockerExecError = {}, 0, 0
        if getDocker:
            if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricdocker version: {versao}")
            try: dockerout = c.exec_cmd(["docker", "ps", "--no-trunc"], c.debugMode)["output"].splitlines()
            except: 
                if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-docker_exec.collect_docker: Docker execution error")
                dockerExecError = 1
        if len(dockerout) > 1:
            if len(dockerout) > 0: resposta = docker_exec.docker_metrics(dockerout)
            if resposta != 0:
                if "all" not in dockerList:
                    validResp = {}
                    validCount = 0
                    for element in resposta:
                        for keyword in dockerList:
                            if keyword in resposta[element]["names"]:
                                validResp[validCount] = resposta[element]
                                validCount += 1
                    resposta = validResp
                if len(dockerExceptList) > 0:
                    validResp = {}
                    validCount = 0
                    for element in resposta:
                        for keyword in dockerExceptList:
                            if keyword not in resposta[element]["names"]:
                                validResp[validCount] = resposta[element]
                                validCount += 1
                    resposta = validResp
        resposta["dockerExecError"] = dockerExecError
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def docker_metrics(dockerout):
        resposta = {}
        if len(dockerout) > 1:
            keyList = dockerout[0].split("  ")
            keyList = [keyName.lower().strip() for keyName in keyList if keyName != ""]
            for element in range(1, len(dockerout)):
                imgData = {}
                tmp1 = dockerout[element].split("  ")
                tmp1 = [nameOut.lower().strip().replace('"','') for nameOut in tmp1 if nameOut != ""]
                if len(tmp1) < 7:
                    tmp1.append(tmp1[-1])
                    tmp1[-2] = ""
                try: indx = keyList.index("image")
                except: imgData["image"] = ""
                else: imgData["image"] = tmp1[indx]
                try: indx = keyList.index("command")
                except: imgData["command"] = ""
                else: imgData["command"] = tmp1[indx]
                try: indx = keyList.index("created")
                except: imgData["created"] = ""
                else: imgData["created"] = docker_exec.convert_texttime(tmp1[indx].split())
                try: indx = keyList.index("status")
                except: 
                    imgData["status"] = ""
                    imgData["statusTime"] = 0
                else:
                    statusList = tmp1[indx].split()
                    imgData["status"] = statusList[0].lower()
                    statusAge = statusList[1:]
                    statusAge.append("ago")
                    imgData["statusTime"] = docker_exec.convert_texttime(statusAge)
                try: indx = keyList.index("ports")
                except: imgData["ports"] = ""
                else: imgData["ports"] = tmp1[indx]
                try: indx = keyList.index("names")
                except: imgData["names"] = ""
                else: imgData["names"] = tmp1[indx]
                resposta[element - 1] = imgData
        else: resposta = 0
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def convert_texttime(textdata):
        if len(textdata) == 3:
            if textdata[0].isdigit(): createdData = int(textdata[0])
            createdData *= docker_exec.get_multiplier(textdata)
        elif len(textdata) > 3:
            for n in range(len(textdata)):
                if textdata[n].isdigit(): createdData = int(textdata[n])
                elif textdata[n] == "a" or textdata[n] == "an": createdData = 1
            createdData *= docker_exec.get_multiplier(textdata)
        return createdData
        #----------------------------------------------------------------------------------------------------------------------
    def get_multiplier(textdata):
        createdData = 0
        if textdata[-1] == "ago" and textdata[-2] == "ago": textdata = textdata[:-1]
        if textdata[-1] == "ago":
            if "second" in textdata[-2]: createdData = 1
            if "minute" in textdata[-2]: createdData = 60
            if "hour" in textdata[-2]: createdData = 60 * 60
            if "day" in textdata[-2]: createdData = 60 * 60 * 24
            if "week" in textdata[-2]: createdData = 60 * 60 * 24 * 7
            if "month" in textdata[-2]: createdData = 60 * 60 * 24 * 30
            if "year" in textdata[-2]: createdData = 60 * 60 * 24 * 365
        return createdData
        #----------------------------------------------------------------------------------------------------------------------
