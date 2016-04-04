#-*- coding: utf-8 -*-
import psycopg2
import re
from clientNessusRPC import Nessus
from fonctions import *


def testConnectionSQL(host,port,database,login,password):
    '''
    Cette fonction permet de verifier que l'utilisateur puisse:
        - se connecter a la base
        - que l'utilisateur ait le droit de créer une base
    '''

    try:
        conn = psycopg2.connect(host=host,port=int(port),database='postgres',user=str(login),password=str(password))
    except Exception as e:
        erreur=str(e)

        if re.search('Connection refused',erreur)!=None:
            raise ValueError('Connection impossible')

        elif re.search('FATAL',erreur)!=None:
            raise ValueError("Erreur d'authentification")

        else:
            raise ValueError('oups: '+erreur)


    #On récupère les informations sur:
    #   - la database specifiée
    #   - l'utilisayeur spécifié
    cursor=conn.cursor()
    cursor.execute("SELECT datdba FROM pg_database WHERE datname=%s",[database])
    base=dictfetchall(cursor)

    cursor.execute("SELECT rolcreatedb,oid FROM pg_roles WHERE rolname=%s",[login])    
    user=dictfetchall(cursor)

    #si la base n'existe pas
    #et si l'utilisateur ne possede pas le droit de creation de base
    if ((len(base)==0) and (user[0]['rolcreatedb']==False)):
        raise ValueError(str(login)+" ne possède pas le doit de création de base")


    #si la base existe, on s'assure que l'utilisateur
    # en est bien le propriétaire
    elif len(base)==1:
        if int(base[0]['datdba'])!=int(user[0]['oid']):
            raise ValueError(str(login)+"n'est pas proprietaire de la base")



def testConnectionNessus(host,port,user,password):
    try:
        ScannerNessus=Nessus(host,port)
        ScannerNessus.connexion(user,password)
        ScannerNessus.deconnexion()
    
    except Exception as e:
        erreur=str(e)
        
        if re.search('Connection refused',erreur)!=None:
            raise ValueError('Connection impossible')

        elif erreur=='Invalid Credentials':
            raise ValueError("Erreur d'authentification")

        else:
            raise ValueError('Erreur')


def testTuples(variable):
    '''
    Permet de contrôler que les variables rentrées soient sous forme
    de tuples
    '''

    tuples=variable.split('\r\n')

    for var_tuple in tuples:
        temp=var_tuple.split(';')
        
        if len(temp)!=2:
            raise ValueError(str(var_tuple)+' -> format invalide: valeur_base;valeur_affichée')

    return variable 
    

