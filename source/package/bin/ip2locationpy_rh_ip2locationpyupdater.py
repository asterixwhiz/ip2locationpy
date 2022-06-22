# SPDX-FileCopyrightText: 2020 Splunk Inc (Ryan Faircloth) <rfaircloth@splunk.com>
#
# SPDX-License-Identifier: Apache-2.0

"""
This controller does the update
"""
import json
import logging
import os
import re
import subprocess
import sys
import tempfile
from os.path import dirname
import shutil
import ssl
import urllib3
import datetime
import random

from splunk import AuthorizationFailed, ResourceNotFound
from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.rest import simpleRequest

import zipfile

ta_name = "ip2locationpy"
pattern = re.compile(r"[\\/]etc[\\/]apps[\\/][^\\/]+[\\/]bin[\\/]?$")
new_paths = [path for path in sys.path if not pattern.search(path) or ta_name in path]
new_paths.append(os.path.join(dirname(dirname(__file__)), "lib"))
new_paths.insert(0, os.path.sep.join([os.path.dirname(__file__), ta_name]))
sys.path = new_paths

from ip2locationpy_helpers import rest_handler


def setup_logger(level):
    """
    Setup a logger for the REST handler
    """

    logger = logging.getLogger(
        "splunk.appserver.ip2locationpy_rh_updater.handler"
    )
    logger.propagate = (
        False  # Prevent the log messages from being duplicated in the python.log file
    )
    logger.setLevel(level)

    log_file_path = make_splunkhome_path(
        ["var", "log", "splunk", "ip2locationpy_rh_updater.log"]
    )
    file_handler = logging.handlers.RotatingFileHandler(
        log_file_path, maxBytes=25000000, backupCount=5
    )

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)s pid=%(process)d tid=%(threadName)s "
        "file=%(filename)s:%(funcName)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    return logger


logger = setup_logger(logging.INFO)


