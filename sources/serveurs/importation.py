#-*- coding: utf-8 -*-
from xml.dom.minidom import parse, parseString
import csv
import re
from django.db import connection
from fonctions import valideMAC, valideIP, dictfetchall
from erreurs import ErreurImport
import ConfigParser
import codecs
from django.conf import settings

class XMLHote:
    '''
    Class permettant l'import en base d'un fichier XML
    contenant des machines et leurs attributs
    '''    

    def __init__(self,fichier):
        self.fichier=fichier

        #Variables de verification
        cursor=connection.cursor()
        cursor.execute('SELECT DISTINCT(nom) FROM application ORDER BY nom ASC')
        self.APPLIS=dictfetchall(cursor)

        cursor.execute('SELECT DISTINCT(ip) FROM hotes')
        temp=dictfetchall(cursor)
        self.LISTE_ADRESSES=[]

        for ip in temp:
            self.LISTE_ADRESSES.append(ip['ip'])

        cursor.execute('SELECT DISTINCT(mac) FROM hotes')
        temp=dictfetchall(cursor)
        self.LISTE_MAC=[]
        cursor.close()

        for mac in temp:
            self.LISTE_MAC.append(mac['mac'])

        BASE=settings.BASE_DIR+'/'
        Config = ConfigParser.ConfigParser()
        Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
        self.LOCALISATION=[elem[0] for elem in Config.items('LOCALISATION')]
        self.TYPE_MACHINE=[elem[0] for elem in Config.items('TYPE')]
        self.LISTE_ENV=[elem[0] for elem in Config.items('ENVIRONNEMENT')]

        '''
        self.LISTE_ENV=('recette','pre-production','production')
        self.TYPE_MACHINE=('equipement-reseau','serveur','vm','appliance')
        self.LOCALISATION=('sarcelles','valence')
        '''
        self.dom = parse(fichier)


        #Liste des éléments pouvant être ajoutés en base pour une machine
        self.elements_hote=[{'nom':'ip','controle':self.valideAdresse},
        {'nom':'mac','controle':self.valideMacAdresse},
        {'nom':'hostname','controle':None},
        {'nom':'os','controle':None},
        {'nom':'type_machine','controle':self.valideTypeMachine},
        {'nom':'localisation','controle':self.valideLocalisation},
        {'nom':'environnement','controle':self.valideEnvironnement},
        {'nom':'commentaires','controle':None}]

        self.NB_ELEMENTS=len(self.elements_hote)
        self.tableau_erreurs=[]


    #Fonctions de contrôle
    def valideTypeMachine(self,type_machine): 
        if str(type_machine) in self.TYPE_MACHINE:
            return type_machine 
        else:
            raise Exception("Type de machine non valide")

    def valideLocalisation(self,localisation):
        if str(localisation) in self.LOCALISATION:
            return localisation
        else:
            raise Exception("Localisation non valide")

    def valideEnvironnement(self,environnement):
        if str(environnement) in self.LISTE_ENV:
            return environnement
        else:
            raise Exception("Environnement non valide")

    def valideAdresse(self,adresse): 
        if str(adresse) in self.LISTE_ADRESSES:
            raise Exception("Adresse IP déjà présente en base")
        else:
            return valideIP(adresse)

    def valideMacAdresse(self,mac): 
        if str(mac) in self.LISTE_MAC:
            raise Exception("Adresse MAC déjà présente en base")

        elif mac==None or mac=='':
            return None
        else:
            return valideMAC(mac)
        
  
    def importer(self):
        cursor=connection.cursor()
        for host in self.dom.getElementsByTagName('hote'):
            hote={'ip':None,'mac':None,'hostname':None,'os':None,'type_machine':None,'localisation':None,'environnement':None,'commentaires':None}
            erreur=False

            for element in self.elements_hote:
                #On recupere chaque attribut d'hôte attendu
                #Si l'attribut n'existe pas on le place à None

                try:
                    valeurAttribut=host.getElementsByTagName(element['nom'])[0].firstChild.data
                except:
                    valeurAttribut=None
                    
                if element['controle']!=None:
                    try:
                        valeurAttribut=element['controle'](valeurAttribut)
                    except Exception as e:
                        addr=hote['ip'] if hote['ip']!=None else valeurAttribut
                        dict_erreur={'ip':addr,'erreur':str(e)}
                        self.tableau_erreurs.append(dict_erreur)
                        erreur=True

                hote[element['nom']]=valeurAttribut

            #On test s'il y a eu des erreurs lors de la varification des attributs
            if erreur==False:
                cursor.execute('INSERT INTO hotes (ip,mac,hostname,os,type_machine,localisation,environnement,commentaires) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)',[hote['ip'],hote['mac'],hote['hostname'],hote['os'],hote['type_machine'],hote['localisation'],hote['environnement'],hote['commentaires']])


        cursor.close()

        if len(self.tableau_erreurs)>0:
            raise ErreurImport(self.tableau_erreurs)
