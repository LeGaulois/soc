#-*- coding: utf-8 -*-
from django.http import HttpResponse,Http404
from django.shortcuts import redirect,render
from fonctions import *
from django.db import connection
from formulaires import *
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie

@login_required
@ensure_csrf_cookie
def ajout(request):
	cursor=connection.cursor()
	cursor.execute('SELECT DISTINCT(nom) FROM application ORDER BY nom ASC')
	applis=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT(ip) FROM hotes')
	adresses=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT environnement FROM hotes ORDER BY environnement ASC')
	liste_env=dictfetchall(cursor)
	cursor.close()

	if request.method == 'POST':

		form = formEditMachine(request.POST,dic_applis=applis,mode='ajout',liste_adresses=adresses)
        	
		if form.is_valid():
			adresse=form.cleaned_data['adresse']
			mac=form.cleaned_data['mac']
			hostname=form.cleaned_data['hostname']
			os=form.cleaned_data['os']
			localisation=form.cleaned_data['localisation']
			type_machine=form.cleaned_data['type_machine']
			info=form.cleaned_data['commentaires']
			commentaires=form.cleaned_data['commentaires']
			selection=form.cleaned_data['type_selection']
		
			if selection=='id_appli':
				liste_application=[form.cleaned_data['appli']]

			else:
				liste_application=form.cleaned_data['backend']
			
			cursor=connection.cursor()
           		cursor.execute('INSERT INTO hotes (ip,mac,hostname,os,localisation,type_machine,commentaires) VALUES (%s,%s,%s,%s,%s,%s,%s) ',[adresse,mac,hostname,os,localisation,type_machine,commentaires])

			if (liste_application[0]!=''):

				for appli in liste_application:
					cursor.execute('SELECT id FROM application WHERE nom=%s LIMIT 1',[appli])
					id_appli=dictfetchall(cursor)

					if (len(id_appli)==1):
						cursor.execute('INSERT INTO application_hote (ip,id_application) VALUES(%s,%s)',[adresse,id_appli[0]['id']])

			cursor.close()
			return redirect ('serveurs:liste')

		else:
			return render(request, 'serveurs/ajout.html', locals())

	else:
		form = formEditMachine(dic_applis=applis,mode='ajout',liste_adresses=adresses)

    		return render(request, 'serveurs/ajout.html', locals())

