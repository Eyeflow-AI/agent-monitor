#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metriccam-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import json 
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metriccam"] = versao
#######################################################################################################################
class cam_exec:
    # Execute camera metric collector
    def collect_cam(getCam, camURL, camRestart = 0):
        from lib import common as c
        urlList = []
        if isinstance(camURL, str): 
            if "," in camURL:
                urlList = camURL.split(",")
            else: urlList.append(camURL)
        else: urlList = camURL
        camURL = urlList
        camout, camExecError = "", 0
        if not c.logFirstRun: logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-metriccam version: {versao}")
        if getCam:
            if camURL != None:
                if len(camURL) > 0:
                    urlCount = 0
                    camTemp = {}
                    for item in camURL:
                        try: camout = json.loads(c.exec_cmd(["curl", str(item), "--connect-timeout", "4"], c.debugMode)["output"])
                        except:
                            if not c.logFirstRun: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.collect_cam: Get camera data error")
                            camExecError = 1
                        if camout != "":
                            camKeys = camout.keys()
                            if "data" in camKeys:
                                camTemp[urlCount] = cam_exec.cam_metrics(camout, camRestart, c.debugMode)
                                camTemp[urlCount]["camUrl"] = item
                                #camTemp[urlCount] = {"camList": cam_exec.cam_metrics(camout, camRestart, c.debugMode)}
                            elif "cameras_list" in camKeys:
                                pyResp = {}
                                pyCount = 0
                                for camItem in range(len(camout["cameras_list"])):
                                    pycam = {
                                    "camUrl": item,
                                    "status": 0,
                                    "camName": "no_cam",
                                    "frameSeq": 0,
                                    "camHB": 0,
                                    "camHeight": 0,
                                    "camWidth": 0,
                                    "endPoint": ""}
                                    try:
                                        if camout["ok"] == True: pycam["status"] = 1
                                    except: pycam["status"] = 0
                                    try: pycam["camName"] = camout["cameras_list"][camItem]["camera_name"]
                                    except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.collect_cam: Get py camera name error")
                                    try: pycam["camHB"] = time.mktime(time.strptime(camout["cameras_list"][camItem]["frame_time"], "%Y-%m-%d %H:%M:%S.%f"))
                                    except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.collect_cam: Get py camera HB error")
                                    try: pycam["endPoint"] = str(camout["cameras_list"][camItem]["url_path"])
                                    except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.collect_cam: Get py URL path error")
                                    pyResp[pyCount] = pycam
                                    pyCount += 1
                                camTemp[urlCount] = pyResp
                                camTemp[urlCount]["camUrl"] = item
                                urlCount += 1
                        else:
                            noCam = {}
                            noCam["status"] = 0
                            noCam["camName"] = "no_cam"
                            noCam["frameSeq"] = 0
                            noCam["camHB"] = 0
                            noCam["camHeight"] = 0
                            noCam["camWidth"] = 0
                            noCam["endPoint"] = ""
                            camTemp[0] = {0: noCam}
                            camTemp[0]["camUrl"] = item
        camTemp["camExecError"] = camExecError
        return camTemp
        #----------------------------------------------------------------------------------------------------------------------
    # Prepare camera metrics data
    def cam_metrics(camout, camRestart, debugMode):
        resposta = {}
        respItem = 0
        try: camData = camout["data"]
        except: camData = 0
        if camData:
            for item in camData.keys():
                cStatus = 0
                camTemp = {
                    "status": 0,
                    "camName": "no_cam",
                    "frameSeq": 0,
                    "camHB": 0,
                    "camHeight": 0,
                    "camWidth": 0,
                    "endPoint": ""}
                try: camTemp["camName"] = camData[item]["input_name"]
                except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera [input_name] not set")
                try: cStatus = camData[item]["status"].lower()
                except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera [status] not set")
                if cStatus == "ok": camTemp["status"] = 1
                try: camTemp["frameSeq"] = int(camData[item]["seq"])
                except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera [seq] not set")
                try: camTemp["camHB"] = float(camData[item]["time"])
                except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera [time] not set")
                try: camTemp["camHeight"] = int(camData[item]["height"])
                except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera [height] not set")
                try: camTemp["camWidth"] = int(camData[item]["width"])
                except: logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera [width] not set")
                resposta[respItem] = camTemp
                respItem += 1
                if camRestart and (time.time() - camTemp["camHB"] > 30): 
                    if debugMode: 
                        logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera restart: {camRestart}")
                        logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.cam_metrics: Camera heartbeat delay: {(time.time() - camTemp['camHB'])}")
                    resposta["camRestartError"] = cam_exec.camera_restart(camTemp["camName"])
        return resposta
        #----------------------------------------------------------------------------------------------------------------------
    # Restart camera
    def camera_restart(camName):
        import subprocess
        camExecError = 0
        if camName != 0: c.cameraCount += 1
        if cameraCount > 3:
            try: reCAM = subprocess.call('echo $SAMON | sudo -S systemctl restart run_flow.service', shell = True)
            except: 
                logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.camera_restart: Error restarting run_flow")
                camExecError = 1
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time()))}-cam_exec.camera_restart: Camera restarted")
            cameraCount = 0
        return camExecError
        #----------------------------------------------------------------------------------------------------------------------
