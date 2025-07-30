#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#######################################################################################################################
versao = "metricremote-v5.11-PUB-2846410-2310272107"
#######################################################################################################################
import logging
import time
from lib import common as c
#######################################################################################################################
c.versionDict["metricremote"] = versao
#######################################################################################################################
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
import time
import socket
from lib import common as c

versao = "metricremote-v5.11-SOCKET"
c.versionDict["metricremote"] = versao

class remote_open_exec:
    # Execute Remote check for Open Port metric collector
    @staticmethod
    def collect_remote_open(getRemoteOpen, remoteOpenList):
        remoteOpenMetrics, remoteOpenExecError = {}, 0
        if not c.logFirstRun:
            logging.info(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-metricapiget version: {versao}")

        if getRemoteOpen and remoteOpenList and len(remoteOpenList) > 0:
            for remoteOpenCount, remoteOpenItem in enumerate(remoteOpenList):
                remoteTemp = {"remoteOpenUrl": remoteOpenItem}
                ipUrl, portUrl = None, None

                try:
                    # Parse IP e porta
                    if ":" in remoteOpenItem:
                        ipUrl, portUrl = remoteOpenItem.split(":")
                        portUrl = int(portUrl)
                    else:
                        ipUrl = remoteOpenItem
                        portUrl = 80  # porta padrão

                    # Testa conexão via socket
                    status, response = remote_open_exec.check_port(ipUrl, portUrl)
                    remoteTemp["remoteOpenStatus"] = status
                    remoteTemp["remoteOpenResponse"] = response

                except Exception as e:
                    remoteTemp["remoteOpenStatus"] = 0
                    remoteTemp["remoteOpenResponse"] = f"error: {e}"
                    remoteOpenExecError = 1
                    if not c.logFirstRun:
                        logging.error(f"{time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}-remote_open_exec.collect_remote_open: error {e}")

                remoteOpenMetrics[remoteOpenCount] = remoteTemp

        remoteOpenMetrics["remoteOpenExecError"] = remoteOpenExecError
        return remoteOpenMetrics

    # Função substituta ao exec_cmd com netcat
    @staticmethod
    def check_port(ip, port, timeout=5):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(timeout)
                result = sock.connect_ex((ip, port))  # 0 = sucesso
                if result == 0:
                    return 1, f"Connection to {ip}:{port} succeeded"
                else:
                    return 0, f"Connection to {ip}:{port} failed (code {result})"
        except socket.gaierror:
            return 0, f"DNS resolution failed for {ip}"
        except Exception as e:
            return 0, f"Exception occurred: {e}"

    # Esta função está aqui apenas por compatibilidade, mas não é mais usada na versão socket
    @staticmethod
    def remote_open_metrics(remoteopenout):
        return {
            "remoteOpenStatus": 0,
            "remoteOpenResponse": remoteopenout
        }
        #----------------------------------------------------------------------------------------------------------------------
