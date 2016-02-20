#-*- coding: utf-8 -*-
import requests
import json
import time
import sys
import ConfigParser
import codecs


'''
Cette fonction permet d'appeler des fonctionnalités de Nessus
Elle sera utilisé typiquement pour:
	- lancer de nouveaux scans
	- afficher la liste des policies définis (formulaire) 
'''



#Variables globales
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open("/var/www/html/soc/soc/default.cfg","r","utf-8"))


LOGIN=Config.get('Nessus','Login')
PASSWORD=Config.get('Nessus','Password')
DIRECTORY_ID=Config.get('Nessus','Directory_Id')
VERIFY=str(Config.get('Nessus','Verify_SSL')).lower()

if VERIFY=="false" or VERIFY=="no" or VERIFY=="non" or VERIFY=="0":
	VERIFY=False
else:
	VERIFY=True
 
CUSTOM_TEMPLATE_UUID=Config.get('Nessus','Custom_Template_UUID')


class Nessus(object):

	def __init__(self,adresse='localhost',port=8834):
		self.adresse=adresse
		self.port=port
		self.url='https://'+str(self.adresse)+':'+str(self.port)+'/'
		self.token=None
		self.headers={'Content-Type':'application/json'}


	def envoyer(self,methode, lien, data=None):

		data = json.dumps(data)

		if methode == 'POST':
			r = requests.post(self.url+str(lien), data=data, headers=self.headers, verify=VERIFY)

		elif methode == 'PUT':
			r = requests.put(self.url+str(lien), data=data, headers=self.headers, verify=VERIFY)

		elif methode == 'DELETE':
			r = requests.delete(self.url+str(lien), data=data, headers=self.headers, verify=VERIFY)

		else:
			r = requests.get(self.url+str(lien), params=data, headers=self.headers, verify=VERIFY)


		if r.status_code != 200:
			e = r.json()
			raise Exception(str(e['error']))

		if 'download' in lien:
			return r.content

		if methode!='DELETE':
			return r.json()



	def connexion(self,login=LOGIN,password=PASSWORD):
		'''
		Methode permettant de se logger sur le serveur Nessus
		La methode ajoute le token renvoye par le serveur
		à la variable headers de l'objet Nessus
		'''

		login_data={'username' : str(login), 'password' : str(password)}
		res=self.envoyer('POST','session/', login_data)
		self.token=str(res['token'])
		self.headers['X-Cookie']='token='+str(res['token'])+';'


	def deconnexion(self):
		res=self.envoyer('DELETE','session/')


	def listScan(self):
		'''
		retourne la liste des scans présents dans le repertoire spécifié
		en parametre GLOBAL
		'''

		res=self.envoyer('GET','scans?folder_id='+str(DIRECTORY_ID))
		return res['scans']


	def statusScan(self,scanID):
		'''
		Renvoie le status d'un scan
		C'est à dire si il est demarré,stoppé,...
		'''

		res=self.envoyer('GET','scans/'+str(scanID))

		return res['info']['status']

		
	def listePolicies(self):
		'''
		Retourne la liste des 'policies'
		définient sur Nessus
		'''

		res=self.envoyer('GET','policies/')
		return res


	def listeScanTemplates(self):
		'''
		Retourne la liste des 'templates'
		définient sur Nessus
		'''

		res=self.envoyer('GET','editor/scan/templates/')

		return res

	def listeCustomScanTemplates(self):
		'''
		Retourne la liste des 'templates'
		définient sur Nessus
		'''

		res=self.envoyer('GET','editor/scan/templates/'+CUSTOM_TEMPLATE_UUID)
		return res['settings']['basic']['inputs'][4]['options']
			

	def getRapport(self,scan_id,format_fichier,nom_fichier):
		'''
		Genere un rapport pour le scan specifie en entree
		'''

		if format_fichier=='pdf':
			file_param = {'format':'pdf','chapters':'vuln_by_plugin'}
		else:
			file_param= {'format':'csv'}

		res=self.envoyer('POST','scans/'+str(scan_id)+'/export',file_param)

		num_fichier=res['file']


			
		#Temporisation: on attend que Nessus ait fini de générer le rapport
		res['status']='encours'
		while res['status']!='ready':
			res=self.envoyer('GET','scans/'+str(scan_id)+'/export/'+str(num_fichier)+'/status')
			time.sleep(1)


		rapport = self.envoyer('GET','scans/'+str(scan_id)+'/export/'+str(num_fichier)+'/download?token='+self.token)
		fic=open(str(nom_fichier),'w')
		fic.write(rapport)
		fic.close()


	
	def nouveauScan(self,policy_id,tableau_cible,nom,description=''):
		'''
		Creation d'un nouveau scan dans le repertoire applicatif 'DJANGO'
		Retourne l'id du nouveau scan
		'''

		adresse=tableau_cible[0]

		for i in range(1,len(tableau_cible)):
			adresse+=','+str(tableau_cible[i])

		param_scan={"uuid": CUSTOM_TEMPLATE_UUID,
			"settings": {
				"name": str(nom),
				"description": str(description),
				"folder_id": str(DIRECTORY_ID),
				"policy_id": str(policy_id),
				"text_targets": adresse,
				"file_targets": "",
				"launch": "ONETIME",
				"enabled": False,
				"launch_now": False,
				"emails": "",
				"filter_type": "",
				"filters": []
			}
		}


		res=self.envoyer('POST','scans/',param_scan)
		return res['scan']['id']
			


	def lancerScan(self,scan_id):
		data = self.envoyer('POST', 'scans/'+str(scan_id)+'/launch')







