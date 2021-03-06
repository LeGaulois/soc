#-*- coding: utf-8 -*-
import socket
from threading import Thread,RLock
import os,sys
import json
from clientNessusRPC import Nessus
from scanner import Scan
from time import sleep
from django.db import connection
from fonctions import dictfetchall
import datetime,pytz,time
from erreurs import ErreurScanNessus
from logger import log
from rapports.rapportEvolution import *
from django.conf import settings
from observable import Observable
import ConfigParser
from socketTCP import socketTCP
import requests
from mail import envoieMail
import logging



logger = logging.getLogger(__name__)

buf=4096
BASE=settings.BASE_DIR+'/'
CHEMIN_TEMP=BASE+'scans/temp/'
CHEMIN_RAPPORT=BASE+'rapports/rapports/'
CHEMIN_LOGS=BASE+'scans/logs/'

Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
DIRECTORY_ID=Config.get('Nessus','Directory_Id')

class dialogueClient(Thread):
    def __init__(self, client,srv,lock):
        Thread.__init__(self)
        self.client=socketTCP(client)
        self.srv=srv
        self.lock=lock


    def run(self):
        while True:
            request=self.client.recevoir()

            if not request:
                self.client.fermer()
                break

            else:
                a_dict = json.loads(request)
                fonction=a_dict['action']

                if fonction=='addScan':
                    try:
                        param=a_dict['parametres']
                        with self.lock:
                            self.srv.addScan(param['cibles'],param['id_scan'],param['type_scan'])
                            self.client.envoyer("done")

                    except Exception as e:
                        logger.error(str(e))
                        self.client.envoyer('error: '+str(e))

                
                elif fonction=='listeScan':
                    try:
                        rep=self.srv.getListeScan()
                        self.client.envoyer(json.dumps(rep))

                    except Exception as e:
                        self.client.envoyer('error: '+str(e))
                



