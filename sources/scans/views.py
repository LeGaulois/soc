#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import redirect,render
from fonctions import *
from django.db import connection
from formulaires import *
from clientNessusRPC import *
import os
from scanner import Scanner
import subprocess
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie



@login_required
def status_scans_manuels(request):
	cursor=connection.cursor()

	cursor.execute('''SELECT date_lancement,date_fin,etat,scans_status.id,scan_manuel_status.id_scan_manuel FROM scans_status 
LEFT JOIN scan_manuel_status ON scans_status.id=scan_manuel_status.id_scans_status
WHERE type='manuel'
ORDER BY date_lancement DESC''')
	scans=dictfetchall(cursor)
	

	for elem in scans:
		cursor.execute('''SELECT ip_hote from scan_manuel_hote WHERE id_scan_manuel=%s ''',[elem['id_scan_manuel']])
		temp=dictfetchall(cursor)
		
		liste_ip=[]

		for ip in temp:
			liste_ip.append(ip['ip_hote'])

		elem['ip_hote']=liste_ip
		elem['nb_hotes']=len(liste_ip)

	
	
	cursor.close()

	return render(request,'scans/status_manuels.html',{'scans':scans})


@login_required
def status_scans_plannifies(request):
	cursor=connection.cursor()
	cursor.execute('''SELECT scans_status.date_lancement,scans_status.date_fin,scans_status.etat,scans_plannifies.nom FROM scans_status 
LEFT JOIN scan_plannifie_status ON scans_status.id=scan_plannifie_status.id_scans_status
LEFT JOIN scans_plannifies ON scan_plannifie_status.id_scan_plannifie=scans_plannifies.id
WHERE scans_status.type='plannifie'
ORDER BY scans_status.date_lancement DESC''')
	scans=dictfetchall(cursor)
	cursor.close()

	return render(request,'scans/status_plannifies.html',{'scans':scans})


@login_required
def liste_scans_plannifies(request):
	cursor=connection.cursor()
	cursor.execute('''SELECT * FROM (
SELECT DISTINCT ON(scans_plannifies.id) nom,description,nmap,nessus,nessus_policy_id,scans_plannifies.id,scans_status.etat FROM scans_plannifies 
LEFT JOIN scan_plannifie_status ON scans_plannifies.id=scan_plannifie_status.id_scan_plannifie
LEFT JOIN scans_status ON (SELECT scan_plannifie_status.id_scans_status FROM scan_plannifie_status
LEFT JOIN scans_plannifies ON scans_plannifies.id=scan_plannifie_status.id_scan_plannifie ORDER BY scans_status.id DESC LIMIT 1)=scans_status.id) p
''')
	scans_plannifies=dictfetchall(cursor)
	cursor.close()

	return render(request,'scans/liste_scans_plannifies.html',{'scans':scans_plannifies})	
	



@login_required
@ensure_csrf_cookie
def ajoutScanPlannifie(request):
	cursor=connection.cursor()
	cursor.execute('SELECT DISTINCT(ip) FROM hotes ORDER BY ip')
	liste_ip_existantes=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT(nom) FROM scans_plannifies')
	liste_noms=dictfetchall(cursor)

	cursor.execute('SELECT nom,id FROM application')
	liste_appli=dictfetchall(cursor)

	ScannerNessus=Nessus()
	ScannerNessus.connexion()
	dict_policies=ScannerNessus.listePolicies()
	liste_policies=dict_policies['policies']
	ScannerNessus.deconnexion()
	cursor.close()

	if request.method == 'POST':
		form = scanPlannifie(request.POST,liste_ip_existantes=liste_ip_existantes,liste_noms=liste_noms,liste_policies=liste_policies,mode='ajout',liste_appli=liste_appli)
        	
		if form.is_valid():
			nom=form.cleaned_data['nom']
			desc=form.cleaned_data['description']
			nmap=form.cleaned_data['nmap']
			nmapOptions=form.cleaned_data['nmapOptions']
			nessus=form.cleaned_data['nessus']
			policy=form.cleaned_data['nessus_policy']
			adresses=form.cleaned_data['adresses']
			jours=form.cleaned_data['jours']
			applis=form.cleaned_data['applis']


			jours_execution=''

			for j in jours:
				jours_execution+=str(j)
				if j!=jours[-1]:
					jours_execution+=';'

			cursor=connection.cursor()
			cursor.execute('INSERT INTO scans_plannifies (nom,description,nmap,nmap_options,nessus,nessus_policy_id,jours_execution) VALUES(%s,%s,%s,%s,%s,%s,%s)',[nom,desc,nmap,nmapOptions,nessus,policy,jours_execution])
			cursor.execute('SELECT id FROM scans_plannifies ORDER BY id DESC LIMIT 1')
			id=dictfetchall(cursor)[0]['id']


			if len(adresses)>0:
				for ip in adresses:
					cursor.execute('INSERT INTO scan_plannifie_hote (id_scan_plannifie,ip_hote) VALUES(%s,%s)',[id,ip])


			elif len(applis)>0:
				for appli in applis:

					for elem in liste_appli:
						if elem['nom']==appli:
							id_appli=elem['id']
							break

					cursor.execute('INSERT INTO scan_plannifie_application (id_scan_plannifie,id_application) VALUES(%s,%s)',[id,id_appli])

				
			cursor.close()

			return redirect ('scans:liste_scans_plannifies')

		else:
			return render(request, 'scans/ajout_plannifie.html', locals())


	else:
		form = scanPlannifie(liste_ip_existantes=liste_ip_existantes,liste_noms=liste_noms,liste_policies=liste_policies,mode='ajout',liste_appli=liste_appli)

    		return render(request, 'scans/ajout_plannifie.html', locals())