@login_required
def liste(request):
	'''
	Cette vue permet de lister toute les machines presentes dans la base
	Il s'agit donc de la page d'accueil
	'''

	cursor=connection.cursor()
	cursor.execute('''SELECT * FROM (
SELECT hotes.ip,application.nom,application.criticite,vulnerabilite,localisation,scans_status.etat FROM hotes 
LEFT JOIN application_hote ON hotes.ip=application_hote.ip 
LEFT JOIN application ON application_hote.id_application=application.id
LEFT JOIN scans_status ON (SELECT scan_manuel_status.id_scans_status FROM scan_manuel_hote LEFT JOIN scan_manuel_status ON scan_manuel_hote.id_scan_manuel=scan_manuel_status.id_scan_manuel WHERE scan_manuel_hote.ip_hote=hotes.ip ORDER BY id_scans_status DESC LIMIT 1)=scans_status.id 
ORDER by hotes.ip) p ORDER BY ip''')

	temp_liste_machines=dictfetchall(cursor)
	taille=len(temp_liste_machines)
	liste_machines=[]


	if taille>1:
		precedent=temp_liste_machines[0]
		premier=True

	
		#Sert à obtenir une seule et unique entre par machine
		#Pour les machines ayant un rôle dans plusieurs applis (ex BDD)
		#on regroupe en uen seule entree avec pour nom d'appli Backend: appli1, appli2,....
		for i in range(1,taille):
			test=(temp_liste_machines[i]['ip'])==str(precedent['ip'])

			if test==True:
				if premier==True:
					precedent['nom']='Backend: '+str(temp_liste_machines[i]['nom'])+' ,'+str(precedent['nom'])
					premier=False
				else:
					precedent['nom']+=' ,'+str(temp_liste_machines[i]['nom'])

			if (test==False) or (i==(taille-1)):
				liste_machines.append(precedent)
				precedent=temp_liste_machines[i]
				premier=True

	elif taille==1:
		liste_machines.append(temp_liste_machines[0])
			

	cursor.execute('SELECT DISTINCT os FROM hotes ORDER BY os ASC')
	liste_os=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT type_machine FROM hotes ORDER BY type_machine ASC')
	liste_type=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT criticite FROM application ORDER BY criticite ASC')
	liste_criticite=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT vulnerabilite FROM hotes ORDER BY vulnerabilite ASC')
	liste_vulnerabilite=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT localisation FROM hotes ORDER BY localisation ASC')
	liste_localisation=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT nom FROM application ORDER BY nom ASC')
	liste_appli=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT environnement FROM hotes ORDER BY environnement ASC')
	liste_env=dictfetchall(cursor)
	cursor.close()

	#Cas de l'utilisation du filtre
	if request.method == 'POST':
		form = formFiltreMachines(request.POST,os=liste_os,appli=liste_appli,typ=liste_type,criticite=liste_criticite,localisation=liste_localisation,vulnerabilite=liste_vulnerabilite,environnement=liste_env)

		#on verifie que le formulaire est valide 	
		if form.is_valid():
			liste_filtres={}
			liste_filtres['os']=form.cleaned_data['os']
			liste_filtres['nom']=form.cleaned_data['appli']
			liste_filtres['criticite']=form.cleaned_data['criticite']
			liste_filtres['vulnerabilite']=form.cleaned_data['vulnerabilite']
			liste_filtres['localisation']=form.cleaned_data['localisation']
			liste_filtres['type_machine']=form.cleaned_data['type_machine']
			liste_filtres['environnement']=form.cleaned_data['environnement']

			requete='''SELECT * FROM (
SELECT DISTINCT ON (hotes.ip) hotes.ip,application.nom AS nom,application.criticite AS criticite,vulnerabilite,localisation,scans_status.etat FROM hotes 
LEFT JOIN application_hote ON hotes.ip=application_hote.ip 
LEFT JOIN application ON application_hote.id_application=application.id
LEFT JOIN scan_hote ON hotes.ip=application_hote.ip 
LEFT JOIN scans_status ON scan_hote.id_scan=scans_status.id '''

			#Cette variable sert a l'ajout du mot AND 
			precedent=False
			valeurs_filtres=[]

			#L'ensemble des variables de filtres sont placés dans un tableau qui seran appelé
			#par la session debian au moment de la requête. Cela permet:
			#	- de réduire le code
			#	- de profiter de la protection contre les injections SQL 

			for filtre in liste_filtres.keys():
				valeur_filtre=str(liste_filtres[filtre])

				if(valeur_filtre!=None and valeur_filtre!=''):
					if(precedent==True):
						requete+=" AND "
					else:
						requete+=" WHERE " 

					requete+=str(filtre)+"=%s"
					valeurs_filtres.append(valeur_filtre)
					precedent=True			
			

			requete+=' ORDER BY ip ASC) p ORDER BY ip'
			
			cursor=connection.cursor()
           		cursor.execute(str(requete),valeurs_filtres)
			liste_machines=dictfetchall(cursor)
			cursor.close()
			return render(request, 'serveurs/liste.html', locals())

		#Dans le cas ou la formulaire n'est pas valide
		else:	
			form = formFiltreMachines(os=liste_os,appli=liste_appli,typ=liste_type,criticite=liste_criticite,localisation=liste_localisation,vulnerabilite=liste_vulnerabilite,environnement=liste_env)
			return render(request, 'serveurs/liste.html', locals())

	#Dans le cas ou la methode est GET, c'est à dire sans passage de paramètres (pas d'utilisation du filtre
	else:
		form = formFiltreMachines(os=liste_os,appli=liste_appli,typ=liste_type,criticite=liste_criticite,localisation=liste_localisation,vulnerabilite=liste_vulnerabilite,environnement=liste_env)

    		return render(request, 'serveurs/liste.html', locals())


@login_required
def identite(request,ip):
	'''
	Cette vue affiche la carte d'identite du serveur
	C'est à dire des informations generales sur la machine,
	Ainsi qu'une vue détaille sur les services et vulnérabilitées associées.
	'''

	ip=str(ip)
	cursor=connection.cursor()

	#Requete Info Host
	cursor.execute('SELECT ip,os,mac,hostname,nb_vulnerabilites,nb_services,vulnerabilite,localisation,commentaires,environnement FROM hotes WHERE ip = %s LIMIT 1', [ip])
	infoHost=dictfetchall(cursor)

	#Requete Info application
	cursor.execute('''SELECT nom,description,criticite FROM application_hote
	LEFT JOIN application ON application_hote.id_application=application.id
	WHERE application_hote.ip = %s''', [ip])
	infoAppli=dictfetchall(cursor)

	nb_applis=len(infoAppli)

	if nb_applis>1:
		backend=True
	else:
		backend=None

	#Requete InfoServices
	cursor.execute('SELECT protocole,port,nom,version,type FROM services WHERE ip_hote = %s AND etat=\'open\' AND date_retrait is NULL', [ip])
	infoServices=dictfetchall(cursor)

	#Requetes vulnerabilites
	cursor.execute('''SELECT vulnerabilitees.nom AS vuln_nom, description, criticite, services.nom AS service_nom, refs.nom AS ref_nom FROM vulnerabilitees
INNER JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id  
LEFT JOIN vulns_refs ON vulnerabilitees.id=vulns_refs.vuln_id
LEFT JOIN refs ON refs.id=vulns_refs.ref_id
LEFT JOIN services ON services.id=vuln_hote_service.id_service
WHERE vuln_hote_service.ip_hote=%s AND vuln_hote_service.date_correction IS NULL ORDER BY vulnerabilitees.criticite ASC''', [ip])
	infoVulns=dictfetchall(cursor)
	infoVulns=modifvulns(infoVulns)

	cursor.execute('''SELECT nom,solution,infos_complementaires FROM vuln_hote_service 
LEFT JOIN vulnerabilitees ON vulnerabilitees.id=vuln_hote_service.id_vuln
WHERE ip_hote=%s and solution is NOT NULL and solution!='n/a' ''',[ip])
	infoSolutions=dictfetchall(cursor)
	cursor.close()

	infosSolutions=prepareListeSolution(infoSolutions)
	
	graph=None

	if type(infoHost[0].get('nb_vulnerabilites'))==int:
		if(int(infoHost[0].get('nb_vulnerabilites'))>0):
			graph=prepareGraphRisk(ip)

	return render(request,'serveurs/identite.html',{'liste_services':infoServices,'machine':infoHost,'liste_vulns':infoVulns,'graph':graph, 'appli':infoAppli,'solutions':infoSolutions,'backend':backend})



