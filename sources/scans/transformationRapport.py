#-*- coding: utf-8 -*-
from xml.dom.minidom import parse, parseString
import csv
from django.db import connection
from fonctions import dictfetchall,getIP
import datetime
import pytz
from erreurs import ErreurScanNessus
import re
from cvedetails import get_CVE_details


def getPlagePorts(listeArgumentsNmap):
    '''
    Cette fonction permet a partir d'une liste d'arguments
    (ex: -p80,443,T:21,22,U:53)
    De renvoyer 2 tableaux avec la liste des ports scannes
    '''
    protocole={
        'all':[('-p\d+','-p'),('-p ','-p')],
        'tcp':[('-pT','-pT:'),(',T:',',T:')],
        'udp':[('-pU','-pU:'),(',U:',',U:')]
    }

    ports_tcp_scannes=[]
    ports_udp_scannes=[]

    for elem in listeArgumentsNmap:
        for proto in protocole.keys():
            for parser in protocole[proto]:
                if re.search(parser[0],elem)!=None:
                    temp=elem.split(parser[1])[1].split(',')

                    for plage in temp:
                        if re.search('-',plage)!=None:
                            try:
                                print 'plage'
                                port_debut=int(plage.split('-')[0])
                                port_fin=int(plage.split('-')[1])

                                for port in range(port_debut,port_fin+1):

                                    if proto=='tcp':
                                        ports_tcp_scannes.append(int(port))
                                    elif proto=='udp':
                                        ports_udp_scannes.append(int(port))
                                    else:
                                        ports_udp_scannes.append(int(port))
                                        ports_tcp_scannes.append(int(port))
                            except ValueError:
                                #dans le cas où la plage corresponde à un parser
                                #d'un autre protocole (ex: ,U: ou ,T:)
                                break
                              
                        else:
                            try:
                                if proto=='tcp':
                                    ports_tcp_scannes.append(int(plage))
                                elif proto=='udp':
                                        ports_udp_scannes.append(int(plage))
                                else:
                                    ports_udp_scannes.append(int(plage))
                                    ports_tcp_scannes.append(int(plage))

                            except ValueError:
                                #dans le cas où la plage corresponde à un parser
                                #d'un autre protocole (ex: ,U: ou ,T:)
                                break


    return ports_udp_scannes,ports_tcp_scannes
       