@login_required
@ensure_csrf_cookie
def editScanPlannifie(request,id_scan_plannifie):
	cursor=connection.cursor()
	cursor.execute('SELECT DISTINCT(ip) FROM hotes ORDER BY ip')
	liste_ip_existantes=dictfetchall(cursor)

	cursor.execute('SELECT ip_hote FROM scan_plannifie_hote WHERE id_scan_plannifie=%s',[id_scan_plannifie])
	liste_ip_selectionnees=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT(nom) FROM scans_plannifies')
	liste_noms=dictfetchall(cursor)

	cursor.execute('SELECT * FROM scans_plannifies WHERE id=%s LIMIT 1', [id_scan_plannifie])
	infoScan=dictfetchall(cursor)
	infoScan=infoScan[0]

	cursor.execute('''SELECT application.id,nom FROM scan_plannifie_application
LEFT JOIN application ON application.id=id_application
WHERE id_scan_plannifie=%s''',[id_scan_plannifie])
	liste_applis_selectionnees=dictfetchall(cursor)

	cursor.execute('SELECT nom,id FROM application ORDER BY nom ASC')
	liste_appli=dictfetchall(cursor)


	ScannerNessus=Nessus()
	ScannerNessus.connexion()
	dict_policies=ScannerNessus.listePolicies()
	liste_policies=dict_policies['policies']
	ScannerNessus.deconnexion()
	cursor.close()

	if request.method == 'POST':
		form = scanPlannifie(request.POST,mode='edit',liste_ip_selectionnees=liste_ip_selectionnees,liste_ip_existantes=liste_ip_existantes,liste_noms=liste_noms,liste_policies=liste_policies,scan=infoScan,liste_applis_selectionnees=liste_applis_selectionnees,liste_appli=liste_appli)
        	
		if form.is_valid():
			nom=form.cleaned_data['nom']
			desc=form.cleaned_data['description']
			nmap=form.cleaned_data['nmap']
			nmapOptions=form.cleaned_data['nmapOptions']
			nessus=form.cleaned_data['nessus']
			policy=form.cleaned_data['nessus_policy']
			adresses=form.cleaned_data['adresses']
			jours=form.cleaned_data['jours']
			applis=form.cleaned_data['applis']
			selection=form.cleaned_data['type_selection']
			jours_execution=''

			cursor=connection.cursor()
			for j in jours:
				jours_execution+=str(j)
				if j!=jours[-1]:
					jours_execution+=';'

			cursor.execute('UPDATE scans_plannifies SET nom=%s,description=%s,nmap=%s,nmap_options=%s,nessus=%s,nessus_policy_id=%s,jours_execution=%s WHERE id=%s',[nom,desc,nmap,nmapOptions,nessus,policy,jours_execution,id_scan_plannifie])

			cursor.execute('DELETE FROM scan_plannifie_hote WHERE id_scan_plannifie=%s',[id_scan_plannifie])
			cursor.execute('DELETE FROM scan_plannifie_application WHERE id_scan_plannifie=%s',[id_scan_plannifie])

			if selection=='id_adresses':
				for ip in adresses:
					cursor.execute('INSERT INTO scan_plannifie_hote (id_scan_plannifie,ip_hote) VALUES(%s,%s)',[id_scan_plannifie,ip])

			elif selection=='id_applis':
				for appli in applis:
					for elem in liste_appli:
						if elem['nom']==appli:
							id_appli=elem['id']
							break

					cursor.execute('INSERT INTO scan_plannifie_application (id_scan_plannifie,id_application) VALUES(%s,%s)',[id_scan_plannifie,id_appli])
			

			cursor.close()
			return redirect ('scans:liste_scans_plannifies')

		else:
			return render(request, 'scans/edit_plannifie.html', locals())


	else:
		form = scanPlannifie(mode='edit',liste_ip_selectionnees=liste_ip_selectionnees,liste_ip_existantes=liste_ip_existantes,liste_noms=liste_noms,liste_policies=liste_policies,scan=infoScan,liste_applis_selectionnees=liste_applis_selectionnees,liste_appli=liste_appli)

    		return render(request, 'scans/edit_plannifie.html', locals())
	
	


	
