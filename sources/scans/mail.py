#-*- coding: utf-8 -*-
import ConfigParser
import codecs
from fonctions import dictfetchall
from django.db import connection
from django.conf import settings
import smtplib,glob
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders

BASE=settings.BASE_DIR+'/'
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

ADRESSE_ENVOIE=Config.get('MAIL','Mail_Addr')
PASSWORD=Config.get('MAIL','Password')
SMTP=Config.get('MAIL','SMTP_Addr')
PORT=int(Config.get('MAIL','SMTP_Port'))


def envoieMail(scan):
    '''
    Cette fonction permet d'envoyer un mail suite à la fin d'un scan
    '''
    
    #Entete
    fromaddr = ADRESSE_ENVOIE
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['Subject'] = "Rapport du scan N°"+str(scan['id'])

    cursor=connection.cursor()
    cursor.execute('SELECT type FROM scans_status WHERE id=%s LIMIT 1',[scan['id']])
    type_scan=dictfetchall(cursor)


    #Corps du texte
    body=""""Bonjour,\n
    Le scan N°"""+str(scan['id'])+" s'est terminé avec l'état \""+str(scan['status'])+"\"."
  
    if scan['status']!="completed":
        body+="Les erreurs suivantes ont été rencontrés lors du scan:\n"

    for erreur in scan['erreurs']:
        body+="- "+str(erreur)+"\n"


    body+="\n\n Cordialement"
    msg.attach(MIMEText(body, 'plain'))


    #Gestion des PJ
    CHEMIN_RAPPORT=BASE+'rapports/rapports/'

    if type_scan[0]['type']=="manuel":
        chemin=CHEMIN_RAPPORT+'ScansManuels/'+str(scan['id'])+'/'
        
    else:
        cursor.execute("SELECT id_scan_plannifie FROM scan_plannifie_status WHERE id_scans_status=%s LIMIT 1",[scan['id']])
        res=dictfetchall(cursor)
        chemin=CHEMIN_RAPPORT+'ScansPlannifies/'+str(res[0]['id_scan_plannifie'])+'/'+str(scan['id'])+'/'


    if scan['nessus']==True:
        liste_fichier=glob.glob(chemin+str(scan['id'])+"__*_nessus.pdf")

        if len(liste_fichier)!=0:
            nom_fichier=liste_fichier[0].split('/')[-1]
    	    attachment = open(str(chemin+nom_fichier), "rb")
    	 
    	    part = MIMEBase('application', 'octet-stream')
    	    part.set_payload((attachment).read())
    	    encoders.encode_base64(part)
    	    part.add_header('Content-Disposition', "attachment; filename= %s" % nom_fichier)
    	    msg.attach(part)


    if scan['nmap']==True:
        liste_fichier=glob.glob(chemin+str(scan['id'])+"__*_evolution.pdf")
    
        if len(liste_fichier)!=0:
            nom_fichier=liste_fichier[0].split('/')[-1]
    	    attachment = open(str(chemin+nom_fichier), "rb")
    	 
    	    part = MIMEBase('application', 'octet-stream')
    	    part.set_payload((attachment).read())
    	    encoders.encode_base64(part)
    	    part.add_header('Content-Disposition', "attachment; filename= %s" % nom_fichier)
    	    msg.attach(part)
    

    #Connexion
    server = smtplib.SMTP(SMTP, PORT)
    server.starttls()
    server.login(fromaddr,PASSWORD)
    
    #Selection des adresses à contacter
    cursor.execute('SELECT email FROM auth_user')
    res=dictfetchall(cursor)

    for element in res:
        toaddr= element['email']
        msg['To']= toaddr
        text = msg.as_string()

        server.sendmail(fromaddr, toaddr, text)
	
	
    server.quit()
