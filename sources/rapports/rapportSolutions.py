#-*- coding: utf-8 -*-
from generationRapports.rapportSolutions.pageGarde import *
from generationRapports.rapportSolutions.intro import *
from generationRapports.rapportSolutions.tableauSolutions import *
from generationRapports.rapportSolutions.tableauVulnerabilites import *
from shutil import copyfile
import subprocess
from django.db import connection
from fonctions import dictfetchall
import socket
import ConfigParser
import codecs
import re
from django.conf import settings

'''
La fonction permet de génerer un rapport PDF
ce rapport présente pour chaque serveur selectionné:
    - la liste des vulnrébilités auquelles il est soumis
    - les actions à adopter pour les corriger

La sélection des IP peut se faire soit par adresse IP, ou bien par application.

Le rapport est généré à l'aide de Latex
'''


#Variables globales
BASE=settings.BASE_DIR+'/'#'/var/www/html/django/sources/'
REP_TRAVAIL=BASE+'rapports/generationRapports/rapportSolutions/'
REP_RAPPORT=BASE+'rapports/rapports/'
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
AUTEUR=Config.get('Rapports','Auteur')
SOCIETE=Config.get('Rapports','Societe')
LOGO=BASE+"static/img/"+Config.get('Rapports','Logo')


def creerRapportSolutions(listeIP,group_by,titre='rapportSolutions'):

    cursor=connection.cursor()

    if group_by=='vuln':
        cursor.execute('''SELECT DISTINCT(id),criticite,nom,solution,description,infos_complementaires,ip_hote FROM vulnerabilitees 
LEFT JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id
WHERE criticite!='Info' ORDER BY id ASC''')

    else:
        cursor.execute('''SELECT ip_hote,nom,description,solution,infos_complementaires,criticite FROM vuln_hote_service
LEFT JOIN vulnerabilitees ON id_vuln=id WHERE criticite!='Info' ORDER BY ip_hote ASC''')

    dict_vuln_temp=dictfetchall(cursor)

    dict_vuln=[]
    taille=len(dict_vuln_temp)
    #On selectionne uniquement les adresses demandees
    for i in range(0,taille):
        if (dict_vuln_temp[i]['ip_hote'] in listeIP):
            dict_vuln.append(dict_vuln_temp[i])


    
    if group_by=='vuln':
        dict_vuln_temp=[]
        taille=len(dict_vuln)
        id_vuln_precedent=-1
        indice=-1

        for i in range(0,taille):
            id_actuel=dict_vuln[i]['id']

            if id_actuel!=id_vuln_precedent:
                id_vuln_precedent=id_actuel
                indice=indice+1
                dict_vuln_temp.append(dict_vuln[i])
                dict_vuln_temp[indice]['ip_hote']=[dict_vuln[i]['ip_hote']]

            else:
                dict_vuln_temp[indice]['ip_hote'].append(dict_vuln[i]['ip_hote'])

        del dict_vuln

        vuln_critical=[]
        vuln_high=[]
        vuln_medium=[]
        vuln_low=[]
        
        for vuln in dict_vuln_temp:
            crit=vuln['criticite']

            if crit=='Critical':
                vuln_critical.append(vuln)
            elif crit=='High':
                vuln_high.append(vuln)

            elif crit=='Medium':
                vuln_medium.append(vuln)

            else:
                vuln_low.append(vuln)

        dict_vuln=vuln_critical+vuln_high+vuln_medium+vuln_low


        repartition_vuln={'critique':len(vuln_critical),'haute':len(vuln_high),'moyenne':len(vuln_medium),'faible':len(vuln_low)}


    else:
        repartition_vuln={'critique':0,'haute':0,'moyenne':0,'faible':0}


        for vuln in dict_vuln:
            crit=vuln['criticite']

            if crit=='Critical':
                repartition_vuln['critique']+=1
            if crit=='High':
                repartition_vuln['haute']+=1

            if crit=='Medium':
                repartition_vuln['moyenne']+=1

            else:
                repartition_vuln['faible']+=1


    #Mise en forme du titre
    #Rappel: en latex les caractères spéciaux (_,& doivent être échappés), sinon erreur de compilation
    titre=titre.replace('&','\&').replace('_','')


    copyfile(REP_TRAVAIL+'base.tex',REP_TRAVAIL+'temp/'+titre+'.tex')
    pageGarde('Actions correctrices\n"'+titre+'"',AUTEUR,SOCIETE,LOGO,REP_TRAVAIL+'temp/'+titre+'.tex')
    intro(repartition_vuln,listeIP,REP_TRAVAIL+'temp/'+titre+'.tex')
    tableauVulnerabilites(dict_vuln,group_by,REP_TRAVAIL+'temp/'+titre+'.tex')
    tableauSolutions(dict_vuln,group_by,REP_TRAVAIL+'temp/'+titre+'.tex')
    fichierLatex=open(REP_TRAVAIL+'temp/'+titre+'.tex','a')
    fichierLatex.write('''
\\end{document}''')
    fichierLatex.close()
    

    liste_arguments=[REP_TRAVAIL,titre]

    #Contrôle des arguments
    for arg in liste_arguments:
        error=re.search('[;|<>]',str(arg))

        if error!=None:
            raise Exception("Erreur de paramètres")


    #Necessaire pour la creation des liens dans le sommaire vers les différentes parties
    for i in range(0,3):
        try:
            subprocess.check_output(['pdflatex -no-file-line-error -interaction=nonstopmode --output-directory '+REP_TRAVAIL+'temp/ '+REP_TRAVAIL+'temp/'+titre+'.tex >/dev/null'],shell=True)
            time.sleep(1)
        except:
            pass


    f = open(REP_TRAVAIL+'temp/'+titre+'.pdf', 'r')
    pdf= f.read()
    f.close()

    subprocess.check_output(['rm '+REP_TRAVAIL+'temp/'+titre.replace(' ','\ ')+'* >/dev/null'],shell=True)

    return pdf
    



