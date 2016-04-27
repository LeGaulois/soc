#-*- coding: utf-8 -*-
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect,render
from fonctions import *
from django.db import connection
from formulaires import *
import glob
import mimetypes
from django.utils.encoding import smart_str
from django.contrib.auth.decorators import login_required
from rapportSolutions import creerRapportSolutions
from django.conf import settings
import ConfigParser

BASE=settings.BASE_DIR+'/'
CHEMIN_RAPPORT=BASE+'rapports/rapports/'


@login_required
def getRapport(request,id_scan,type_scan,type_rapport):
    '''
    Cette vue permet d'obtenir un rapport d'évolution ou la rapport Nessus résultant d'un scan
    Les rapports étant générés automatiquement à la fin de chaque scan réussi,
    la fonction test si le rapport existe:
        - si oui le renvoir
        - si non renvoie vers la page approprié
    '''

    try:
        id_scan=int(id_scan)
    except:
        return HttpResponse(status=500)

    chemin=CHEMIN_RAPPORT

    if type_scan=='manuel':
        id_scan_type=id_scan
        chemin+='ScansManuels/'+str(id_scan)+'/'
        
    else:
        cursor=connection.cursor()
        cursor.execute('''SELECT id_scan_plannifie FROM scans_status 
INNER JOIN scan_plannifie_status ON scans_status.id=scan_plannifie_status.id_scans_status
WHERE scans_status.id=%s LIMIT 1''',[id_scan])
        id_dict=dictfetchall(cursor)
        id_scan_type=id_dict[0]['id_scan_plannifie']
        cursor.close()
        chemin+='ScansPlannifies/'+str(id_scan_type)+'/'+str(id_scan)+'/'


    if type_rapport=='nessus':
        liste_fichier=glob.glob(chemin+str(id_scan)+"__*_nessus.pdf")

        if len(liste_fichier)==0:
            return HttpResponse(status=400)

        nom_fichier=liste_fichier[0].split('/')[-1]

    else:
        
        liste_fichier=glob.glob(chemin+str(id_scan)+"__*_evolution.pdf")
    
        if len(liste_fichier)==0:
            return HttpResponse(status=400)

        nom_fichier=liste_fichier[0].split('/')[-1]


    f = open(chemin+nom_fichier, 'r')
    pdf_contents = f.read()
    f.close()
    response = HttpResponse(pdf_contents,content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(nom_fichier)
    response['X-Sendfile'] = smart_str(chemin+nom_fichier)

    return response


@login_required
def getPDF(request):
    '''
    Cette vue permet d'obtenir un rapport de vulnérabilités et solutions pour une liste de serveurs
    La sélection se faisant via appel d'un formulaire 
    '''
    cursor=connection.cursor()
    cursor.execute('SELECT DISTINCT(ip) FROM hotes ORDER BY ip')
    liste_ip=dictfetchall(cursor)

    cursor.execute('SELECT nom,id FROM application')
    liste_appli=dictfetchall(cursor)
    cursor.close()
    
    if request.method == 'POST':
        form = getPDF_formulaire(request.POST,liste_ip=liste_ip,liste_appli=liste_appli)
            
        if form.is_valid():
            nom=form.cleaned_data['nom']
            group_by=form.cleaned_data['group_by']
            liste_adresses=form.cleaned_data['adresses']
            selection=form.cleaned_data['type_selection']
            applis=form.cleaned_data['applis']

            

            if selection=='id_adresses':
                adresses=liste_adresses

            else:
                cursor=connection.cursor()
                adresses=[]
                for appli in applis:
                    for elem in liste_appli:
                        if elem['nom']==appli:
                            id_appli=elem['id']
                            break

                    cursor.execute('SELECT ip FROM application_hote WHERE id_application=%s',[id_appli])
                    hotes_application=dictfetchall(cursor)

                    for ip in hotes_application:
                        adresse=ip['ip']

                        if (adresse in adresses)==False:
                            adresses.append(adresse)
            

                cursor.close()

            pdf=creerRapportSolutions(adresses,group_by,nom)
            response = HttpResponse(pdf,content_type='application/pdf')
            return response

        else:
            return render(request, 'rapports/get_pdf.html', locals())

    else:
        form = getPDF_formulaire(liste_ip=liste_ip,liste_appli=liste_appli)
        return render(request, 'rapports/get_pdf.html', locals())


