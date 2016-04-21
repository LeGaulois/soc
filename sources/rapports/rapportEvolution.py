#-*- coding: utf-8 -*-
from generationRapports.rapportEvolution.pageGarde import *
from generationRapports.rapportEvolution.intro import *
from generationRapports.rapportEvolution.tableauVuln import *
from generationRapports.rapportEvolution.tableauServices import *
from shutil import copyfile
import subprocess
from django.db import connection
from fonctions import dictfetchall
import socket
import ConfigParser
import codecs
from django.conf import settings
import re
import time

'''
La fonction permet de génerer un rapport PDF
ce rapport d'évolution peut être généré à la suite de chaque scan

Il montre l'évolution des vulnérabilités rencontrés, pour une même machine,
depuis la date du dernier scan 

Le rapport est généré à l'aide de Latex
'''


#Variables globales
BASE=settings.BASE_DIR+'/'
REP_TRAVAIL=BASE+'rapports/generationRapports/rapportEvolution/'
REP_RAPPORT=BASE+'rapports/rapports/'
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
AUTEUR=Config.get('Rapports','Auteur')
SOCIETE=Config.get('Rapports','Societe')
LOGO=BASE+"static/img/"+Config.get('Rapports','Logo')


def creerRapportEvolution(nomUnique,id_scan,type_scan):
    cursor=connection.cursor()
    cursor.execute('SELECT date_lancement FROM scans_status WHERE id=%s LIMIT 1',[id_scan])
    date=dictfetchall(cursor)
    date_scan=date[0]['date_lancement']
    
    cursor.execute('''SELECT ip_hote,nom,description,criticite,date_correction,date_detection FROM vuln_hote_service 
        INNER JOIN vulnerabilitees ON vuln_hote_service.id_vuln=vulnerabilitees.id
        WHERE (date_detection=%s or date_correction=%s) AND criticite!='Info' ORDER BY ip_hote ASC''',[date_scan,date_scan])
    retourScan=dictfetchall(cursor)

    cursor.execute('''SELECT ip_hote,nom,protocole,port,version,date_ajout,date_retrait FROM services 
        WHERE date_ajout=%s or date_retrait=%s ORDER BY ip_hote ASC''',[date_scan,date_scan])
    retourServices=dictfetchall(cursor)


    if type_scan=='plannifie':
        cursor.execute('''SELECT id_scan_plannifie FROM scans_status 
            INNER JOIN scan_plannifie_status ON scans_status.id=scan_plannifie_status.id_scans_status
            WHERE scans_status.id=%s LIMIT 1''',[id_scan])
        dict_id_scan=dictfetchall(cursor)
        id_scan_plannifie=dict_id_scan[0]['id_scan_plannifie']

        cursor.execute('SELECT DISTINCT(ip) FROM scan_hote WHERE id_scan=%s',[id_scan])
        dictIP=dictfetchall(cursor)

        cursor.execute('SELECT * FROM scans_plannifies WHERE id=%s LIMIT 1',[id_scan_plannifie])
        dictScan=dictfetchall(cursor)
        titre='Rapport du scan plannifie\n"'+str(dictScan[0]['nom'])+'"\ndu '+str(date_scan).split(' ')[0]

        chemin_rapport=REP_RAPPORT+'ScansPlannifies/'+str(int(id_scan_plannifie))+'/'+str(int(id_scan))+'/'

    else:
        cursor.execute('''SELECT id_scan_manuel FROM scans_status 
            INNER JOIN scan_manuel_status ON scans_status.id=scan_manuel_status.id_scans_status
            WHERE scans_status.id=%s LIMIT 1''',[id_scan])
        dict_id_scan=dictfetchall(cursor)
        id_scan_manuel=dict_id_scan[0]['id_scan_manuel']


        cursor.execute('SELECT DISTINCT(ip_hote) FROM scan_manuel_hote WHERE id_scan_manuel=%s',[id_scan_manuel])
        dictIP=dictfetchall(cursor)

        cursor.execute('SELECT * FROM scans_manuels WHERE id=%s LIMIT 1',[id_scan_manuel])
        dictScan=dictfetchall(cursor)

        if len(dictIP)==1:
            try:
                name, alias, addresslist = socket.gethostbyaddr(dictIP[0]['ip_hote'])
            except:
                name=dictIP[0]['ip_hote']

            titre='Rapport du scan Manuel sur \n"'+str(name)+'"\ndu '+str(date_scan).split(' ')[0]

        else:
            titre='Rapport du scan Manuel \n démarré le '+str(date_scan).split(' ')[0]+'\n à '+str(date_scan).split(' ')[1].split('.')[0]



        chemin_rapport=REP_RAPPORT+'ScansManuels/'+str(int(id_scan))+'/'

        

    

    
    copyfile(REP_TRAVAIL+'base.tex',REP_TRAVAIL+'/temp/'+nomUnique+'.tex')


    pageGarde(titre,AUTEUR,SOCIETE,LOGO,REP_TRAVAIL+'/temp/'+nomUnique+'.tex') 

    if type_scan=='plannifie':
        intro(dictScan[0],dictIP,REP_TRAVAIL+'/temp/'+nomUnique+'.tex','plannifie')

    else: 
        intro(dictScan[0],dictIP,REP_TRAVAIL+'/temp/'+nomUnique+'.tex','manuel')


    fichierLatex=open(REP_TRAVAIL+'/temp/'+nomUnique+'.tex','a')
    fichierLatex.write('''\\newpage
\\section{Scans}''')
    fichierLatex.close()


    if dictScan[0]['nessus']==True:
        tableauVuln(retourScan,REP_TRAVAIL+'/temp/'+nomUnique+'.tex')

    if dictScan[0]['nmap']==True:
        tableauServices(retourServices,REP_TRAVAIL+'/temp/'+nomUnique+'.tex')

    
    fichierLatex=open(REP_TRAVAIL+'/temp/'+nomUnique+'.tex','a')
    fichierLatex.write('''
\\end{document}''')
    fichierLatex.close()


    liste_arguments=[REP_TRAVAIL,nomUnique,chemin_rapport]

    #Contrôle des arguments
    #On s'assure qu'il n'y ait pas d'injection de codes tiers
    for arg in liste_arguments:
        error=re.search('[;|<>]',str(arg))

        if error!=None:
            raise Exception("Erreur de paramètres")


    #Necessaire pour la creation des liens dans le sommaire vers les différentes parties
    for i in range(0,3):
        try:
            subprocess.check_output(['pdflatex -no-file-line-error -interaction=nonstopmode --output-directory '+REP_TRAVAIL+'temp/ '+REP_TRAVAIL+'temp/'+nomUnique+'.tex >/dev/null &>/dev/null'],shell=True)
            time.sleep(3)
        except:
            pass 

    time.sleep(10)
    copyfile(REP_TRAVAIL+'temp/'+nomUnique+'.pdf',chemin_rapport+nomUnique+'_evolution.pdf')
    subprocess.check_output(['rm '+REP_TRAVAIL+'temp/'+nomUnique+'* >/dev/null'],shell=True)



