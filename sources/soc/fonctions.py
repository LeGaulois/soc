#-*- coding: utf-8 -*-
import re
import csv 
from django.db import connection
from math import floor
import dns.resolver
import socket

def dictfetchall(cursor):
    "Retourne le resultat d'une requête SQL dans un tableau de dictionnaire"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]



def toString(s):
    return '' if s is None else str(s)



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
    '''
    Permet de valider une adresse IP
    '''
    try:
        octet=str(adresse).split('.')
        if (len(octet)!=4):
            raise ValueError("Adresse IP non valide")

        else:
            for num in octet:
                if (int(num)>255 or int(num)<0):
                    raise ValueError("Adresse IP non valide")
            return adresse
    except:
        raise ValueError("Adresse IP non valide")


def valideMAC(mac):
    try:
        mac_expr=re.search('([0-9A-Fa-f]{2}[:]){5}([0-9A-Fa-f]{2})',str(mac))

        if(mac_expr==None):
            raise ValueError("Adresse MAC non valide")

        else:
            return mac

    except:
        raise ValueError("Adresse MAC non valide")



    
def calculCriticite(ip):
    '''
    Permet de définir le niveau de vulnérabilité d'une machine en fonction
    du nombre et du type de vulnérabilités auquelles elle est soumise
    '''

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


def desatanize(string):
    '''
    Permet verifier qu'un string ne contient pas
    de caractere succeptibles d'engendrer une injection de commande
    '''

    elements_recherches=['\[','\]',';','\|','<','>','/','\.\.']

    for elem in elements_recherches:
        error=re.search(elem, str(string))

        if error!=None:
            raise Exception("Erreur de paramètre")

    return string


def get_value_from_liste_dict(liste_dict,nom_colonne_filtre,condition,cle_recherche):
    """
    Cette fonction permet de retourner la valeur d'un élement recherché
    dans un tableau de dictionnaire
    """

    for elem in liste_dict:
        if elem[nom_colonne_filtre]==condition:
            return elem[cle_recherche]

    return 0


def getIP(hostname):
    '''
    Cette fonction permet de récupérer l'adresse IP
    à partir d'un hostname
    '''
    try:
        reponse=dns.resolver.query(str(hostname),'a')
        return str(reponse[0])
    except:
        reponse=socket.gethostbyname_ex(hostname)[2][0]
        return reponse
         
