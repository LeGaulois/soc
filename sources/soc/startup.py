#-*- coding: utf-8 -*-
from scans.serveurTCP import srvTCP
from django.db import connection
from scans.clientNessusRPC import Nessus
import ConfigParser
from django.conf import settings
import datetime
import codecs,subprocess

BASE=settings.BASE_DIR+'/'
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
DIRECTORY_ID=Config.get('Nessus','Directory_Id')

def run():
    #Purge des scans dans la base
    date_fin=datetime.datetime.now()

    try:
        cursor=connection.cursor()
        cursor.execute("UPDATE scans_status SET etat='cancelled', date_fin=%s  WHERE etat='running'",[date_fin])
        cursor.close()
    except:
        pass

    #Purge des scans dans Nessus
    nessus=Nessus()
    try:
        nessus.connexion()
        liste=nessus.listScanStatusAndProgress(DIRECTORY_ID)
        
        for scan in liste:
            if scan['status']=='running':
                nessus.stopScan(scan['id'])
                time.sleep(8)

            try:
                nessus.supprimerScan(scan['id']) 
            except:
                pass

        nessus.deconnexion()
    except:
        pass

    srv=srvTCP()
    srv.start()

    #Suppression de l'ensemble des fichiers temporaires
    subprocess.check_output('rm -rf '+BASE+'scans/temp/nmap/*', shell=True)
    subprocess.check_output('rm -rf '+BASE+'scans/temp/nessus/*', shell=True)
    subprocess.check_output('rm -rf '+BASE+'maintenance/temp/*', shell=True)