def parserNmapXml(fichierXML,scans_status_id):
    '''
    fonction permet de parser le rapport csv dun scan nmap
    et de l'importer dans une BDD
    La fonction met aussi a jour la table service
    Les anciens services seront toujours present mais avec une date de suppression non NULL  
    '''

    cursor=connection.cursor()
    dom = parse(fichierXML)

    cursor.execute('SELECT date_lancement FROM scans_status WHERE id=%s LIMIT 1',[scans_status_id])
    rep=dictfetchall(cursor)
    date_scan=rep[0]['date_lancement']

    #On recupere dans un premier temps les arguments
    args=dom.getElementsByTagName('nmaprun')[0].getAttribute('args')
    
    #Rappel, le scan nmap est lance a partir d'une fonction
    #On connait donc la forme exact de la commande
    #ex: nmap -A -sS -sU -&#45;privileged -oX exemple.xml
    liste_args=args.split('-&')[0].split('nmap ')[1].split(' ')
    [ liste_args.remove(elem) for elem in liste_args if len(elem)==0]


    #Dans le cas ou on effectue un scan nmap uniquement sur certains ports
    #Ces 2 listes permettront de gérer la suppression des services dans la base
    #ex ne pas supprimer un service en base si on n'a pas scanné le port en question
    ports_udp_scannes,ports_tcp_scannes=getPlagePorts(liste_args)


    for host in dom.getElementsByTagName('host'):
    
        #On recupere les attributs de l'hôte
        host_dict={}

        for addr in host.getElementsByTagName('address'):
            if addr.getAttribute('addrtype')=='ipv4':
                host_dict['ip']=addr.getAttribute('addr')

            elif addr.getAttribute('addrtype')=='mac':
                host_dict['mac']=addr.getAttribute('addr')

        host_dict['hostname']=None

        for hostname in host.getElementsByTagName('hostnames'):
            for name in hostname.getElementsByTagName('hostname'):
                host_dict['hostname']=str(name.getAttribute('name'))


        host_dict['os']=''
        host_dict['famille_os']=''

        #dans le cas ou l'utilisateur a demandé une detection d'OS (-O)
        #ou une detection de version et d'OS (-A)
        if '-A' in liste_args or '-O' in liste_args:
            try:
                host_dict['os']=host.getElementsByTagName('osmatch')[0].getAttribute('name')
                host_dict['famille_os']=host.getElementsByTagName('osclass')[0].getAttribute('osfamily')

            except:
                pass    
             


            #On s'assure que le nom de l'os ne soit pas trop grand
            #En effet, dans le cas où plusieurs possibilitées existe, nmap les mets les unes a la suite des autres
            #ex: Microsoft Windows 7 SP0 - SP1, Windows Server 2008 SP1, Windows 8, or Windows 8.1 Update 1
            if len(host_dict['os'])>40:
                host_dict['os']=host_dict['os'].split(',')[0]

                if len(host_dict['os'])>40:
                    host_dict['os']=host_dict['os'].split('or')[0]
            
        #On verifie si une entree pour cet hote existe deja dans la base                        
        cursor.execute('SELECT count(ip) from hotes WHERE ip=%s',[host_dict['ip']])
        nb_hotes=dictfetchall(cursor)


        if(int(nb_hotes[0]['count'])>0):
            cursor.execute('SELECT id FROM services WHERE ip_hote=%s AND date_retrait is NULL',[host_dict['ip']])
            id_existant=dictfetchall(cursor)
            id_initiaux=[]

            for id in id_existant:
                id_initiaux.append(id['id'])

            host_dict['nb_services']=0
        
            if '-A' in liste_args or '-O' in liste_args:
                if host_dict['os']!='' and host_dict['famille_os']!='':
                    cursor.execute('UPDATE hotes SET os=%s, famille_os=%s WHERE ip=%s',[host_dict['os'],host_dict['famille_os'],host_dict['ip']])
            

        else:
            continue

            #Possibilité d'ajouter automatiquement le nouvel hôte en base
            #Decommentez pour activer
            """
            id_initiaux=[]
            host_dict['nb_services']=0
                
            cursor.execute('INSERT INTO hotes (ip,mac,hostname,os,famille_os,nb_services) VALUES (%s,%s,%s,%s,%s,%s)',[host_dict['ip'],host_dict['mac'],host_dict['hostname'],host_dict['os'],host_dict['famille_os'],host_dict['nb_services']])
            """
            ####

        del nb_hotes
        #On cherche ensuite les services associes a la machine

        for service in host.getElementsByTagName('port'):
            dic={'etat':None,'nom':None,'type':None,'version':None}
            dic['protocole']=service.getAttribute('protocol')
            dic['port']=service.getAttribute('portid')
    
            for child in service.childNodes:
                if child.nodeName=='state':
                    dic['etat']=child.getAttribute('state')

                elif child.nodeName=='service':
                    dic['nom']=child.getAttribute('product')
                    dic['type']=child.getAttribute('name')
                    dic['version']=child.getAttribute('version')


            if dic['etat']=='closed':
                continue

            host_dict['nb_services']+=1


            #On verifie si le service est deja repertorie
            cursor.execute('SELECT count(id) from services WHERE protocole=%s AND port=%s AND etat=%s AND nom=%s AND type=%s AND version=%s AND ip_hote=%s AND date_retrait is NULL',[dic['protocole'],dic['port'],dic['etat'],dic['nom'],dic['type'],dic['version'],host_dict['ip']])
            nb_services=dictfetchall(cursor)


            if nb_services[0]['count']==0:
                cursor.execute('INSERT INTO services (protocole,port,etat,nom,type,version,ip_hote,date_ajout) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',[dic['protocole'],dic['port'],dic['etat'],dic['nom'],dic['type'],dic['version'],host_dict['ip'],date_scan])

            else:
                cursor.execute('SELECT id from services WHERE protocole=%s AND port=%s AND etat=%s AND nom=%s AND type=%s AND version=%s AND ip_hote=%s AND date_retrait is NULL LIMIT 1',[dic['protocole'],dic['port'],dic['etat'],dic['nom'],dic['type'],dic['version'],host_dict['ip']])
                id=dictfetchall(cursor)
                id_initiaux.remove(id[0]['id'])


        #On met a jour la table 'services'
        #Si date_retrait est null cela veut dire que
        #le service est tjrs actif
        for srv in id_initiaux:
            if len(ports_tcp_scannes)!=0 or len(ports_udp_scannes)!=0:
                cursor.execute("SELECT protocole,port FROM services WHERE id=%s LIMIT 1",[srv])
                rep=dictfetchall(cursor)

                if int(rep[0]['port'])==0:
                    continue

                #Si le port en question fait parti des ports scannes
                if rep[0]['protocole']=='udp' and int(rep[0]['port']) in ports_udp_scannes:
                    cursor.execute('UPDATE services SET date_retrait=%s WHERE id=%s and ip_hote=%s',[date_scan,srv,host_dict['ip']])

                elif rep[0]['protocole']=='tcp' and int(rep[0]['port']) in ports_tcp_scannes:
                    cursor.execute('UPDATE services SET date_retrait=%s WHERE id=%s and ip_hote=%s',[date_scan,srv,host_dict['ip']])
        
            #Si le scan a été lancé sur tous les ports alors, on peut supprimer tous les ports présents dans la base 
            #qui n'ont pas été détecté lors de ce scan
            else:    
                cursor.execute('UPDATE services SET date_retrait=%s WHERE id=%s and ip_hote=%s',[date_scan,srv,host_dict['ip']])

        #On met a jour la table hote
        cursor.execute("SELECT count(id) FROM services WHERE ip_hote=%s AND date_retrait is NULL",[host_dict['ip']])
        nb_services=dictfetchall(cursor)[0]['count']
        cursor.execute('UPDATE hotes SET nb_services=%s WHERE ip=%s',[nb_services,host_dict['ip']])

        