@login_required
@ensure_csrf_cookie
def edit(request,ip):
	'''
	Cette vue permet d'éditer les informations liées à un serveur
	C'est à dire toutes les informations situées dans la table 'hotes'
	à l'exception du champ 'vulnerabilite' qui est determiner automatiquement
	'''

	cursor=connection.cursor()
	cursor.execute('''SELECT hotes.ip,mac,hostname,os,localisation,type_machine,commentaires,environnement FROM hotes 
WHERE hotes.ip = %s LIMIT 1''', [ip])
	serv=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT(nom) FROM application ORDER BY nom ASC')
	applis=dictfetchall(cursor)

	cursor.execute('''SELECT DISTINCT(nom) FROM application_hote 
LEFT JOIN application ON application.id=application_hote.id_application
WHERE ip=%s ORDER BY nom ASC''',[ip])
	appli_hote=dictfetchall(cursor)
	cursor.close()

    	#Dans le cas d'une methode post, cad modification de l'objet hote 
	if request.method == 'POST':
		form = formEditMachine(request.POST,dic=serv,dic_applis=applis,appli_hote=appli_hote,mode='edit')
        	
		#On verifie si les donnees recu sont valides
		if form.is_valid():
			adresse=form.cleaned_data['adresse']
			mac=form.cleaned_data['mac']
			hostname=form.cleaned_data['hostname']
			os=form.cleaned_data['os']
			#application=form.cleaned_data['appli']
			localisation=form.cleaned_data['localisation']
			type_machine=form.cleaned_data['type_machine']
			info=form.cleaned_data['commentaires']	
			commentaires=form.cleaned_data['commentaires']
			env=form.cleaned_data['environnement']
			selection=form.cleaned_data['type_selection']
		
			if selection=='id_appli':
				liste_application=[form.cleaned_data['appli']]

			else:
				liste_application=form.cleaned_data['backend']

			cursor=connection.cursor()
           		cursor.execute('UPDATE hotes SET ip=%s , mac=%s , hostname=%s , os=%s , localisation=%s,type_machine=%s,commentaires=%s,environnement=%s WHERE ip=%s',[ip,mac,hostname,os,localisation,type_machine,commentaires,env,ip])

			

			cursor.execute('DELETE FROM application_hote WHERE ip=%s',[ip])

			
			if (liste_application[0]!=''):

				for appli in liste_application:
					cursor.execute('SELECT id FROM application WHERE nom=%s LIMIT 1',[appli])
					id_appli=dictfetchall(cursor)

					if (len(id_appli)==1):
						cursor.execute('INSERT INTO application_hote (ip,id_application) VALUES(%s,%s)',[adresse,id_appli[0]['id']])

			cursor.close()
			return redirect ('serveurs:liste')

		else:
			return render(request, 'serveurs/edit.html', locals())

    # if a GET (or any other method) we'll create a blank form
	else:
		form = formEditMachine(dic=serv,dic_applis=applis,mode='edit',appli_hote=appli_hote)

    		return render(request, 'serveurs/edit.html', locals())



@login_required
@ensure_csrf_cookie
def suppression(request,ip):
	cursor=connection.cursor()

	#Requete Info Host
	cursor.execute('''SELECT hotes.ip,mac,hostname,os,localisation,type_machine,commentaires,application.nom AS appli_nom FROM hotes 
	LEFT JOIN application_hote ON application_hote.ip=hotes.ip
	LEFT JOIN application ON application.id=application_hote.id_application
	WHERE hotes.ip = %s LIMIT 1''', [ip])
	infoHost=dictfetchall(cursor)
	cursor.close()

	if request.method == 'POST':
		try:
			confirmation=request.POST['confirmation']

		except (KeyError):
			return render(request,'serveurs/suppression.html',{'erreur':'Cochez pour supprimer','machine':infoHost})

		cursor=connection.cursor()
		cursor.execute('DELETE FROM hotes WHERE ip = %s', [ip])
		cursor.close()
		return redirect ('serveurs:liste')

	else:
		return render(request,'serveurs/suppression.html',{'machine':infoHost})