class serveurTache(Thread,Observable):
    def __init__(self):
        Thread.__init__(self)
        Observable.__init__(self)
        self.scanListe=[]
        self.ScannerNessus=Nessus()
        self.attenteNessus=[]

        try:
            self.ScannerNessus.connexion()

        except:
            pass

        self.log=log(CHEMIN_LOGS+'scan.log','scanner.'+'srv_tache')


    def notify(self,emetteur,*args,**kwargs):
        #emetteur=kwargs.pop('emetteur')
        #On verifie qu'il s'agise de nmap
        if isinstance(emetteur,Scan):
            #Traitement des demandandes de log
            if kwargs.has_key('log'):
                log=kwargs.pop('log')
                self.log.ecrire(log['message'],log['type'])

            #Traitement des actions demandé par la class Scan
            if kwargs.has_key('tache'):
                tache=kwargs.pop('tache')
                action=tache['action']

                if action=='nessus_addScan':
                    #demandé lors de l'instanciation de la 
                    parametres=tache['param']
                    try:
                        nessus_id=self.ScannerNessus.nouveauScan(parametres['policy_id'],parametres['cibles'],parametres['nom'],parametres['description'])
                        emetteur.nessusSetID(int(nessus_id))
                    except Exception as e:
                        pass

                elif action=='nessus_getRapport':
                    parametres=tache['param']

                    try:
                        self.ScannerNessus.getRapport(parametres['id'],parametres['format'],parametres['localisation'])
                    except Exception as e:
                        if(str(e)=='Invalid Credentials'):
                            self.ScannerNessus.connexion()
                            self.ScannerNessus.getRapport(parametres['id'],parametres['format'],parametres['localisation'])


            if kwargs.has_key('status') or kwargs.has_key('status_import'):
                self.updateStatusBase(emetteur)



    def updateStatusBase(self,scan):
        '''
        Cette fonction permet de controler si le scan est termine
        et mettre à jour son status en base
        A noter que le status en base est un status general englobant
        a la fois le status nmap et nessus
        '''
        temp=scan.getObject()
        nessus_status=temp['nessus']['status']
        nessus_import=temp['nessus']['import']
        nmap_status=temp['nmap']['status']
        nmap_import=temp['nmap']['import']
        id_scan=temp['id_scan']
        nom_unique=temp['nom_unique']
        type_scan=temp['type_scan']
        erreurs=scan.getErreurs()
        del temp

        cursor=connection.cursor()

        status_completed=['disable','completed']
        status_completed_with_error=['disable','completed','completed_with_error']
        status_error=['disable','error','completed','completed_with_error','stopping','canceled']

        d=datetime.datetime.now()
        tz = pytz.timezone('Europe/Paris')
        date_fin=tz.localize(d)

        if nessus_status=='running' or nmap_status=='running':
            cursor.execute('UPDATE scans_status SET etat=\'running\' WHERE id=%s', [id_scan])


        else:
            #Données pour l'envoie de mail
            infos_scan={
                'id': str(id_scan),
                'status': None,
                'nessus': None,
                'nmap': None,
                'erreurs': erreurs
            }

            infos_scan['nessus']=True if nessus_status!='disable' else False
            infos_scan['nmap']=True if nmap_status!='disable' else False


            if (nmap_status in status_completed) and (nmap_import in status_completed) and (nessus_status in status_completed) and (nessus_import in status_completed): 
                self.generationRapport(id_scan,nom_unique,type_scan)
                status="completed"
                infos_scan['status']=status
                message='['+str(id_scan)+']= Scan termine avec success'
                level='info'


            elif (nmap_status in status_completed_with_error) and (nmap_import in status_completed_with_error) and (nessus_status in status_completed_with_error) and (nessus_import in status_completed_with_error):
                self.generationRapport(id_scan,nom_unique,type_scan)
                status="completed_with_error"
                infos_scan['status']=status
                message='['+str(id_scan)+']= Scan termine avec des erreurs'
                level='error'


            elif (nmap_status in status_error) and (nmap_import in status_error) and (nessus_status in status_error) and (nessus_import in status_error):
                f.write("error\n")
                status="error"
                infos_scan['status']=status
                message='['+str(id_scan)+']= Echec du scan :('
                level='warning'

            else:
                status=None


            if status is not None:
                cursor.execute('UPDATE scans_status SET etat=%s, date_fin=%s WHERE id=%s', [status,date_fin,id_scan])
                self.log.ecrire(message,level)
                self.supprimerScan(id_scan)

                try:
                    envoieMail(infos_scan)
                except Exception as e:
                    message='['+str(id_scan)+"]= Echec d envoie des mails "+str(e)
                    level="warning"
                    self.log.ecrire(message,level)

        cursor.close()



    def generationRapport(self,id_scan,nom_unique,type_scan):
        self.log.ecrire('['+str(id_scan)+"]= Génération du rapport d'évolution en cours...",'info')

        try:
            creerRapportEvolution(nom_unique,id_scan,type_scan)
            self.log.ecrire('['+str(id_scan)+"]= La génération du rapport d'évolution a réussi",'info')

        except Exception as e:
            erreur="La génération du rapport d'évolution a échoué "+str(e)
            self.log.ecrire('['+str(id_scan)+"]= "+str(erreur),'info')


    def addScan(self,tableau_ip,id_scan,type_scan):
        cursor=connection.cursor()

        if type_scan=='manuel':
            cursor.execute('SELECT * FROM scans_manuels WHERE id=%s LIMIT 1',[id_scan])
            dictScan=dictfetchall(cursor)

        else:
            cursor.execute('SELECT * FROM scans_plannifies WHERE id=%s LIMIT 1',[id_scan])
            dictScan=dictfetchall(cursor)


        nmap=dictScan[0]['nmap']
        nessus=dictScan[0]['nessus']

        nmapOptions=dictScan[0]['nmap_options'] if nmap==True else None
        policy_id=dictScan[0]['nessus_policy_id'] if nessus==True else None

        tz = pytz.timezone('Europe/Paris')
        date_lancement=datetime.datetime.now()
        date_postgresql=tz.localize(date_lancement)
        date_lancement=datetime.datetime.now()


        cursor.execute('INSERT INTO scans_status (date_lancement,etat,type) VALUES (%s,\'ready\',%s)',[date_postgresql,str(type_scan)])
        cursor.execute('SELECT id FROM scans_status WHERE date_lancement=%s AND etat=%s AND type=%s LIMIT 1',[date_postgresql,'ready',str(type_scan)])
        temp=dictfetchall(cursor)
        id_scan_status=temp[0]['id']

        #Le nom unique sera utilisé pour:
        #    - le nom du rapport PDF
        #    - l'instance de log 
        nom_unique=str(id_scan_status)+'__'+str(date_lancement).replace(' ','_').split('.')[0]


        if type_scan=='manuel':
            cursor.execute('INSERT INTO scan_manuel_status (id_scans_status,id_scan_manuel) VALUES(%s,%s)',[str(id_scan_status),str(id_scan)])
            chemin_rapport=CHEMIN_RAPPORT+'ScansManuels/'+str(id_scan_status)+'/'
            os.makedirs(chemin_rapport)


        else:
            for ip in tableau_ip:
                cursor.execute('INSERT INTO scan_hote (id_scan,ip) VALUES(%s,%s)',[str(id_scan_status),ip])

            cursor.execute('INSERT INTO scan_plannifie_status (id_scan_plannifie,id_scans_status) VALUES(%s,%s)',[id_scan,str(id_scan_status)])
            chemin_rapport=CHEMIN_RAPPORT+'ScansPlannifies/'+str(id_scan)+'/'+str(id_scan_status)+'/'
            os.makedirs(chemin_rapport)

        cursor.close()



        #On instancie notre scan et on le place dans la liste
        scan=Scan(id_scan_status,nom_unique,type_scan,chemin_rapport,tableau_ip,nmapOptions,policy_id)
        self.scanListe.append({'id':id_scan_status,'scan':scan})


        #On ajoute reciproquement en observateur le scan et le serveur de tâche
        #Dans le premier cas pour pouvoir logger l'avancement du scan dans un fichier de log
        #   et lancer des commande Nessus (une seule instance Nessus pour n Scan)
        #Dans le second pour avertir le scan lorsque le scan Nessus est fini
        scan.add_observer(self,'dispatcher')
        self.add_observer(scan,str(id_scan_status))

        if nessus==True:
            try:
                nessus_id=self.ScannerNessus.nouveauScan(policy_id,tableau_ip,nom_unique,'Scan DJANGO')
                scan.nessusSetID(int(nessus_id))
                self.ScannerNessus.lancerScan(int(nessus_id))
                self.log.ecrire('['+str(id_scan_status)+']= Demmarage du scan nessus','info')
            except Exception as e:
                self.attenteNessus.append({'action':'ajout_scan','id_scan_status':id_scan_status,'scan':scan,'policy_id':policy_id,'tableau_ip':tableau_ip,'nom_unique':nom_unique,'info':'Scan DJANGO'})
                self.log.ecrire("["+str(id_scan_status)+"]= Echec de l'ajout du scan Nessus, "+str(e),"error")
        if nmap==True:
            scan.demarrerScanNmap()


    def demarrerScan(self,id_scan,type_scan):
        scan=self.getScan(id_scan)

        if scan.nessusGetStatus()=='ready' and (type_scan=='nessus' or type_scan=='all'):
            self.ScannerNessus.lancerScan(scan.nessusGetID())
            self.log.ecrire('['+str(id_scan)+']= Demmarage du Scan Nessus','info')

        if scan.nmapGetStatus()=='ready' and (type_scan=='nmap' or type_scan=='all'):
            scan.demarrerScanNmap()


    def supprimerScan(self,id_scan_status):
        '''
        Permet de supprimer un scan de la liste en cours
        '''
        for scan in self.scanListe:
            if int(scan['id'])==int(id_scan_status):
                sc=scan['scan']
                id_nessus=sc.nessusGetID()

                if id_nessus is not None:
                    try:
                        self.ScannerNessus.supprimerScan(id_nessus)
                    except:
                        self.attenteNessus.append({'action':'supprimer_scan','id_scan_nessus':id_nessus})

                self.scanListe.remove(scan)
                break


    def getScanProgress(self,id_scan,type_scan):
        scan=self.getScan(id_scan)

        if type_scan=='nmap':
             return scan.nmapGetProgress()

        if type_scan=='nessus':
             return scan.nessusGetProgress()



    def getScan(self,id_scan):
        for elem in self.scanListe:
            if int(elem['id'])==int(id_scan):
                return elem['scan']

        cursor=connection.cursor()
        cursor.execute('SELECT id_scans_status FROM scan_manuel_status WHERE id_scan_manuel=%s LIMIT 1',[str(id_scan)])
        temp=dictfetchall(cursor)
        id_scan=temp[0]['id_scans_status']

        for elem in self.scanListe:
            if int(elem['id'])==int(id_scan):
                return elem['scan']

        raise Exception('scan non présent en base')


    def getListeScan(self):
        reponse=[]

        for elem in self.scanListe:
            reponse.append(elem['scan'].getObject())

        return reponse


    def tentativeReconnexion(self):
        """
        Gestion des tentatives de reconnexion au serveur Nessus
        et à la reprise des tâches en attentes
        """

        self.log.ecrire('Tentative de reconnexion au serveur Nessus','debug')

        timeout = 10
        compteur = 0
        reussi=False

        while compteur < timeout:
            try:
                self.ScannerNessus.connexion()
                self.log.ecrire('Reconnexion réussi','debug')
                reussi=True
                break

            except Exception as e:
                time.sleep(10)
                compteur+=1

        if reussi==False:
            self.log.ecrire('Echec de reconnexion au serveur Nessus: '+str(e),'error')


        else:
            #si la connexion reussi on verifie si des scans sont en attente d'ajout
            if len(self.attenteNessus)>0:
                self.log.ecrire('Traitement des tâches Nessus en attente','debug')

                for scan_en_attente in self.attenteNessus:
                    try:
                        if scan_en_attente['action']=='ajout_scan':
                            scan=scan_en_attente['scan']
                            policy_id=scan_en_attente['policy_id']
                            tableau_ip=scan_en_attente['tableau_ip']
                            nom_unique=scan_en_attente['nom_unique']
                            info=scan_en_attente['info']
                            id_scan_status=scan_en_attente['id_scan_status']

                            nessus_id=self.ScannerNessus.nouveauScan(policy_id,tableau_ip,nom_unique,'Scan DJANGO')
                            scan.nessusSetID(int(nessus_id))
                            self.ScannerNessus.lancerScan(int(nessus_id))
                            self.log.ecrire('['+str(id_scan_status)+']= Demmarage du scan nessus','info')

                        elif scan_en_attente['action']=='ajout_scan':
                            id_scan_nessus=scan_en_attente['id_scan_nessus']
                            self.ScannerNessus.supprimerScan(id_scan_nessus)
                            self.log.ecrire('Suppresion du scan Nessus N°'+str(id_scan_nessus),'debug')
                    except Exception as e:
                        self.log.ecrire('Erreur d etraitement de la tâche en attente '+str(e),'error')
                    else:
                        self.attenteNessus.remove(scan_en_attente)

    def run(self):
        '''
        On fait des requêtes auprès de Nessus afin de récupérer régulièrement
        le status et la progression des scans
        Puis on compare les résultats avec les précédents
        En cas d'évolution, on prévient les scans
        '''

        while True:
            try:
                time.sleep(10)
                status=self.ScannerNessus.listScanStatusAndProgress(DIRECTORY_ID)

                for scan in self.scanListe:
                    id_scan=scan['id']
                    nessus_id=scan['scan'].nessusGetID()
                    nessus_status=scan['scan'].nessusGetStatus()
                    nessus_progress=scan['scan'].nessusGetProgress()

                    for elem in status:
                        if elem['id']==nessus_id:
                            if elem['status']!=nessus_status:
                                self.notify_observers(str(id_scan),status=elem['status'])

                            if int(elem['progress'])!=int(nessus_progress):
                                self.notify_observers(str(id_scan),progress=elem['progress'])


            #En cas de perte de la connexion avec Nessus
            except requests.exceptions.ConnectionError:
                self.log.ecrire('Perte de la connexion au serveur Nessus','warning')
                self.tentativeReconnexion()

            except Exception as e:
                #Dans le cas ou la session trop longtemps, elle passe en timeout
                #On se reconnecte donc
                if(str(e)=='Invalid Credentials'):
                    self.log.ecrire('Connexion timeout, reconnexion...','debug')

                elif(str(e)=='You need to log in to perform this request'):
                    self.log.ecrire('Perte de la connexion au serveur Nessus','warning')

                else:
                    self.log.ecrire(str(e),'warning')

                self.tentativeReconnexion()




class srvTCP(Thread):
    def __init__(self):
        Thread.__init__(self)
        if os.path.exists(BASE+"scans/temp/socket_scanner_django"):
          os.remove(BASE+"scans/temp/socket_scanner_django")

        try:
            self.conn=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.conn.bind(BASE+"scans/temp/socket_scanner_django")
            self.srv_tache=serveurTache()
            self.srv_tache.start()
            self.lock=RLock()

        except Exception as e:
            logger.critical('Erreur de lancement du serveur de gestion des scans !')
            logger.critical(str(e))
            sys.exit(-1)

    def run(self):
        while True:
            try:
                self.conn.listen(0)
                client,adresse=self.conn.accept()

                cv=dialogueClient(client,self.srv_tache,self.lock)
                cv.start()

            except Exception as e:
                logger.warning('Erreur client/serveur avec le serveur de taches')
                logger.warning(str(e))
                pass