@login_required
@ensure_csrf_cookie
def suppression(request,id):
	cursor=connection.cursor()

	#Requete Info Host
	cursor.execute('SELECT * FROM scans_plannifies WHERE id=%s LIMIT 1', [id])
	infoScan=dictfetchall(cursor)
	cursor.close()

	if request.method == 'POST':
		try:
			confirmation=request.POST['confirmation']

		except (KeyError):
			return render(request,'scans/suppression.html',{'erreur':'Cochez pour supprimer','scans':infoScan})

		cursor=connection.cursor()
		cursor.execute('DELETE FROM scans_plannifies WHERE id = %s', [id])
		cursor.close()
		return redirect ('scans:liste_scans_plannifies')

	else:
		return render(request,'scans/suppression.html',{'scans':infoScan})



@login_required
@ensure_csrf_cookie
def ajoutScanManuel(request, ip=None):
	cursor=connection.cursor()
	cursor.execute('SELECT DISTINCT(ip) FROM hotes ORDER BY ip')
	liste_ip=dictfetchall(cursor)


	cursor.execute('SELECT nom,id FROM application')
	liste_appli=dictfetchall(cursor)
	
	ScannerNessus=Nessus()
	ScannerNessus.connexion()
	dict_policies=ScannerNessus.listePolicies()
	liste_policies=dict_policies['policies']
	ScannerNessus.deconnexion()
	ip=ip
	cursor.close()
	
	if request.method == 'POST':
		form = scanManuel(request.POST,liste_ip=liste_ip,liste_policies=liste_policies,ip=ip,liste_appli=liste_appli)
        	
		if form.is_valid():
			type_scan='manuel'
			Nmap=form.cleaned_data['nmap']
			nmapOptions=form.cleaned_data['nmapOptions']
			nessus=form.cleaned_data['nessus']
			nessusPolicy_id=form.cleaned_data['nessus_policy']
			

			if ip==None:
				liste_ip=form.cleaned_data['adresses']
				selection=form.cleaned_data['type_selection']
				applis=form.cleaned_data['applis']

			else:
				liste_ip=[ip]
				selection=None				


			cursor=connection.cursor()
			cursor.execute('INSERT INTO scans_manuels (nmap,nmap_options,nessus,nessus_policy_id) VALUES(%s,%s,%s,%s)',[Nmap,nmapOptions,nessus,nessusPolicy_id])
			cursor.execute('SELECT id FROM scans_manuels ORDER BY id DESC LIMIT 1')
			id_scan=dictfetchall(cursor)[0]['id']


			if selection=='id_applis':
				liste_ip=[]
				for appli in applis:
					for elem in liste_appli:
						if elem['nom']==appli:
							id_appli=elem['id']
							break

					cursor.execute('SELECT ip FROM application_hote WHERE id_application=%s',[id_appli])
					hotes_application=dictfetchall(cursor)

					for ip in hotes_application:
						adresse=ip['ip']

						if (adresse in liste_ip)==False:
							liste_ip.append(adresse)
			
			for adresse in liste_ip:	
				cursor.execute('INSERT INTO scan_manuel_hote (ip_hote,id_scan_manuel) VALUES(%s,%s)',[adresse,id_scan])

			try:
				scanner=Scanner(liste_ip,id_scan,type_scan)
				scanner.start()

			except Exception as e:
				cursor.close()
				return HttpResponse(status=500)

			
			cursor.close()
			return redirect('scans:status_scans_manuels')

		else:
			return render(request, 'scans/ajout_manuel.html', locals())


	else:
		form = scanManuel(liste_ip=liste_ip,liste_policies=liste_policies,ip=ip,liste_appli=liste_appli)

    		return render(request, 'scans/ajout_manuel.html', locals())



