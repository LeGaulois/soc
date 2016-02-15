#-*- coding: utf-8 -*-
import subprocess
from fonctions import valideIP
import re

def lancerScanNmap(tableau_adresse,options,fichier_sortie):
	adresse=''

	for ip in tableau_adresse:
		if valideIP(ip):
			adresse+=' '+str(ip)

	liste_arguments=[adresse,options,fichier_sortie]


	#Contrôle des arguments
	for arg in liste_arguments:
		error=re.search('[;|<>]',str(arg))

		if error!=None:
			raise Exception("Erreur de paramètres Nmap")


	
	subprocess.check_output(['nmap '+str(options)+' --privileged '+str(adresse)+' -oX '+str(fichier_sortie)],shell=True)
