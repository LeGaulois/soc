#-*- coding: utf-8 -*-
from serveurs.fonctions import dictfetchall
from django.db import connection
import subprocess
from time import sleep
from scans.scanner import Scanner


'''
doit être appelé par une crontab pour déclencher le lancement des scans plannifiés pour la journée en cours
'''



ojd=subprocess.check_output(['date'],shell=True).split(' ')[0]

cursor=connection.cursor()
cursor.execute('SELECT id,jours_execution FROM scans_plannifies WHERE jours_execution is NOT NULL and jours_execution!=\'\'')
scans=dictfetchall(cursor)

liste_id=[]



for scan in scans:
	jours=scan['jours_execution'].split(';')

	if ojd in jours:
		liste_id.append(scan['id'])


for id_scan in liste_id:
	cursor=connection.cursor()
	cursor.execute('SELECT ip_hote FROM scan_plannifie_hote WHERE id_scan_plannifie=%s',[id_scan])
	liste_ip=dictfetchall(cursor)	


	tableau_ip=[]

	for ip in liste_ip:
		tableau_ip.append(ip['ip_hote'])

	del liste_ip


	if len(tableau_ip)==0:
		cursor.execute('SELECT id_application FROM scan_plannifie_application WHERE id_scan_plannifie=%s',[id_scan])
		liste_id_appli=dictfetchall(cursor)



		for id_appli in liste_id_appli:
			cursor.execute('SELECT ip FROM application_hote WHERE id_application=%s',[id_appli['id_application']])
			liste_ip_appli=dictfetchall(cursor)
			for adresse in liste_ip_appli:
				if (adresse['ip'] in tableau_ip)==False:
					tableau_ip.append(adresse['ip'])


	try:
		scanner=Scanner(tableau_ip,id_scan,'plannifie')
		scanner.start()
		sleep(1)

	except Exception as e:
		print str(e)
	




