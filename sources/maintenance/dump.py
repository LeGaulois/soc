#-*- coding: utf-8 -*-
import re
import psycopg2
from django.conf import settings
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from fonctions import dictfetchall,desatanize,valideIP,getIP
import os
import shutil
import datetime
import subprocess
import re

BASE=settings.BASE_DIR+'/'

def exportProjet():
    #Sauveguarde des rapports et des fichiers de config
    try:
        os.mkdir(BASE+'sav/')

    except OSError:
        pass

    #shutil.copytree(BASE+'rapports/rapports/',BASE+'sav/')
    shutil.copyfile(BASE+'soc/settings.py',BASE+'sav/settings.py')
    shutil.copyfile(BASE+'soc/default.cfg',BASE+'sav/default.cfg')

    #DUMP postgreSQL
    postgresql=settings.DATABASES['default']
    host=valideIP(postgresql['HOST'])
    port=int(postgresql['PORT'])
    base=desatanize(postgresql['NAME'])
    user=desatanize(postgresql['USER'])
    password=desatanize(postgresql['PASSWORD'])

    #Variables de temps
    date_dump=datetime.datetime.now()

    os.putenv('PGPASSWORD',password)
    subprocess.check_output('pg_dump -h '+host+' -p '+str(port)+' -d '+base+' -U '+user+' > '+BASE+'sav/database.pg', shell=True)

    #Creation de l'archive
    chemin_archive=BASE+'sav/'
    nom='sav-soc_'+str(date_dump)+'.tar.gz'
    subprocess.check_output('tar -C '+BASE+' -cvf '+chemin_archive+nom+' sav/', shell=True)

    #Mise en ram et nettoyage
    temp=open(chemin_archive+nom,'rb')
    archive=temp.read()
    temp.close()
    shutil.rmtree(BASE+'sav/')

    return nom,archive
    

def importProjet(fichier):
    #Variables de temps
    date_import=datetime.datetime.now()

    chemin=BASE+'sav_'+date_import+'/'
    os.mkdir(chemin)

    with open(chemin+'import.tar.gz', 'wb+',0) as archive:
        for chunk in fichier.chunks():
            archive.write(chunk)

    archive.close()

    subprocess.check_output('tar -xvf '+str(chemin)+'import.tar.gz'+' -C '+str(chemin), shell=True)
    shutil.copyfile(chemin+'sav/settings.py',BASE+'soc/settings.py')
    shutil.copyfile(chemin+'sav/default.cfg',BASE+'soc/default.cfg')

    #Import postgreSQL
    postgresql=settings.DATABASES['default']
    host=valideIP(postgresql['HOST'])
    port=int(postgresql['PORT'])
    base=desatanize(postgresql['NAME'])
    user=desatanize(postgresql['USER'])
    password=desatanize(postgresql['PASSWORD'])

    initialiserPG(chemin+'sav/database.pg',host,port,base,user,password)
    
    shutil.rmtree(chemin)
    subprocess.check_output('touch '+BASE+'soc/wsgi-apache.py', shell=True)



def initialiserPG(dump_file,host,port,database,login,password):
    '''
    Cette fonction permet d'initialiser une base de donnée POstgreSQL
    à partir d'un fichier de dump
    '''

    conn = psycopg2.connect(host=host,port=port,database='postgres',user=login,password=password)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    cursor=conn.cursor()

    cursor.execute("SELECT datdba FROM pg_database WHERE datname=%s",[database])
    base=dictfetchall(cursor)

    cursor.execute("SELECT rolcreatedb,oid FROM pg_roles WHERE rolname=%s",[login])    
    user=dictfetchall(cursor)

    #si la base n'existe pas
    #et si l'utilisateur ne possede pas le droit de creation de base
    if ((len(base)==0) and (user[0]['rolcreatedb']==True)):
        error=re.search('[;|<>]&"\'',str(database))

        if error!=None:
            raise Exception("Erreur de paramètre")

        cursor.execute('CREATE DATABASE '+str(database))


    cursor.close()

    if len(base)==1:
        conn = psycopg2.connect(host=host,port=port,database=database,user=login,password=password)
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor=conn.cursor()
        cursor.execute("SELECT tablename FROM pg_tables WHERE tableowner=%s AND schemaname='public'",[login])
        liste=dictfetchall(cursor)

        for table in liste:
            cursor.execute("DROP TABLE IF EXISTS "+str(table['tablename'])+" CASCADE")

    
    os.putenv('PGPASSWORD',password)

    #On recupère l'adresse IP si l'utilisateur nous envoie le hostname
    try:
        host=valideIP(host)
    except:
        host=getIP(host)

    subprocess.check_output('psql -h '+desatanize(host)+' -p '+str(port)+' -d '+desatanize(database)+' -U '+desatanize(login)+' < '+dump_file, shell=True)
    
