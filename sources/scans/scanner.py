#-*- coding: utf-8 -*-
import threading
from django.db import connection
from fonctions import dictfetchall,calculCriticite
import datetime
import pytz
import sys
import os
import time
import re
from erreurs import ErreurScanNessus
from transformationRapport import *
from clientNessusRPC import *
from clientNmap import *
from logger import log
from rapports.rapportEvolution import *


BASE='/var/www/html/django/soc/'
CHEMIN_TEMP=BASE+'scans/temp/'
CHEMIN_RAPPORT=BASE+'rapports/rapports/'
CHEMIN_LOGS=BASE+'scans/logs/'

class Scanner(threading.Thread):
	'''
	Permet le lancement de scans Nmap et Nessus
	'''

	def __init__(self,tableau_ip,id_scan,type_scan='manuel'):
		cursor=connection.cursor()

		if type_scan=='manuel':
			cursor.execute('SELECT * FROM scans_manuels WHERE id=%s LIMIT 1',[id_scan])
			dictScan=dictfetchall(cursor)

		else:
			cursor.execute('SELECT * FROM scans_plannifies WHERE id=%s LIMIT 1',[id_scan])
			dictScan=dictfetchall(cursor)

	
		self.policy_id=dictScan[0]['nessus_policy_id']
		self.tableau_ip=tableau_ip
		self.nmap=dictScan[0]['nmap']
		self.nessus=dictScan[0]['nessus']
		self.type_scan=type_scan
		self.nmapOptions=dictScan[0]['nmap_options']
		

		tz = pytz.timezone('Europe/Paris')
		d=datetime.datetime.now()
		self.date_lancement=tz.localize(d)
		self.nom_unique=str(id_scan)+'__'+str(self.date_lancement).replace(' ','_').split('.')[0]


		threading.Thread.__init__(self)
		self.num_thread=self.nom_unique
		self.log=log(CHEMIN_LOGS+'scan.log','scanner.'+str(self.num_thread))

		cursor.execute('INSERT INTO scans_status (date_lancement,etat,type) VALUES (%s,\'encours\',%s)',[self.date_lancement,str(type_scan)])
		cursor.execute('SELECT id FROM scans_status WHERE date_lancement=%s AND etat=%s AND type=%s LIMIT 1',[self.date_lancement,'encours',str(type_scan)])
		id=dictfetchall(cursor)
		self.id_scan=id[0]['id']

		if type_scan=='manuel':
			cursor.execute('INSERT INTO scan_manuel_status (id_scans_status,id_scan_manuel) VALUES(%s,%s)',[str(self.id_scan),id_scan])
			self.CHEMIN_RAPPORT=CHEMIN_RAPPORT+'ScansManuels/'+str(self.id_scan)+'/'
			os.makedirs(self.CHEMIN_RAPPORT)


		else:
			for ip in tableau_ip:
				cursor.execute('INSERT INTO scan_hote (id_scan,ip) VALUES(%s,%s)',[str(self.id_scan),ip])

			cursor.execute('INSERT INTO scan_plannifie_status (id_scan_plannifie,id_scans_status) VALUES(%s,%s)',[id_scan,str(self.id_scan)])

			self.CHEMIN_RAPPORT=CHEMIN_RAPPORT+'ScansPlannifies/'+str(id_scan)+'/'+str(self.id_scan)+'/'

			os.makedirs(self.CHEMIN_RAPPORT)


		cursor.close()


			
	def run(self):
		try:
			if self.nmap==True:
				self.log.ecrire('['+str(self.id_scan)+']= Demmarage du scan nmap','info')
				lancerScanNmap(self.tableau_ip,self.nmapOptions,CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')
				self.log.ecrire('['+str(self.id_scan)+']= Scan nmap realise avec success','info')
				self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nmap','info')
				parserNmapXml(CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml',self.date_lancement,self.id_scan)
				self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nmap reussi','info')
				os.remove(CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')

			if self.nessus==True:
				ScannerNessus=Nessus()
				ScannerNessus.connexion()

				id_nessus=ScannerNessus.nouveauScan(self.policy_id,self.tableau_ip,'scan_'+self.nom_unique,description='Scan DJANGO')
				self.log.ecrire('['+str(self.id_scan)+']= Demarrage du scan Nessus','info')
				ScannerNessus.lancerScan(id_nessus)


				#while (ScannerNessus.statusScan(id_nessus))=='running':
				#	time.sleep(10)
				#Dans le cas ou le scan dure trop longtemps, la session passe en timeout
				#On se reconnecte donc
				while True:
					try:
						if (ScannerNessus.statusScan(id_nessus))!='running':
							break

					except Exception as e:
						if(str(e)=='Invalid Credentials'):
							ScannerNessus.connexion()
						else:
							raise Exception(e)

					time.sleep(10)


				self.log.ecrire('['+str(self.id_scan)+']= Scan Nessus reussi','info')
				ScannerNessus.getRapport(id_nessus,'csv',CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv')

				#On crée une boucle, car lors du traitement du rapport nessus, il peut arriver
				#qu'une vulnerabilite ne soit pas prise en compte, du fait que le service concerne ne soit pas présent en base
				#On relance alors un scan nmap sur l'hote 
				continuer=False
				max_essai=3
				nb_essai=0
				while (continuer==False):
					try:
						self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nessus en cours...','info')
						parserNessusCsv(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv',self.id_scan,True)
						continuer=True
						self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nessus reussi','info')


					except ErreurScanNessus as e:
						adresse=''
						dict_erreur=e.getData()

						for ip in dict_erreur['ip']: 
							adresse+=' '+str(ip)

						optionsNmap='-Pn -sV '

						if len(dict_erreur['ports_tcp'])!=0:
							optionsNmap+='-sS -pT:'
						
							for portTcp in dict_erreur['ports_tcp']:
								optionsNmap+=str(portTcp)
								
								if portTcp!=dict_erreur['ports_tcp'][-1]:
									optionsNmap+=','

						if len(dict_erreur['ports_udp'])!=0:
							if(re.search('-pT:',optionsNmap)!=None):
								optionsNmap+=',U:'

							else:
								optionsNmap+='-pU:'
			
							for portUdp in dict_erreur['ports_udp']:
								optionsNmap+=str(portUdp)
					
								if portUdp!=dict_erreur['ports_udp'][-1]:
									optionsNmap+=','

							optionsNmap+=' -sU'

						
						self.log.ecrire("["+str(self.id_scan)+"]= lancement d'un scan nmap  suite a une erreur d'importation du scan Nessus",'error')
						self.log.ecrire("["+str(self.id_scan)+"]="+str(optionsNmap),"error")
						self.log.ecrire("["+str(self.id_scan)+"]="+str(adresse),"error") 
						nb_essai+=1
						lancerScanNmap(dict_erreur['ip'],str(optionsNmap),CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')
						self.log.ecrire('['+str(self.id_scan)+']= Scan nmap realise avec success','info')
						self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nmap en cours...','info')
						parserNmapXml(CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml',self.date_lancement,self.id_scan)
						self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nmap reussi ;)','info')
						os.remove(CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')

					except Exception as e:
						if(str(e)=='Invalid Credentials'):
							ScannerNessus.connexion()
							nb_essai+=1
							continue
						else:
							pass

					if continuer==False and nb_essai==max_essai+1:
						self.log.ecrire('['+str(self.id_scan)+']= Le scan Nmap a echoué','warning')
						self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nessus en mode Non Strict','warning')
						parserNessusCsv(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv',self.id_scan,False)
						continuer=True
						self.log.ecrire('['+str(self.id_scan)+']= Parsage du rapport Nessus reussi','info')
						#raise ErreurScanNessus('Service(s) non present(s) en base')


				os.remove(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv')

				try:
					self.log.ecrire('['+str(self.id_scan)+']= DL du rapport nessus en cours...','info')
					ScannerNessus.getRapport(id_nessus,'pdf',self.CHEMIN_RAPPORT+str(self.nom_unique)+'_nessus.pdf')
					self.log.ecrire('['+str(self.id_scan)+']= DL du rapport nessus accompli','info')
				except:
					ScannerNessus.connexion()
					ScannerNessus.getRapport(id_nessus,'pdf',self.CHEMIN_RAPPORT+str(self.nom_unique)+'_nessus.pdf')
					self.log.ecrire('['+str(self.id_scan)+']= DL du rapport nessus accompli','info')
				
				ScannerNessus.deconnexion()

				for ip in self.tableau_ip:
					calculCriticite(ip)

			
			self.log.ecrire('['+str(self.id_scan)+']= Generation du rapport devolution en cours...','info')
			
			try:
				creerRapportEvolution(self.nom_unique,self.id_scan,self.type_scan)
				self.log.ecrire('['+str(self.id_scan)+']= Generation du rapport devolution reussi ;)','info')
			except Exception as e:
				self.log.ecrire('['+str(self.id_scan)+']= Erreur lors de la creation du rapport devolution, '+str(e),'warning')	

			tz = pytz.timezone('Europe/Paris')
			d=datetime.datetime.now()
			date_fin=tz.localize(d)

			cursor=connection.cursor()
			cursor.execute('UPDATE scans_status SET etat=\'fini\', date_fin=%s WHERE id=%s', [date_fin,self.id_scan])
			cursor.close()
			self.log.ecrire('['+str(self.id_scan)+']= Scan termine avec success','info')
			self.log.fermer()

		except Exception as f:
			tz = pytz.timezone('Europe/Paris')
			d=datetime.datetime.now()
			date_fin=tz.localize(d)
			cursor=connection.cursor()
			cursor.execute('UPDATE scans_status SET etat=\'abandon\', date_fin=%s WHERE id=%s', [date_fin,self.id_scan])
			cursor.close()
			self.log.ecrire('['+str(self.id_scan)+']= '+str(f),'critical')
			self.log.fermer()
		




		
		
		
