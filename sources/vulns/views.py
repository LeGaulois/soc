#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import redirect,render
from fonctions import *
from django.db import connection
from formulaires import *
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie



@login_required
def stats_vulns(request):
    cursor=connection.cursor()

    #TOP10
    cursor.execute('''SELECT id,nom,description,criticite, (SELECT count(DISTINCT(ip_hote)) from vuln_hote_service WHERE id=id_vuln and date_correction IS NULL) AS nb FROM vulnerabilitees WHERE criticite!='Info' ORDER BY nb DESC LIMIT 10''')
    top10_vuln_data=dictfetchall(cursor)
    top_10_vuln={'data':top10_vuln_data,'titre':'TOP 10 Vulnérabilitées'}

    top_10_vuln['data']=None if len(top10_vuln_data)!=10 else top10_vuln_data
    
    #Graph radar
    #1) la première famille du graphique a pour but de montrer pour chaque catégorie 
    #   le nombre de vulnérabilitées présentes
    cursor.execute('''SELECT refs.type AS categorie, COUNT(refs.type) AS nb FROM refs
        JOIN (SELECT COUNT(ip_hote),refs.id FROM refs
                LEFT JOIN vulns_refs ON refs.id=vulns_refs.ref_id
                LEFT JOIN vulnerabilitees ON vulns_refs.vuln_id=vulnerabilitees.id
                LEFT JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id
                WHERE vuln_hote_service.date_correction IS NULL GROUP BY refs.id
        ) count
        ON refs.id=count.id AND count>0
        WHERE refs.type IS NOT NULL
        GROUP BY refs.type''')
    refs_categorie=dictfetchall(cursor)

    #2) la seconde categorie a pour but de montrer pour chaque catégorie
    #   la somme de (CVE_1:>nb_hotes_touches) + (CVE_2>nb_hotes_touches)
    cursor.execute("""
        SELECT COUNT(ip_hote) AS nb,refs.type AS categorie FROM refs
        LEFT JOIN vulns_refs ON refs.id=vulns_refs.ref_id
        LEFT JOIN vulnerabilitees ON vulns_refs.vuln_id=vulnerabilitees.id
        LEFT JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id
        WHERE vuln_hote_service.date_correction IS NULL AND refs.type IS NOT NULL
        GROUP BY refs.type
    """)
    refs_nb_vulns=dictfetchall(cursor)
    cursor.close()


    spyder=[]    

    noms_categories=[
        "Vulnerabilities with exploits",
        "Code execution",
        "Overflows",
        "CSRF",
        "File inclusion",
        "Gain privilege",
        "Sql injection",
        "Cross Site Scripting",
        "Directory traversal",
        "Memory corruption",
        "Http response splitting",
        "Bypass a restriction or similar",
        "Obtain Information",
        "Denial of service",
        "Execute Code"
    ]

    for categorie in noms_categories:
        spyder.append({
            "nom":categorie,
            "nb_refs":int(get_value_from_liste_dict(refs_categorie,'categorie',str(categorie),'nb')),
            "nb_vulns":int(get_value_from_liste_dict(refs_nb_vulns,'categorie',str(categorie),'nb'))
        })

    return render(request,'vulns/statistiques.html',{'top_10_vuln':top_10_vuln,'spyder':spyder})



@login_required
def details(request,vuln_id):
    cursor=connection.cursor()
    cursor.execute('SELECT * FROM vulnerabilitees WHERE id=%s LIMIT 1',[vuln_id])
    vuln=dictfetchall(cursor)

    vuln=prepareListeSolution(vuln)

    cursor.execute('''SELECT vuln_hote_service.ip_hote,services.protocole,services.port,retour_vuln FROM vuln_hote_service
    INNER JOIN services ON services.id=vuln_hote_service.id_service
    WHERE id_vuln=%s''',[vuln_id])
    hotes=dictfetchall(cursor)

    cursor.execute('''SELECT DISTINCT(refs.nom) FROM refs 
    INNER JOIN vulns_refs ON refs.id=vulns_refs.ref_id
    INNER JOIN vulnerabilitees ON vulnerabilitees.id=vulns_refs.vuln_id 
    WHERE vulnerabilitees.id=%s''',[vuln_id])
    temp=dictfetchall(cursor)
    cursor.close()

    if len(temp)==0:
        liste_refs=None

    else:
        liste_refs=[]

        for ref in temp:
            liste_refs.append({
                    'nom':ref['nom'],
                    'url':ref['nom'].replace('-','_')
            })

    if len(hotes)>0:
        vuln[0]['nb']=len(hotes)

    return render(request,'vulns/details.html',{'vuln':vuln,'hotes':hotes,'liste_refs':liste_refs})




