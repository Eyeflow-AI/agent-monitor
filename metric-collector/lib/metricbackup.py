#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricbackup-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricbackup"] = versao
#######################################################################################################################
class backup_exec: 
    def collect_backup(getBkp, bkpFolder, bkpPrefix, bkpSuffix, bkpFreq):
        execerror = 0
        resposta = {}
        if getBkp:
            if bkpFolder != None:
                if (len(bkpFolder) > 0):
                    if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metricbackup version: {versao}")
                    try: backupFiles = c.exec_cmd(["ls", "-lt", bkpFolder], c.debugMode)["output"].splitlines()
                    except: 
                        if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-backup_exec.collect_backup: List dir execution error")
                        execerror = 1
                    else:
                        backupout = {}
                        item = 0
                        for element in backupFiles:
                            fileStat = ""
                            checkPre, checkSuf = False, False
                            fileData = element.split()
                            if len(fileData) > 8:
                                if fileData[0][0] == "d": fileType = "dir"
                                else: fileType = "file"
                                if bkpFolder[-1] == "/": statName = bkpFolder + fileData[-1]
                                else: statName = bkpFolder + "/" + fileData[-1]
                                if bkpPrefix == "" or bkpPrefix == None: checkPre = True
                                else:
                                    if bkpPrefix in fileData[-1]: checkPre = True
                                if bkpSuffix == "" or bkpSuffix == None: checkSuf = True
                                else:
                                    if bkpSuffix in fileData[-1]: checkSuf = True
                                if checkPre and checkSuf:
                                    try: fileStat = c.exec_cmd(["stat", statName], c.debugMode)["output"].splitlines()
                                    except:
                                        if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-backup_exec.collect_backup: stat file execution error")
                                        execerror = 1
                                    backupout[item] = {
                                        "name": fileData[-1], 
                                        "path": bkpFolder,
                                        "type": fileType, 
                                        "access": fileStat[4].split(":", 1)[1].strip(),
                                        "modified": fileStat[5].split(":", 1)[1].strip(),
                                        "frequency": bkpFreq}
                                    item += 1
                    if len(backupout) > 0: resposta.update(backup_exec.backup_metrics(backupout))
        resposta["backupExecError"] = execerror
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    def backup_metrics(backupout):
        resposta = {}
        if len(backupout) > 0:
            item = 0
            for element in range(len(backupout)):
                try: fileItem = {
                    "status": 1,
                    "name": backupout[element]["name"],
                    "path": backupout[element]["path"],
                    "type": backupout[element]["type"],
                    "access": time.mktime(time.strptime(backupout[element]["access"][:19], "%Y-%m-%d %H:%M:%S")),
                    "modified": time.mktime(time.strptime(backupout[element]["modified"][:19], "%Y-%m-%d %H:%M:%S")),
                    "expire_in": time.mktime(time.strptime(backupout[element]["modified"][:19], "%Y-%m-%d %H:%M:%S")) + 
                        backup_exec.convert_frequency(backupout[element]["frequency"])}
                except: fileItem = {
                    "status": 0,
                    "name": backupout[element]["name"],
                    "path": backupout[element]["path"],
                    "type": backupout[element]["type"],
                    "access": 0,
                    "modified": 0,
                    "expire_in": 0}
                resposta[item] = fileItem
                item += 1
        return resposta                    
        #----------------------------------------------------------------------------------------------------------------------
    def convert_frequency(bkpFreq):
        if bkpFreq[-1] == "m" or bkpFreq[-1] == "M": mult = 30 * 24 * 60 * 60
        elif bkpFreq[-1] == "d" or bkpFreq[-1] == "D": mult = 24 * 60 * 60
        elif bkpFreq[-1] == "h" or bkpFreq[-1] == "H": mult = 60 * 60
        else: mult = 1
        freqTS = mult
        if len(bkpFreq) > 1:
            if bkpFreq[:-1].isnumeric(): freqTS = int(bkpFreq[:-1]) * mult
        return freqTS
        #----------------------------------------------------------------------------------------------------------------------
