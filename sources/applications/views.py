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
def liste(request):
	'''
	Cette vue permet de lister toute les applis presentes dans la base
	'''

	cursor=connection.cursor()
	cursor.execute('''SELECT * FROM application ORDER by nom''')
	liste_applis=dictfetchall(cursor)

	cursor.execute('SELECT DISTINCT criticite FROM application')
	liste_criticite=dictfetchall(cursor)
	cursor.close()
	
	#Cas de l'utilisation du filtre
	if request.method == 'POST':
		form = formFiltreApplis(request.POST,criticite=liste_criticite)

		#on verifie que le formulaire est valide 	
		if form.is_valid():
			liste_filtres={}
			liste_filtres['criticite']=form.cleaned_data['criticite']

			requete='''SELECT * FROM application '''
			
			precedent=False
			valeurs_filtres=[]

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
			

			requete+=' ORDER BY nom ASC'
				
			
			cursor=connection.cursor()
           		cursor.execute(str(requete),valeurs_filtres)
			liste_applis=dictfetchall(cursor)
			cursor.close()
			return render(request, 'applications/liste.html', locals())

		#Dans le cas ou la formulaire n'est pas valide
		else:	
			form = formFiltreApplis(criticite=liste_criticite)
			return render(request, 'applications/liste.html', locals())

	#Dans le cas ou la methode est GET, c'est à dire sans passage de paramètres (pas d'utilisation du filtre
	else:
		form = formFiltreApplis(criticite=liste_criticite)

    		return render(request, 'applications/liste.html', locals())


@login_required
@ensure_csrf_cookie
def ajout(request):
	cursor=connection.cursor()
	cursor.execute('SELECT DISTINCT(nom) FROM application')
	noms=dictfetchall(cursor)
	cursor.close()

	if request.method == 'POST':
		form = formEditApplication(request.POST,dic_noms=noms,mode='ajout')
        	
		#On verifie si les donnees recu sont valides
		if form.is_valid():
			nom=form.cleaned_data['nom']
			description=form.cleaned_data['desc']
			criticite=form.cleaned_data['criticite']
			nb_utilisateurs=form.cleaned_data['nb_utilisateurs']
			type_appli=form.cleaned_data['type_appli']
			technologies=form.cleaned_data['technologies']
	
			cursor=connection.cursor()
           		cursor.execute('INSERT INTO application (nom,description,criticite,nb_utilisateurs,type,technologies) VALUES (%s,%s,%s,%s,%s,%s) ',[nom,description,criticite,nb_utilisateurs,type_appli,technologies])
			cursor.close()
			return redirect('applications:liste')

		else:
			return render(request, 'applications/ajout.html', locals())

    # if a GET (or any other method) we'll create a blank form
	else:
		form = formEditApplication(dic_noms=noms,mode='ajout')

    		return render(request, 'applications/ajout.html', locals())


@login_required
@ensure_csrf_cookie
def edit(request,id_application):
	cursor=connection.cursor()
	cursor.execute('SELECT DISTINCT(nom) FROM application')
	noms=dictfetchall(cursor)

	cursor.execute('SELECT * FROM application WHERE id=%s LIMIT 1',[id_application])
	dic_appli=dictfetchall(cursor)	
	cursor.close()

	if request.method == 'POST':
		form = formEditApplication(request.POST,dic=dic_appli,dic_noms=noms,mode='edit')
        	
		#On verifie si les donnees recu sont valides
		if form.is_valid():
			nom=form.cleaned_data['nom']
			description=form.cleaned_data['desc']
			criticite=form.cleaned_data['criticite']
			nb_utilisateurs=form.cleaned_data['nb_utilisateurs']
			type_appli=form.cleaned_data['type_appli']
			technologies=form.cleaned_data['technologies']

			cursor=connection.cursor()
           		cursor.execute('UPDATE application SET nom=%s, description=%s, criticite=%s ,nb_utilisateurs=%s ,type=%s, technologies=%s WHERE id=%s',[nom,description,criticite,nb_utilisateurs,type_appli,technologies,str(id_application)])
			cursor.close()
			return redirect('applications:liste')

		else:
			return render(request, 'applications/edit.html', locals())

    # if a GET (or any other method) we'll create a blank form
	else:
		form = formEditApplication(dic=dic_appli,dic_noms=noms,mode='edit')
		nom=dic_appli[0]['nom']
		app_id=dic_appli[0]['id']

    		return render(request, 'applications/edit.html', locals())


@login_required
def identite(request,id_application):
	cursor=connection.cursor()

	cursor.execute('SELECT * FROM application WHERE id=%s',[id_application])
	appli=dictfetchall(cursor)

	cursor.execute('''SELECT application_hote.ip,hotes.hostname,environnement FROM application_hote 
LEFT JOIN hotes ON application_hote.ip=hotes.ip
WHERE id_application=%s''',[id_application])
	serveurs=dictfetchall(cursor)
	cursor.close()
	taille=len(serveurs)

	return render(request,'applications/identite.html',{'application':appli[0],'serveurs':serveurs,'nb_vm':taille})



@login_required
@ensure_csrf_cookie
def suppression(request,id_application):
	cursor=connection.cursor()

	cursor.execute('SELECT * FROM application WHERE id=%s',[id_application])
	appli=dictfetchall(cursor)
	cursor.close()

	if request.method == 'POST':
		try:
			confirmation=request.POST['confirmation']

		except (KeyError):
			return render(request,'applications/suppression.html',{'erreur':'Cochez pour supprimer','application':appli})

		cursor=connection.cursor()
		cursor.execute('DELETE FROM application WHERE id=%s', [id_application])
		cursor.close()

		return redirect ('applications:liste')

	else:
		return render(request,'applications/suppression.html',{'application':appli})


