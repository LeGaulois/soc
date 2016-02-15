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



def modifListeScan(tableauDict):
	'''
	Fonction permettant le regroupement des ip
	Une ligne du tableau = Un scan
	avec la liste des ip associes
	'''
	table=[]
	nouveau=True

	for element in tableauDict:
		info=str(element.get("vulnsinfo"))

		for i in range(len(table)):
			if(table[i].get('vulnsinfo')==info):

				if element.get('refsname') not in table[i]['refsname']:
					table[i]['refsname'].append(element.get('refsname'))
				break

			elif(i==len(table)-1):
				nouveau=True

		if(nouveau==True):	
			nouveau=False
			table.append(element)
			tmp=[element.get('refsname')]
			table[-1]['refsname']=tmp
							

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



	
def calculCriticite(ip):
	try:
		dicGraph={}	
		cursor=connection.cursor()
		score=0
		ponderation={'Critical':80,'High':20,'Medium':10,'Low':2}


		for risk in ('Critical','High','Medium','Low'):
			cursor.execute('SELECT count(criticite) FROM vulnerabilitees  LEFT JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id WHERE ip_hote=%s AND criticite=%s',[ip,risk])
			vuln=dictfetchall(cursor)
			dicGraph[risk]=int(vuln[0].get('count'))
			score+=dicGraph.get(risk)*ponderation.get(risk)


	
		if int(score)>=80:
			cursor.execute('UPDATE hotes SET vulnerabilite=%s WHERE ip=%s',['haute',ip])

		elif int(score)>50:
			cursor.execute('UPDATE hotes SET vulnerabilite=%s WHERE ip=%s',['moyenne',ip])

		else:
			cursor.execute('UPDATE hotes SET vulnerabilite=%s WHERE ip=%s',['faible',ip])

	except Exception as e:
		print Exception('Calcul Criticite ('+str(hostid)+')= '+str(e))





		

