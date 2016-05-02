#-*- coding: utf-8 -*-
import os,sys

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "soc.settings")
sys.path.append('.')

from django.conf import settings
from serveurs.fonctions import dictfetchall
from django.db import connection
import subprocess
from scans.socketTCP import socketTCP
import json
import logging

#Ce script sert a lancer les scans plannifies prevus pour la journee en cours
#Son execution devra donc etre plannifie a laide dune crontab


ojd=subprocess.check_output(['date'],shell=True).split(' ')[0]
cursor=connection.cursor()
cursor.execute('SELECT id,jours_execution FROM scans_plannifies WHERE jours_execution is NOT NULL and jours_execution!=\'\'')
scans=dictfetchall(cursor)
conn=clientTCP()

logger = logging.getLogger(__name__)

for scan in scans:
    jours=scan['jours_execution'].split(';')

    if ojd in jours:
        cursor=connection.cursor()
        cursor.execute('SELECT ip_hote FROM scan_plannifie_hote WHERE id_scan_plannifie=%s',[scan['id']])
        liste_ip=dictfetchall(cursor)    
        tableau_ip=[]

        for ip in liste_ip:
            tableau_ip.append(ip['ip_hote'])

        cursor.execute('SELECT id_application FROM scan_plannifie_application WHERE id_scan_plannifie=%s',[scan['id']])
        liste_id_appli=dictfetchall(cursor) 

        for id_appli in liste_id_appli:
            cursor.execute('SELECT ip FROM application_hote WHERE id_application=%s',[id_appli['id_application']])
            liste_ip_appli=dictfetchall(cursor)

            for adresse in liste_ip_appli:
                if (adresse['ip'] in tableau_ip)==False:
                    tableau_ip.append(adresse['ip']) 

        try:            
            data={'action':'addScan',
                'parametres':{
                'cibles':tableau_ip,
                'id_scan':scan['id'],
                'type_scan':'plannifie'}
            }

            rep=conn.envoyer(json.dumps(data))  
        
        except Exception as e:
            logger.error("[CRONTAB] Erreur d'ajout du scan: "+str(e))
            pass


cursor.close()
conn.fermer()    