@login_required
def demarrerScanPlannifie(request,id_scan):
	cursor=connection.cursor()
	cursor.execute('SELECT ip_hote FROM scan_plannifie_hote WHERE id_scan_plannifie=%s',[id_scan])
	liste_ip=dictfetchall(cursor)	

	tableau_ip=[]

	for ip in liste_ip:
		tableau_ip.append(ip['ip_hote'])

	del liste_ip


	cursor.execute('SELECT id_application FROM scan_plannifie_application WHERE id_scan_plannifie=%s',[id_scan])
	liste_id_appli=dictfetchall(cursor)
	
	for id_appli in liste_id_appli:
		cursor.execute('SELECT ip FROM application_hote WHERE id_application=%s',[id_appli['id_application']])
		liste_ip_appli=dictfetchall(cursor)

		for adresse in liste_ip_appli:
			if (adresse['ip'] in tableau_ip)==False:
				tableau_ip.append(adresse['ip'])


	cursor.execute('SELECT * FROM scans_plannifies WHERE id=%s LIMIT 1',[id_scan])
	scan=dictfetchall(cursor)
	cursor.close()

	try:
		scanner=Scanner(tableau_ip,id_scan,'plannifie')
		scanner.start()

	except Exception as e:
		return HttpResponse(status=500)

	return redirect('scans:status_scans_plannifies')



@login_required
def parametresScanManuel(request,id_scan):
	cursor=connection.cursor()
	cursor.execute('''SELECT ip_hote,nmap,nmap_options,nessus,nessus_policy_id,etat,scan_manuel_status.id_scans_status FROM scans_manuels
LEFT JOIN scan_manuel_status ON scans_manuels.id=scan_manuel_status.id_scan_manuel
LEFT JOIN scan_manuel_hote ON scan_manuel_hote.id_scan_manuel=scans_manuels.id
LEFT JOIN scans_status ON scans_status.id=scan_manuel_status.id_scans_status
WHERE scan_manuel_status.id_scans_status=%s''',[id_scan])
	infoScan=dictfetchall(cursor)
	cursor.close()
	scan=infoScan

	type_scan='manuel'
	nessus='nessus'
	autre='evolution'

	adresses=''
	last=scan[-1]['ip_hote']

	for ip in scan:
		adresses+=str(ip['ip_hote'])
	
		if ip['ip_hote'] != last:
			adresses+=', '

	scan=scan[0]
	scan['ip_hote']=adresses

	return render(request,'scans/scans_manuels_description.html',locals())


def scanApplication(request,id_appli):
	'''
	Permet d elancer un scan sur tous les serveur
	dune application donnee
	'''
	
	cursor=connection.cursor()
	cursor.execute('SELECT ip FROM application_hote WHERE id_application=%s',[id_application])
	liste_ip=dictfetchall(cursor)
	cursor.close()

	if len(liste_ip)>0:
		liste=[]
		for ip in liste_ip:
			liste.append(ip['ip'])

		try:
			scanner=Scanner(liste,id_scan,type_scan)
			scanner.start()

		except Exception as e:
			return HttpResponse(status=500)

			return redirect('scans:status_scans_manuels')

@login_required
def historiqueScanPlannifie(request,id_scan_plannifie):
	cursor=connection.cursor()
	cursor.execute('''SELECT etat,date_lancement,date_fin,scans_status.id FROM scans_status
LEFT JOIN scan_plannifie_status ON scan_plannifie_status.id_scans_status=scans_status.id
WHERE id_scan_plannifie=%s ORDER BY date_lancement DESC''',[id_scan_plannifie])
	histoScan=dictfetchall(cursor)
	cursor.close()

	type_scan='plannifie'
	nessus='nessus'
	autre='evolution'

	return render(request,'scans/historique_scan_plannifie.html',locals())

		
	
	