def parserNessusCsv(fichierCSV,scans_status_id,modeStrict=False):
    '''
    Importe le rapport CSV d'un scan Nessus dans une base SQL
    
    Le mode restrictif permet de générer une erreur en cas de decouverte
    d'une vulnerabilite sur un service non présent en base
    '''

    csvfile=open(fichierCSV, 'r')
    spamreader = csv.reader(csvfile, delimiter=',')
    cursor=connection.cursor()

    cursor.execute('SELECT date_lancement FROM scans_status WHERE id=%s LIMIT 1',[scans_status_id])
    rep=dictfetchall(cursor)
    date_scan=rep[0]['date_lancement']

    #Gestion du mode restrict
    dict_raise={'ip':[],'ports_tcp':[],'ports_udp':[]}

    dict_vulns_hote={}
    entete=True

    #liste hotes existant
    cursor.execute('SELECT ip FROM hotes')
    dict_hotes_existant=dictfetchall(cursor)
    tableau_hotes_existant=[]
    dict_dns={}

    for elem in dict_hotes_existant:
        tableau_hotes_existant.append(elem['ip'])

    
    cve_a_interroger=[]
    
    for row in spamreader:
        #Pour ne pas recuperer la ligne dentete
        if entete==True:
            entete=False
            continue

        plugin_id=int(row[0])
        cve=str(row[1])
        cvss=str(row[2])
        criticite=str(row[3])
        protocole=str(row[5])
        port=str(row[6])
        nom=str(row[7])
        synopsis=str(row[8])
        description=str(row[9])
        solution=str(row[10])        
        a_lire=str(row[11])
        retour_plugin=str(row[12])

        if criticite =='None':
            criticite='Info'
        

        cursor.execute('SELECT id FROM vulnerabilitees WHERE plugin_id=%s AND criticite=%s AND nom=%s AND description=%s AND synopsis=%s LIMIT 1',[plugin_id,criticite,nom,description,synopsis])
        nb=dictfetchall(cursor)

        if len(nb)==0:
            #on ajoute la vulnerabilites a la base de donnee
            cursor.execute('INSERT INTO vulnerabilitees (plugin_id,nom,description,synopsis,solution,infos_complementaires,criticite) VALUES (%s,%s,%s,%s,%s,%s,%s)',[plugin_id,nom,description,synopsis,solution,a_lire,criticite])


        
        #On verifie s'il y a eu une MAJ au niveau de la solution ou des liens
        else:    

            cursor.execute('SELECT solution,infos_complementaires FROM vulnerabilitees WHERE id=%s LIMIT 1',[nb[0]['id']])
            info_scan=dictfetchall(cursor)

            if info_scan[0]['solution']!=solution:
                cursor.execute('UPDATE vulnerabilitees SET solution=%s WHERE id=%s',[solution,nb[0]['id']])

            if info_scan[0]['infos_complementaires']!=a_lire:
                cursor.execute('UPDATE vulnerabilitees SET infos_complementaires=%s WHERE id=%s',[a_lire,nb[0]['id']])



        #On recupere l'id de la vulnerabilite recemment ajoute ou correspondant
        cursor.execute('SELECT id FROM vulnerabilitees WHERE plugin_id=%s AND criticite=%s AND nom=%s AND description=%s AND synopsis=%s AND solution=%s AND infos_complementaires=%s',[plugin_id,criticite,nom,description,synopsis,solution,a_lire])
        temp=dictfetchall(cursor)
        id_vuln=temp[0]['id']


        #Gestion des références associées à la vulnérabilitée rencontrée (CVE)        
        for reference in cve.split(','):
            if reference !='':
                cursor.execute('SELECT id FROM refs WHERE nom=%s',[reference])
                temp=dictfetchall(cursor)

                #On ajoute la reference à un tableau si elle n'y est pas présente
                #A la fin de l'importation, chaque reference sera interrogé sur le site (cvedetails)
                # afin de récupérer diverse informations (facilité, impact sur la dispo,confidentialité,...)
                if reference not in cve_a_interroger:
                    cve_a_interroger.append(reference)

                #Si la reference n'existe pas on la cree
                if len(temp)==0:
                    cursor.execute('INSERT INTO refs (nom) VALUES(%s)',[reference])
                    cursor.execute('SELECT id FROM refs WHERE nom=%s',[reference])
                    temp=dictfetchall(cursor)
 
                id_ref=temp[0]['id']
    
                #On verifie si la vulnerabilite possede déjà une association avec la référence
                cursor.execute('SELECT vuln_id,ref_id FROM vulns_refs WHERE vuln_id=%s AND ref_id=%s',[str(id_vuln),str(id_ref)])
                nb=dictfetchall(cursor)
                
                if len(nb)==0:
                    cursor.execute('INSERT INTO vulns_refs (vuln_id,ref_id) VALUES (%s,%s)',[id_vuln,id_ref])
                
        
        #On parcourt l'ensemble des hotes affectes par la vulnerabilite
        #afin d'ajouter, si besoin, une correspondance dans la table vuln_hote_service
        
        for hote in str(row[4]).split(','):
            #Il arrive que Nessus mette le nom de la machine au lieu de son ip
            #Dans ce cas, on réalise une résolution DNS 
            #Le dictionnaire permet d'économiser le nombre de requêtes effectuées
            if re.search('([0-9]{1,3}\.){3}([0-9]{1,3})',str(hote))==None:
                if dict_dns.has_key(str(hote)):
                    hote=dict_dns[str(hote)]
                else:
                    try:
                        hostname=str(hote)
                        hote=getIP(hostname)
                        dict_dns[hostname]=hote
                    except:
                        continue
                             

            #On verifie que notre dictionnaire de travail contient une entree pour l'hote scanner
            #si ce n'est pas le cas on la cree avec comme valeur de cle la liste des vuln_id qu'il possede
            if dict_vulns_hote.has_key(hote)==False:
                cursor.execute('SELECT id_vuln,id_service FROM vuln_hote_service WHERE ip_hote=%s AND date_correction is NULL', [hote])
                rep=dictfetchall(cursor)
                tableau_vuln_service=[]

                for i in range(len(rep)):
                         tableau_vuln_service.append(rep[i])


                dict_vulns_hote[hote]=tableau_vuln_service


            #On selectionne l'id du service correpondant 
            cursor.execute('SELECT id FROM services WHERE ip_hote=%s AND protocole=%s AND port=%s AND date_retrait is NULL', [hote,protocole,port])
            rep=dictfetchall(cursor)


            #Dans le cas où le service n'est pas présent en base, on indique dans un dictionnaire le port correspondant
            #Une fois le CSV parcouru, on lévera une alerte indiquant les ports à scanner avec Nmap
            #Rappel: le modeStrict sur "OFF" permet de ne pas lever d'erreur en n'important pas la vulnérabilitée (mode dégradé)
            if len(rep)==0:
                #Cas d'une vulnerabilite systeme:
                if port=='0' and criticite!='Info':
                    cursor.execute("SELECT id  FROM services WHERE ip_hote=%s AND port=0 AND nom='OS' AND type='OS'",[hote])
                    rep=dictfetchall(cursor)

                    if len(rep)==0:
                        cursor.execute("INSERT INTO services (protocole,port,etat,nom,type,ip_hote,date_ajout) VALUES ('tcp',0,'open','OS','OS',%s,%s)",[hote,date_scan])

                        cursor.execute("SELECT id FROM services WHERE ip_hote=%s AND port=0 AND nom='OS' AND type='OS'", [hote])
                        rep=dictfetchall(cursor)


                elif modeStrict==True and str(port)!='0':
                    if (str(hote) not in dict_raise['ip']):
                        dict_raise['ip'].append(str(hote))

                    if (protocole=='udp' and (port not in dict_raise['ports_udp'])):
                        dict_raise['ports_udp'].append(str(port))

                    if (protocole=='tcp' and (port not in dict_raise['ports_tcp'])):
                        dict_raise['ports_tcp'].append(str(port))
                    continue
                else:
                    continue

            if port=="0":
                id_service=rep[0]['id']
                cursor.execute('SELECT id_vuln FROM vuln_hote_service WHERE ip_hote=%s AND id_service=%s AND id_vuln=%s AND date_correction is NULL',[hote,id_service,id_vuln])
                temp=dictfetchall(cursor)

            else:
                id_service=rep[0]['id']

                #On verifie si la table vuln_hote_service contient une entree pour le trio (service,ip,vuln)
                cursor.execute('SELECT id_vuln FROM vuln_hote_service WHERE ip_hote=%s AND id_service=%s AND id_vuln=%s AND date_correction is NULL',[hote,id_service,id_vuln])
                temp=dictfetchall(cursor)

            # 1)Il s'agit alors d'une nouvelle vulnérabilitée 
            if len(temp)==0:
                cursor.execute('INSERT INTO vuln_hote_service (ip_hote,id_service,id_vuln,date_detection,retour_vuln) VALUES (%s,%s,%s,%s,%s)',[hote,id_service,id_vuln,date_scan,retour_plugin])


            # 2) la vulnérabilitée était déjà présente en base (rien de nouveau donc)
            #on supprime donc l'entrée de notre dictionnaire de travail
            #Rappel dict_vulns_hote={'host1':[liste_vulnerabilitees]}
            else: 
                dict_a_supprimer={}
                dict_a_supprimer['id_vuln']=id_vuln
                dict_a_supprimer['id_service']=id_service
                try:
                    dict_vulns_hote[hote].remove(dict_a_supprimer)
                except ValueError:
                    #Il arrive que Nessus remonte la meme vulnerabilite pour un meme service mais avec 
                    #une syntaxe de sortie de plugin légérement différente (mais avec une information identique)
                    #dans ce cas note tableau_vuln initial ne contiendra qu'une iteration du couple service/vuln
                    #alors que le rapport en contient plusieurs, d'où l'erreur
                    pass


    for reference in cve_a_interroger:
        param=get_CVE_details(str(reference))
        cursor.execute("SELECT * FROM refs WHERE nom=%s",[str(reference)])
        temp=dictfetchall(cursor)

        if len(temp)==0:
            cursor.execute('''INSERT INTO refs (nom,cvss_score,confidentialite,integrite,disponibilite,complexite,authentification,type,acces_obtention) 
                            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)''',
                            [reference,param['cvss_score'],param['confidentialite'],param['integrite'],param['disponibilite'],
                            param['complexite'],param['authentification'],param['type'],param['acces_obtention']])

        else:
            cursor.execute('''UPDATE refs
                            SET cvss_score=%s,
                            confidentialite=%s,
                            integrite=%s,
                            disponibilite=%s,
                            complexite=%s,
                            authentification=%s,
                            type=%s,
                            acces_obtention=%s WHERE nom=%s''',[param['cvss_score'],param['confidentialite'],param['integrite'],param['disponibilite'],
                                                      param['complexite'],param['authentification'],param['type'],param['acces_obtention'],reference])


    if modeStrict==True:
        if len(dict_raise['ip'])>0:
            raise ErreurScanNessus('Service(s) introuvable(s)',dict_raise)


    #Pour finir, on parcourt le dictionnaire de travail
    #Les vuln_id restantes correspondent à des vulnerabilitées qui ont été corrigées
    # On met donc a jour la table vuln_hote_service en fonction
    for hote in dict_vulns_hote.keys():
        for dic in dict_vulns_hote[hote]:
            cursor.execute('UPDATE vuln_hote_service SET date_correction=%s WHERE ip_hote=%s AND id_vuln=%s AND id_service=%s',[date_scan,hote,dic['id_vuln'],dic['id_service']])



        cursor.execute('SELECT count(id_vuln) FROM vuln_hote_service WHERE ip_hote=%s AND date_correction IS NULL',[hote])
        nb=dictfetchall(cursor)
        nb_vuln=nb[0]['count']

        cursor.execute('UPDATE hotes SET nb_vulnerabilites=%s WHERE ip=%s',[nb_vuln,hote])

    csvfile.close()

















        


