#-*- coding: utf-8 -*-
from scans.serveurTCP import srvTCP
from django.db import connection
from scans.clientNessusRPC import Nessus
import ConfigParser
from django.conf import settings
import datetime,pytz,time
import codecs,subprocess
import logging

BASE=settings.BASE_DIR+'/'
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
DIRECTORY_ID=Config.get('Nessus','Directory_Id')
INITIALISER=Config.get('PROJET','initialiser')

logger = logging.getLogger(__name__)

def run():
    #Purge des scans dans la base
    if INITIALISER=='YES':
        demarrageServeurTache()

def demarrageServeurTache():
    d=datetime.datetime.now()
    tz = pytz.timezone('Europe/Paris')
    date_fin=date_fin=tz.localize(d)

    try:
        cursor=connection.cursor()
        cursor.execute("UPDATE scans_status SET etat='cancelled', date_fin=%s  WHERE etat='running'",[date_fin])
        cursor.close()
    except Exception as e:
        logger.error("Erreur lors de la MAJ du status des scans non arretes: "+str(e))
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
    except Exception as e:
        logger.error("Erreur lors de la suppresion des scans Nessus")

    srv=srvTCP()
    srv.start()

    #Suppression de l'ensemble des fichiers temporaires
    subprocess.check_output('rm -rf '+BASE+'scans/temp/nmap/*', shell=True)
    subprocess.check_output('rm -rf '+BASE+'scans/temp/nessus/*', shell=True)
    subprocess.check_output('rm -rf '+BASE+'maintenance/temp/*', shell=True)