@login_required
def liste(request):
    cursor=connection.cursor()
    cursor.execute('SELECT id,nom,criticite,synopsis FROM vulnerabilitees')
    liste_vulns=dictfetchall(cursor)

    cursor.execute('SELECT DISTINCT(criticite) FROM vulnerabilitees')
    liste_criticite=dictfetchall(cursor)
    cursor.close()
    

    if request.method == 'POST':
        form = formFiltreVulns(request.POST,criticite=liste_criticite)

     
        if form.is_valid():
            liste_filtres={}
            liste_filtres['criticite']=form.cleaned_data['criticite']

            requete='''SELECT id,nom,criticite,synopsis FROM vulnerabilitees '''
            
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
                
            
            cursor=connection.cursor()
            cursor.execute(str(requete),valeurs_filtres)
            liste_vulns=dictfetchall(cursor)
            cursor.close()
            return render(request, 'vulns/liste.html', locals())


        else:    
            form = formFiltreVulns(criticite=liste_criticite)
            return render(request, 'vulns/liste.html', locals())


    else:
        form = formFiltreVulns(criticite=liste_criticite)
        return render(request, 'vulns/liste.html', locals())


@login_required
def details_cve(request,cve):
    """
    Cette fonction permet de lister toutes les CVE
    """

    cve=cve.replace('_','-')
    cursor=connection.cursor()
    cursor.execute('SELECT * from refs WHERE nom=%s',[cve])
    cve_details=dictfetchall(cursor)

    if len(cve_details)==0:
        return HTTPResponse(status=404)

    cursor.execute("""
        SELECT vuln_hote_service.ip_hote,protocole,port,services.nom FROM refs
        INNER JOIN vulns_refs ON vulns_refs.ref_id=refs.id
        INNER JOIN vulnerabilitees ON vulnerabilitees.id=vulns_refs.vuln_id
        INNER JOIN vuln_hote_service ON vulnerabilitees.id=id_vuln
        INNER JOIN services ON vuln_hote_service.id_service=services.id     
        WHERE refs.nom=%s AND date_correction IS NULL ORDER BY ip_hote ASC
    """,[cve])

    hotes_associes=dictfetchall(cursor)

    cursor.close()

    return render(request, 'vulns/details_cve.html',{'cve':cve_details,'hotes_associes':hotes_associes})


@login_required
def liste_cve_famille(request,type_cve):
    '''
    Retourne la liste des CVE associés à une famille
    (injection SQL, execution code)
    '''

    type_cve=type_cve.replace('_',' ')

    cursor=connection.cursor()
    cursor.execute('''
    SELECT refs.id,nom,cvss_score,count.count FROM refs
        JOIN (SELECT COUNT(ip_hote),refs.id FROM refs
                LEFT JOIN vulns_refs ON refs.id=vulns_refs.ref_id
                LEFT JOIN vulnerabilitees ON vulns_refs.vuln_id=vulnerabilitees.id
                LEFT JOIN vuln_hote_service ON vuln_hote_service.id_vuln=vulnerabilitees.id
                WHERE vuln_hote_service.date_correction IS NULL GROUP BY refs.id
        ) count
        ON refs.id=count.id AND count>0
        WHERE refs.type=%s ORDER BY nom ASC
    ''',[type_cve])
    liste_cve=dictfetchall(cursor)

    for cve in liste_cve:
        cve['nom_url']=cve['nom'].replace('-','_')

    if len(liste_cve)==0:
        return HTTPResponse(status=404)

    return render(request, 'vulns/liste_cve_famille.html',{'type_cve':type_cve,'liste_cve':liste_cve,'type':type_cve} )
  

    
        

    
