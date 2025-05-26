#!/usr/bin/env python3
# -*- coding: utf-8 -*-
###################################################################################################
versao = "metric-updater-v1.03-20231027-1732"
###################################################################################################
import os
import time
import json
import logging
import requests
###################################################################################################
class service_action:
    def check_status():
        status = "error"
        for line in os.popen("systemctl status metric-collector.service"):
            if line.strip().startswith("Active:"): 
                if "active (running)" in line: status = "active"
                if "inactive (dead)" in line: status = "stopped"
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: Metric service status: {status}")
        return status
    #----------------------------------------------------------------------------------------------
    def stop_service():
        os.popen("systemctl stop metric-collector.service")
        time.sleep(.5)
        status = service_action.check_status()
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: Stop service status: {status}")
        return status
    #----------------------------------------------------------------------------------------------
    def start_service():
        os.popen("systemctl start metric-collector.service")
        time.sleep(.5)
        status = service_action.check_status()
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: Start service status: {status}")
        return status
###################################################################################################
class updater:
    def __init__(self) -> None:
        self.status = service_action.check_status()
        self.apiURL = "https://vc.eyeflow.ai"
        self.metricPath = "/metricversion"
        self.defaultDir = "/opt/eyeflow/monitor"
        self.update = {}
        self.whatsnew = {
            "update": {
                "autoUpdate": True,
                "autoRestart": True,
                "updateUrl": self.apiURL
            }
        }
        logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: Init apiURL: {self.apiURL}")
        logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: Init Metric path: {self.metricPath}")
        logging.debug(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: Init default dir: {self.defaultDir}")
    #----------------------------------------------------------------------------------------------
    def check_api(self):
        apiURL = self.apiURL + self.metricPath
        try: apiData = json.loads(requests.get(apiURL).text)
        except Exception as error: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: API inbound GET error: {error}")
        else:
            if len(apiData) > 0:
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: check API GET successful")
                self.gitData = {}
                for element in apiData:
                    if "/" in apiData[element]["libname"]: libName = apiData[element]["libname"].split("/")[-1]
                    else: libName = apiData[element]["libname"]
                    self.gitData[element] = {"name": libName, "folder": apiData[element]["folder"], "version": apiData[element]["libversion"]}
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: check API GET data lenght: {element}")
            else:
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: check API GET failed - empty response")
                if os.path.isdir("./lib"):
                    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: checking local ./lib folder")
                    self.gitData = {}
                    element = 0
                    for fn in os.listdir("./lib"):
                        if "/" in fn: libName = fn.split("/")[-1]
                        else: libName = fn
                        self.gitData[element] = {"name": libName, "folder": "lib", "version": "local"}
                        element += 1
                    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metric collector updater: checking local ./lib folder has {element} files")
        return
    #----------------------------------------------------------------------------------------------
    def is_hex(num):
        for x in num:
            if not x.isalnum(): return False
        return True
    #----------------------------------------------------------------------------------------------
    def update_module(self, localData):
        updated = False
        try: 
            git = int(self.gitData[localData["gitFile"]]["version"].split("-")[1])
            loc = int(localData["libVersion"].split("-")[1])
        except:
            git = self.gitData[localData["gitFile"]]["version"]
            loc = localData["libVersion"]
        if git > loc:
            if self.gitData[localData["gitFile"]]["folder"] == "root": modPath = ""
            else: modPath = self.gitData[localData["gitFile"]]["folder"]
            if not os.path.isdir(self.defaultDir + "/" + modPath): 
                os.mkdir(self.defaultDir + "/" + modPath)
                logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-updater.update_module: creating modules folder: {self.defaultDir + '/' + modPath}")
            fn = self.defaultDir + "/" + modPath + "/" + localData["name"]
            apiURL = self.apiURL + "/outbound/" + localData["name"]
            try: newFile = requests.get(apiURL)
            except Exception as error:
                newFile = ""
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: API outbound GET error: {error}")
            if newFile != "":
                os.rename(fn, fn + ".vcb")
                with open(fn, 'w') as f:
                    f.write(newFile.text)
                    updated = True
                    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_outdated: module {localData['name']} updated")
        return updated
    #----------------------------------------------------------------------------------------------
    def check_local(self):
        wd = os.getcwd()
        resposta = {}
        localCount = 0
        if os.path.isdir(self.defaultDir + "/lib"):
            localLib = os.listdir(self.defaultDir + "/lib")
            for fn in localLib:
                localVer = {}
                for gitFile in self.gitData:
                    if fn == self.gitData[gitFile]["name"]:
                        if self.gitData[gitFile]["folder"] == "root":
                            localFile = self.defaultDir + "/"  + fn
                        else: localFile = self.defaultDir + "/" + self.gitData[gitFile]["folder"] + "/" + fn
                        with open(localFile, "r") as f:
                            status = "not found"
                            for i in range(5):
                                a = next(f).strip()
                                if "versao" in a:
                                    tempVer = a.split("-")
                                    localVer["name"] = fn
                                    localVer["gitFile"] = gitFile
                                    localVer["folder"] = "lib"
                                    localVer["libDevVersion"] = tempVer[1].replace("'", "").replace('"', "")
                                    d = tempVer[-1].replace("'", "").replace('"', "")
                                    if len(d) == 14: localVer["libVersion"] = d[2:12]
                                    else: localVer["libVersion"] = d
                                    d = tempVer[-2].replace("'", "").replace('"', "")
                                    if updater.is_hex(d): localVer["libVersion"] = d + "-" + localVer["libVersion"]
                                    if localVer["libVersion"] == self.gitData[gitFile]["version"]: status = "uptodate"
                                    else:
                                        if updater.update_module(self, localVer): status = "success"
                                        else: status = "failed"
                                localVer["status"] = status
                            resposta[localCount] = localVer
                            localCount += 1
                            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_local: local file {fn} / GIT Info {self.gitData[gitFile]} / status {localVer['status']}")
            if os.path.isdir(self.defaultDir):
                localLib = os.listdir(self.defaultDir)
                for fn in localLib:
                    localVer = {}
                    for gitFile in self.gitData:
                        if fn == self.gitData[gitFile]["name"]:
                            with open(self.defaultDir + "/" + fn, "r") as f:
                                status = "not found"
                                for i in range(5):
                                    a = next(f).strip()
                                    if any(x in a for x in ["versao", "PUB", "beta"]):
                                        tempVer = a.split("-")
                                        localVer["name"] = fn
                                        localVer["gitFile"] = gitFile
                                        localVer["folder"] = ""
                                        localVer["libDevVersion"] = tempVer[1].replace("'", "").replace('"', "")
                                        d = tempVer[-1].split()[0].replace("'", "").replace('"', "")
                                        if len(d) == 14: localVer["libVersion"] = d[2:12]
                                        else: localVer["libVersion"] = d
                                        d = tempVer[-2].replace("'", "").replace('"', "")
                                        if updater.is_hex(d): localVer["libVersion"] = d + "-" + localVer["libVersion"]
                                        if localVer["libVersion"] == self.gitData[gitFile]["version"]: status = "uptodate"
                                        else:
                                            if updater.update_module(self, localVer): status = "success"
                                            else: status = "failed"
                                localVer["status"] = status
                            resposta[localCount] = localVer
                            localCount += 1
                            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.check_local: local file {fn} / GIT Info {self.gitData[gitFile]} / status {localVer['status']}")
            return resposta
        else: print("nao tem diretorio, faça a instalacao")
        return "error"
    #----------------------------------------------------------------------------------------------
    def update_config(self):
        import yaml
        from yaml.loader import SafeLoader
        for x in range(len(self.update)):
            if len(self.update[x]) > 2:
                if "collector-config" in self.update[x]["name"]:
                    if any(w in self.update[x]["status"] for w in["success", "uptodate"]):
                        getLib = os.listdir(self.defaultDir)
                        for fn in getLib:
                            if ("collector-config" in fn) and ((".vcb" in fn) or (".bkp" in fn)):
                                with open(self.defaultDir + "/" + fn) as f:
                                    oldConf = yaml.load(f, Loader=SafeLoader)
                                with open(self.defaultDir + "/" + self.update[x]["name"]) as f:
                                    newConf = yaml.load(f, Loader=SafeLoader)
                                os.rename(self.defaultDir + "/" + self.update[x]["name"], self.defaultDir + "/" + self.update[x]["name"] + ".ori") 
                                newConf.update(oldConf)
                                newConf.update(self.whatsnew)
                                with open(self.defaultDir + "/" + self.update[x]["name"], "w") as f:
                                    yaml.dump(newConf, f, default_flow_style=False, sort_keys=False)
        return
    #----------------------------------------------------------------------------------------------
    def cleanup(self):
        import re
        resposta = "error"
        for a in ["/lib", ""]:
            localLib = os.listdir(self.defaultDir + a)
            resposta = "nothing to delete"
            for fn in localLib:
                if re.search(".vcb", fn):
                    os.remove(os.path.join(self.defaultDir + a, fn))
                    resposta = "success"
        return resposta
###################################################################################################
# Main Application
if __name__ == '__main__':
    logging.basicConfig(filename = "./updater.log", level=logging.DEBUG, force=True)
    count = 0
    a=updater()
    status = service_action.check_status()
    while status == "active": 
        service_action.stop_service()
        print("trying to stop metric collector service")
        time.sleep(3)
        status = service_action.check_status()
        if count > 5: 
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: failed to stop service for {count} times")
            exit(1)
        count += 1
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: service stopped")
    updater.check_api(a)
    a.update = updater.check_local(a)
    try:
        if (len(a.update) == 0) or a.update == "error":
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: check local returned an error {a.update}")
    except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: check local returned valid data")
    updater.update_config(a)
    print("activating metric collector service")
    status = service_action.check_status()
    while status == "stopped": 
        service_action.start_service()
        print("trying to start metric collector service")
        time.sleep(3)
        status = service_action.check_status()
        if count > 5: 
            logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: failed to start service for {count} times")
            exit(1)
        count += 1
    logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: service started")
    cl = updater.cleanup(a)
    if cl == "error": logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: cleanup error")
    else:
        logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-version_update.main: cleanup completed: {cl}, exiting gracefully")
        print(f"Success! - cleanup status: {cl} - Exiting installer")