class ip2locationpy_update_handler(rest_handler.RESTHandler):
    """
    This is a REST handler that supports backing up lookup files.
    This is broken out as a separate handler so that this handler can be replayed on other search
    heads via the allowRestReplay setting in restmap.conf.
    """
    
    def __init__(self, command_line, command_arg):
        super().__init__(command_line, command_arg, logger)

    def post_update(self, request_info, token, database_code, proxy_settings=None, **kwargs):
        updatesession=(datetime.datetime.now()).strftime("%Y%m%d%H%M%S") + "_" + str(random.randint(1,10000))
        logger.info(f"[Updatesession {updatesession}]: Asked to update")
        # payload = json.loads(request["payload"])
        db_bin_dir = os.path.expandvars("$SPLUNK_HOME/etc/apps/ip2locationpy/data/")
        try:
            if database_code=="DBCLEAN":
                logger.info("[Updatesession {updatesession}]: Entering Special Use Case for database_code==""DBCLEAN""")
                path=os.path.join(db_bin_dir,"ip2locationgeodb.bin")
                if os.path.exists(path):
                    logger.info(f"[Updatesession {updatesession}]: Found {path}.  Trying to remove.")
                    os.remove(path)
                    logger.info(f"[Updatesession {updatesession}]: Removed {db_bin_dir}ip2locationgeodb.bin.")
                else:
                    logger.info(f"[Updatesession {updatesession}]: {path} Not Found.  No cleanup to perform.  Disable input(s) with DBCLEAN recommended")
            elif database_code=="PXCLEAN":
                logger.info("[Updatesession {updatesession}]: Entering Special Use Case for database_code==""PXCLEAN""")
                path=os.path.join(db_bin_dir,"ip2locationproxydb.bin")
                if os.path.exists(path):
                    logger.info(f"[Updatesession {updatesession}]: Found {path}.  Trying to remove.")
                    os.remove(path)
                    logger.info(f"R[Updatesession {updatesession}]: Removed {path}")
                else:
                    logger.info(f"[Updatesession {updatesession}]: {path} Not Found.  No cleanup to perform.  Disable input(s) with PXCLEAN recommended")
            else:
                    with tempfile.TemporaryDirectory() as tmpdirname:
                        logger.info(f"[Updatesession {updatesession}]: Used tmpdirname = {tmpdirname}")
                        zipfilename="ip2locationpy_"+database_code+".zip"
                        zipfilefullname=os.path.join(tmpdirname,zipfilename)
                        with open(zipfilefullname, "wb"
                        ) as file:
                            cert_file = os.path.expandvars("$SPLUNK_HOME/etc/apps/ip2locationpy/lib/certifi/cacert.pem")
                            if (not os.path.exists(cert_file)):
                                logger.info(f"[Updatesession {updatesession}]: CA Cert File Missing {cert_file}")
                                raise Exception(f"[Updatesession {updatesession}]: ERROR: CA Cert File Missing {cert_file}.")
                            url="https://www.ip2location.com/download"
                            logger.info(f"[Updatesession {updatesession}]: Trying to update using {url}/?token=<<tokenhidden>>&file={database_code}")
                            http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED",ca_certs=cert_file,ssl_version=ssl.PROTOCOL_TLSv1_2)
                            resp = http.request(
                                    "GET",
                                    url,
                                    fields={"file": database_code,
                                    "token": token},
                                    preload_content=False
                                )    
                            while True:
                                data = resp.read(65536)
                                if not data:
                                    break
                                file.write(data)
                        if (resp.status==200 and 'Content-Length' in resp.headers.keys() and int(resp.headers['Content-Length'])<1048576):
                            logger.info(f"[Updatesession {updatesession}]: ERROR: Reponse 200 but 'Content-Length' doesn't exists or is < 1MB, possibly bad API key or other error.")
                            raise Exception(f"[Updatesession {updatesession}]: ERROR: Reponse 200 but 'Content-Length' < 1MB, possibly bad API key or other error.")
                        elif (not resp.status==200):
                            logger.info(f"[Updatesession {updatesession}]: ERROR: Reponse not 200, instead {resp.status}")
                            raise Exception(f"[Updatesession {updatesession}]: ERROR: Reponse not 200.  Status: {resp.status}")
                        logger.info(f"[Updatesession {updatesession}]: File Downloaded, starting unzip routine.")
                        with zipfile.ZipFile(zipfilefullname, "r") as file:
                            dbfile=(next((match for match in file.namelist() if re.match(".+\.BIN$",match)),None))
                            if re.match(".+\.BIN$",dbfile) and re.match("^DB.+",database_code):
                                logger.info(f"[Updatesession {updatesession}]: Found geolocation DB {dbfile} in {file.filename}, trying to extract to {tmpdirname}")
                                path=file.extract(dbfile,tmpdirname)
                                logger.info(f"[Updatesession {updatesession}]: Trying to rename {path} as {db_bin_dir}ip2locationgeodb.bin")
                                '''os.replace(path, db_bin_dir + "ip2locationgeodb.bin")'''
                                shutil.copyfile(path, db_bin_dir + "ip2locationgeodb.bin")
                                logger.info(f"[Updatesession {updatesession}]: Successfully renamed {path} as {db_bin_dir}ip2locationgeodb.bin")
                            elif re.match(".+\.BIN$",dbfile) and re.match("^PX.+",database_code):
                                logger.info(f"[Updatesession {updatesession}]: Found proxy DB {dbfile} in {file.filename}, trying to extract to {tmpdirname}")
                                path=file.extract(dbfile,tmpdirname)
                                logger.info(f"[Updatesession {updatesession}]: Trying to rename {path} as {db_bin_dir}ip2locationproxydb.bin")
                                '''os.replace(path, db_bin_dir + "ip2locationproxydb.bin")'''
                                shutil.copyfile(path, db_bin_dir + "ip2locationproxydb.bin")
                                logger.info(f"[Updatesession {updatesession}]: Successfully renamed {path} as {db_bin_dir}ip2locationproxydb.bin")
                            else:
                                logger.info(f"[Updatesession {updatesession}]: ERROR: No BIN file found in {f.filename}.  Check database code")
                                raise Exception(f"[Updatesession {updatesession}]: ERROR: No BIN file found in {file.filename}.")

            # Everything worked, return accordingly
            return {
                "payload": "done",  # Payload of the request.
                "status": 200,  # HTTP status code
            }
        except Exception as e:
            logger.exception(f"[Updatesession {updatesession}]: ERROR: Exception generated when attempting to download AND/OR extract IP2Location Files or clean files: {e}"
            )
            return {
                "payload": "Failed",  # Payload of the request.
                "status": 500,  # HTTP status code
            }
        finally:
            path=(os.path.join(db_bin_dir,"ip2locationgeodb.bin"))
            if os.path.exists(path):
                inode = os.stat(path)
                logger.info(
                        "db_bin=ip2locationgeodb.bin"
                        + " exists=true"
                        + " size="
                        + str(inode.st_size)
                        + " mtime="
                        + str(inode.st_mtime)
                    )
            else:
                logger.info(
                        "db_bin=ip2locationgeodb.bin"
                        + " exists=false"
                        + " size=0"
                        + " mtime=0"
                    )
            path=(os.path.join(db_bin_dir,"ip2locationproxydb.bin"))
            if os.path.exists(path):
                inode = os.stat(path)
                logger.info(
                        "db_bin=ip2locationproxydb.bin"
                        + " exists=true"
                        + " size="
                        + str(inode.st_size)
                        + " mtime="
                        + str(inode.st_mtime)
                    )
            else:
                logger.info(
                        "db_bin=ip2locationproxydb.bin"
                        + " exists=false"
                        + " size=0"
                        + " mtime=0"
                    )
