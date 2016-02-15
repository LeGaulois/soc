#-*- coding: utf-8 -*-
import re
import csv 
from django.db import connection
from math import floor




def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def modifvulns(tableauDict):
	'''
	Fonction permettant le regroupement des vulnérabilites
	Une ligne du tableau = Une vulnerabilites 
	avec la liste des references associes
	'''
	table=[]
	nouveau=True

	#On parcours l'ensemble des elements renvoyes par la base
	for element in tableauDict:
		info=str(element.get("description"))

		#On parcours notre tableau de travail qui contient un tableau de 'id_ref' au lieu d'une seule valeur
		for i in range(len(table)):
			if(table[i].get('description')==info):

				if element.get('ref_nom') not in table[i]['ref_nom']:
					table[i]['ref_nom'].append(element.get('ref_nom'))
				break

			elif(i==len(table)-1):
				nouveau=True

		#Si la vulnerabilite n'est pas presente dans notre tableau de travail, on l'ajoute
		#On remplace la valeur ref_id par un tableau de refs
		if(nouveau==True):	
			nouveau=False
			table.append(element)
			tmp=[element.get('ref_nom')]
			table[-1]['ref_nom']=tmp
							

	return table



def valideIP(adresse):
	try:
		octet=str(adresse).split('.')
		if (len(octet)!=4):
			return False

		else:
			for num in octet:
				if (int(num)>255 or int(num)<0):
					return False
			return True
	except:
		return False


def valideMAC(mac):
	try:
		mac_expr=re.search('([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})',str(mac))

		if(mac_expr==None):
			return False

		else:
			return True

	except:
		return False
		


def prepareGraphRisk(ip):
	dicGraph={}
	total=0
	cursor=connection.cursor()

	try:
		for risk in ('Critical','High','Medium','Low','Info'):
			cursor.execute('SELECT count(criticite) FROM vulnerabilitees  LEFT JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id WHERE ip_hote=%s AND criticite=%s',[ip,risk])
			vuln=dictfetchall(cursor)
			dicGraph[risk]=int(vuln[0].get('count'))
			dicGraph[risk+"nb"]=int(vuln[0].get('count'))
			total+=int(dicGraph.get(risk))

		for risk in ('Critical','High','Medium','Low','Info'):
			dicGraph[risk]=int(int(dicGraph.get(risk))*100/int(total))

	except:
		pass

	return dicGraph

	
def scanEncours(hostID):
	cursor=connection.cursor()
	cursor.execute('SELECT COUNT(host_id) FROM scans WHERE host_id = %s AND etat=\'encours\'', [hostID])
	nb=dictfetchall(cursor)

	if(int(nb[0].get('count'))>0):
		return True

	else:
		return False



def prepareListeSolution(liste_solution):

	for solution in liste_solution:
		liste_liens=solution['infos_complementaires'].split('\n')
		solution['infos_complementaires']=[]

		if len(liste_liens)>0:
			for lien in liste_liens:
				solution['infos_complementaires'].append(lien)


	return liste_solution
			
		


