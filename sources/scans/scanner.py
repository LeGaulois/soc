#-*- coding: utf-8 -*-
from client_nmap import scanNmap
from django.db import connection
import os
import re
from transformationRapport import *
from django.conf import settings
from observable import Observable
from time import sleep
from fonctions import calculCriticite
from erreurs import ErreurImport


BASE=settings.BASE_DIR+'/'
CHEMIN_TEMP=BASE+'scans/temp/'
TIMEOUT=60 
#Temps max d'attente pour le téléchargement d'un rapport

class Scan(Observable):
    '''
    Cette class correspond à un scan nmap et/ou nessus
    '''

    def __init__(self,id_scan,nom_unique,date_lancement,type_scan,chemin_rapport,liste_adresses,nmap_options=None,nessus_policy_id=None):
        Observable.__init__(self)
        self.nmap={'enable':False,'options':None,'instance':None,'status':'disable','progress':0,'import':'disable'}
        self.nessus={'enable':False,'id':-1,'policy_id':None,'status':'disable','progress':0,'import':'disable'}
        self.erreurs=[]
        self.cibles=liste_adresses
        self.date_lancement=date_lancement
        self.nom_unique=nom_unique
        self.chemin_rapport=chemin_rapport
        self.id_scan=id_scan
        self.tache_attente=[]
        self.compteur_erreur_nessus=0
        self.type_scan=type_scan

        if nmap_options!=None:
            self.nmap['enable']=True
            self.nmap['options']=nmap_options
            self.nmap['status']='ready'
            self.nmap['import']='ready'
            self.nmap['instance']=scanNmap(self.cibles,self.nmap['options'],CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')


        if nessus_policy_id!=None:
            self.nessus['enable']=True
            self.nessus['policy_id']=nessus_policy_id
            self.nessus['status']='ready'
            self.nessus['import']='ready'

    
    def getObject(self):
        '''
        retourne les élements importants sous forme de dictionnaire
        '''
        reponse={
            'nmap':{
                    'status':self.nmap['status'],
                    'progress':self.nmap['progress'],
                    'import':self.nmap['import']},
            'nessus':{        
                    'status':self.nessus['status'],
                    'progress':self.nessus['progress'],
                    'import':self.nessus['import']},
            'erreurs':self.erreurs,
            'cibles':self.cibles,
            'id_scan':self.id_scan,
            'type_scan':self.type_scan,
            'nom_unique':self.nom_unique}

        return reponse
 
    def nessusGetID(self):
        return self.nessus['id']

    def nessusSetID(self,nessus_id):
        self.nessus['id']=int(nessus_id)

    def nessusGetStatus(self):
        return self.nessus['status']

    def nessusGetProgress(self):
        return self.nessus['progress']

    def nessusGetImport(self):
        return self.nessus['import']

    def relancerNmap(self,tableau_ip,options):
            self.nmap['options']=options
            self.nmap['status']='ready'
            self.nmap['import']='ready'
            sc_nmap=scanNmap(self.cibles,self.nmap['options'],CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')
            self.nmap['instance']=sc_nmap
            self.demarrerScanNmap()


    def setErreur(self,type_scan,erreur):
        dict_erreur={'type':str(type_scan),'description':str(erreur)}
        self.erreurs.append(dict_erreur)


    def getErreurs(self):
        return self.erreurs
    

    def nessusUpdateImport(self,nessus_import):
        self.nessus['import']=nessus_import
        self.notify_observers('dispatcher',status_import={'scan':'nessus','status':self.nessus['import']})

    def nmapGetProgress(self):
        return str(self.nmap['progress'])

    def nmapGetStatus(self):
        return self.nmap['status']

    def nmapUpdateStatus(self,status):
        self.nmap['status']=status
        self.notify_observers('dispatcher',status={'scan':'nmap','status':self.nmap['status']})

    def nmapUpdateImport(self,nmap_import):
        self.nmap['import']=nmap_import
        self.notify_observers('dispatcher',status_import={'scan':'nmap','status':self.nmap['import']})

    def getScanID(self):
        return self.id_scan

    def demarrerScanNmap(self):     
        sc_nmap=self.nmap['instance']
        sc_nmap.start()
        sc_nmap.add_observer(self,'scan')
        self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Demmarage du scan nmap','type':'info'})

    

    def notify(self, emetteur,*args,**kwargs):
        #On verifie qu'il s'agise de nmap
        if isinstance(emetteur,scanNmap):
            if kwargs.has_key('progress'):
                self.nmap['progress']=int(kwargs.pop('progress'))

            if kwargs.has_key('status'):
                self.nmapUpdateStatus(str(kwargs.pop('status')))

                #si le scan est fini, on lance l'importation du rapport
                if self.nmap['status']=='completed':
                    self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Scan nmap realise avec success','type':'info'})
                    self.parserNmap()
                    os.remove(CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml')

                    #Puis on verifie s'il y a des tâches en attente
                    #Typiquement, une erreur d'importation du scan Nessus entraine la relance d'un nouveau scan
                    for job in self.tache_attente:
                        if job['type']=='nmap':
                            param=job['parametres']
                            self.nmapUpdateImport('ready')
                            self.relancerNmap(param['cibles'],param['options'])
                            del self.tache_attente[0]
                            break
        
                        elif job['type']=='import_nessus':
                            del self.tache_attente[0]
                            self.parserNessus()
                            break

                #En cas d'erreur avec Nmap, on desactive l'importation du rapport
                elif self.nmap['status']=='error':
                    self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Erreur lors du scan Nmap','type':'error'})
                    self.nmapUpdateImport('disable')

  
        #Sinon, il s'agit du dispatcher qui nous informe d'une evolution sur le scan Nessus
        else:
            if kwargs.has_key('progress'):
                self.nessus['progress']=int(kwargs.pop('progress'))

            if kwargs.has_key('status'):
                self.nessus['status']=str(kwargs.pop('status'))

                if self.nessus['status']=='completed':
                    try:
                        self.parserNessus()

                    except ErreurImport as e:
                        dict_erreur=e.getData()
                        self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= '+str(dict_erreur['message']),'type':dict_erreur['type']})
                        self.setErreur('nessus',str(dict_erreur['message']))
                        self.nessusUpdateImport('ready')

                    except Exception as e:
                        erreur=str(e)
                        self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= '+erreur,'type':'critical'})
                        self.setErreur('nessus',erreur)
                        self.nessusUpdateImport('error')

                elif self.nessus['status']=='error':
                    self.nessusUpdateImport('disable')

                elif self.nessus['status']=='stopping':
                    self.nessusUpdateImport('stopping')

                elif self.nessus['status']=='canceled':
                    self.nessusUpdateImport('canceled')
                        


    def parserNmap(self):
        self.nmapUpdateImport('running')

        try:
            parserNmapXml(CHEMIN_TEMP+'nmap/'+str(self.nom_unique)+'.xml',self.date_lancement)
            self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Parsage du rapport Nmap reussi','type':'info'})
            self.nmapUpdateImport('completed')

        except Exception as e:
            self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Erreur lors du parsage du scan Nmap '+str(e),'type':'critical'})
            self.setErreur('nmap','le parsage du rapport a échoué')
            self.nmapUpdateImport('error')


    def parserNessus(self):
        self.nessusUpdateImport('running')
        self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= DL du rapport Nessus au format CSV en cours...','type':'info'})   
        self.notify_observers('dispatcher',tache={'param':{'id':self.nessus['id'],'format':'csv','localisation':CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv'},'action':'nessus_getRapport'})

        timer=0
        #Tant que le rapport n'a pas été téléchargé, on attend
        while (os.path.exists(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv'))==False:
            sleep(2)
            timer+=2

            if timer>=TIMEOUT:
                self.nessusUpdateImport('error')
                raise Exception("délai d'attente pour le téléchargement du rapport dépassé")


        self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= le DL du rapport Nessus au format CSV a réussi','type':'info'})

    
        #Une fois le rapport télécharger, on le parse
        try:
            if self.compteur_erreur_nessus==2:
                mode_degrade=True
                self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Parsage du rapport Nessus en mode dégradé','type':'error'})
                parserNessusCsv(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv',self.id_scan,False)
                self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Parsage du rapport Nessus en mode dégradé a réussi','type':'error'})

            else:
                mode_degrade=False
                self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Parsage du rapport Nessus en cours...','type':'info'})
                parserNessusCsv(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv',self.id_scan,True)
                self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= Parsage du rapport Nessus réussi ;)','type':'info'})
               

        except ErreurScanNessus as e:
            if mode_degrade==True:
                self.nessusUpdateImport('error')
                raise Exception("echec de l'import du scan Nessus")

                
            erreur='Erreur lors du parsage du rapport Nessus'
            self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= '+erreur,'type':'error'})
            self.setErreur('nessus',erreur)

            self.compteur_erreur_nessus+=1
            adresse=''
            dict_erreur=e.getData()

            for ip in dict_erreur['ip']: 
                adresse+=' '+str(ip)
                optionsNmap='-Pn -sV '

            if len(dict_erreur['ports_tcp'])!=0:
                optionsNmap+='-sS -pT:'
                            
                for portTcp in dict_erreur['ports_tcp']:
                    optionsNmap+=str(int(portTcp))
                                    
                    if portTcp!=dict_erreur['ports_tcp'][-1]:
                        optionsNmap+=','

            if len(dict_erreur['ports_udp'])!=0:
                if(re.search('-pT:',optionsNmap)!=None):
                    optionsNmap+=',U:'

                else:
                    optionsNmap+='-pU:'
                
                for portUdp in dict_erreur['ports_udp']:
                    optionsNmap+=str(int(portUdp))
                        
                    if portUdp!=dict_erreur['ports_udp'][-1]:
                        optionsNmap+=','

                optionsNmap+=' -sU'

            #On essaye de replannifier un scan Nmap
        
            #Si un scan Nmap est déjà en cours, on met les 
            #tâches en file d'attente
            #Elles seront alors traîtés lors de la fin du scan Nmap
            if self.nmap['status']=='running':
                self.tache_attente.append({'type':'nmap','parametres':{'cibles':dict_erreur['ip'],'options':optionsNmap}})
                self.tache_attente.append({'type':'import_nessus'})
                raise ErreurImport({'message':"scan Nmap toujours en cours, ajout des tâches en file d'attente",'type':'error'})

            else:
                self.tache_attente.append({'type':'import_nessus'})
                self.relancerNmap(dict_erreur['ip'],optionsNmap)
                raise ErreurImport({"message":"creation du nouveau scan Nmap en vue d'une nouvelle importation du rapport Nessus: "+str(optionsNmap)+'\n'+str(self.tache_attente),"type":"error"})

        os.remove(CHEMIN_TEMP+'nessus/'+str(self.nom_unique)+'.csv')


        #On telecharge d'abord le rapport au format PDF
        #Si il y a une erreur on la note mais on continue (non-bloquant)  
        self.notify_observers('dispatcher',tache={'param':{'id':self.nessus['id'],'format':'pdf','localisation':self.chemin_rapport+str(self.nom_unique)+'_nessus.pdf'},'action':'nessus_getRapport'})

        #Tant que le rapport n'a pas été téléchargé, on attend
        timer=0
        while (os.path.exists(self.chemin_rapport+str(self.nom_unique)+'_nessus.pdf'))==False:
            sleep(2)
            timer+=2

            if timer>=TIMEOUT:
                break

        if os.path.exists(self.chemin_rapport+str(self.nom_unique)+'_nessus.pdf'):
            self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= le DL du rapport Nessus au format PDF a réussi','type':'info'})

        else:
            erreur='le DL du rapport Nessus au format PDF a échoué'
            self.notify_observers('dispatcher',log={'message':'['+str(self.id_scan)+']= '+erreur,'type':'warning'})
            self.setErreur('nessus',erreur)



        #Pour tous les hotes scannés, on met à jour leur vulnérabilitée
        for ip in self.cibles:
            calculCriticite(ip)

        import_ok=True

        #On parcourt la liste des erreurs 
        for erreur in self.erreurs:
            if erreur['type']=='nessus':
                self.nessusUpdateImport('completed_with_error')
                import_ok=False
                break


        if import_ok:
            self.nessusUpdateImport('completed')
            del import_ok

