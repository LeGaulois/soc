#-*- coding: utf-8 -*-
import requests
import json
import time
import sys
import ConfigParser
import codecs
from django.conf import settings

'''
Cette fonction permet d'appeler des fonctionnalités de Nessus
Elle sera utilisé typiquement pour:
    - lancer de nouveaux scans
    - afficher la liste des policies définis (formulaire) 
'''



#Variables globales
BASE=settings.BASE_DIR+'/'
Config = ConfigParser.ConfigParser()
Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

ADRESSE=Config.get('Nessus','adresse')
PORT=Config.get('Nessus','port')
LOGIN=Config.get('Nessus','Login')
PASSWORD=Config.get('Nessus','Password')
DIRECTORY_ID=Config.get('Nessus','Directory_Id')
VERIFY=str(Config.get('Nessus','Verify_SSL')).lower()

if VERIFY=="false" or VERIFY=="no" or VERIFY=="non" or VERIFY=="0":
    VERIFY=False
else:
    VERIFY=True
 
CUSTOM_TEMPLATE_UUID=Config.get('Nessus','Custom_Template_UUID')


class Nessus(object):

    def __init__(self,adresse=ADRESSE,port=PORT,verify=None):
        self.adresse=adresse
        self.port=port
        self.url='https://'+str(self.adresse)+':'+str(self.port)+'/'
        self.token=None
        self.headers={'Content-Type':'application/json'}
        self.verify=VERIFY if verify is None else verify


    def envoyer(self,methode, lien, data=None):

        data = json.dumps(data)

        if methode == 'POST':
            r = requests.post(self.url+str(lien), data=data, headers=self.headers, verify=self.verify)

        elif methode == 'PUT':
            r = requests.put(self.url+str(lien), data=data, headers=self.headers, verify=self.verify)

        elif methode == 'DELETE':
            r = requests.delete(self.url+str(lien), data=data, headers=self.headers, verify=self.verify)

        else:
            r = requests.get(self.url+str(lien), params=data, headers=self.headers, verify=VERIFY)


        if r.status_code != 200:
            e = r.json()
            raise Exception(str(e['error']))

        if 'download' in lien:
            return r.content

        if methode!='DELETE':
            return r.json()



    def connexion(self,login=LOGIN,password=PASSWORD):
        '''
        Methode permettant de se logger sur le serveur Nessus
        La methode ajoute le token renvoye par le serveur
        à la variable headers de l'objet Nessus
        '''

        login_data={'username' : str(login), 'password' : str(password)}
        res=self.envoyer('POST','session/', login_data)
        self.token=str(res['token'])
        self.headers['X-Cookie']='token='+str(res['token'])+';'


    def deconnexion(self):
        res=self.envoyer('DELETE','session/')


    def createFolder(self,name):
        '''
        Créer un répertoire pour les scans et retourne
        l'ID du repertoire
        '''
        folder_param={"name":str(name)}
        res=self.envoyer('POST','folders/',folder_param)

        res=self.envoyer('GET','folders/',)

        for folder in res:
            if folder['name']==name:    
                return int(folder['id'])


    def listScanStatus(self,directory_id):
        '''
        retourne la liste des scans présents dans le repertoire spécifié
        en parametre GLOBAL
        Pour chaque scan, renvoie son id et son etat
        '''

        temp=self.envoyer('GET','scans/')
        res=[]

        if temp['scans']:
            for scan in temp['scans']:
                param={'id':int(scan['id']),
                        'status':str(scan['status'])
                      }
                res.append(param)
        
        return res



    def statusScan(self,scanID):
        '''
        Renvoie le status d'un scan
        C'est à dire si il est demarré,stoppé,...
        '''

        res=self.envoyer('GET','scans/'+str(scanID))

        return res['info']['status']

        
    def listePolicies(self):
        '''
        Retourne la liste des 'policies'
        définient sur Nessus
        '''

        res=self.envoyer('GET','policies/')
    
        if res['policies'] is None:
            res['policies']=[]

        return res


    def listeScanTemplates(self):
        '''
        Retourne la liste des 'templates'
        définient sur Nessus
        '''

        res=self.envoyer('GET','editor/scan/templates/')

        return res

    def listeCustomScanTemplates(self):
        '''
        Retourne la liste des 'templates'
        définient sur Nessus
        '''

        res=self.envoyer('GET','editor/scan/templates/'+CUSTOM_TEMPLATE_UUID)
        return res['settings']['basic']['inputs'][4]['options']
            

    def getRapport(self,scan_id,format_fichier,nom_fichier):
        '''
        Genere un rapport pour le scan specifie en entree
        '''

        if format_fichier=='pdf':
            file_param = {'format':'pdf','chapters':'vuln_by_plugin'}
        else:
            file_param= {'format':'csv'}

        res=self.envoyer('POST','scans/'+str(scan_id)+'/export',file_param)

        num_fichier=res['file']


            
        #Temporisation: on attend que Nessus ait fini de générer le rapport
        res['status']='encours'
        while res['status']!='ready':
            res=self.envoyer('GET','scans/'+str(scan_id)+'/export/'+str(num_fichier)+'/status')
            time.sleep(1)


        rapport = self.envoyer('GET','scans/'+str(scan_id)+'/export/'+str(num_fichier)+'/download?token='+self.token)
        fic=open(str(nom_fichier),'w')
        fic.write(rapport)
        fic.close()


    
    def nouveauScan(self,policy_id,tableau_cible,nom,description=''):
        '''
        Creation d'un nouveau scan dans le repertoire applicatif 'DJANGO'
        Retourne l'id du nouveau scan
        '''

        adresse=tableau_cible[0]

        for i in range(1,len(tableau_cible)):
            adresse+=','+str(tableau_cible[i])

        param_scan={"uuid": CUSTOM_TEMPLATE_UUID,
            "settings": {
                "name": str(nom),
                "description": str(description),
                "folder_id": str(DIRECTORY_ID),
                "policy_id": str(policy_id),
                "text_targets": adresse,
                "file_targets": "",
                "launch": "ONETIME",
                "enabled": False,
                "launch_now": False,
                "emails": "",
                "filter_type": "",
                "filters": []
            }
        }


        res=self.envoyer('POST','scans/',param_scan)
        return res['scan']['id']
            


    def lancerScan(self,scan_id):
        data = self.envoyer('POST', 'scans/'+str(scan_id)+'/launch')


    def getScanProgress(self,scan_id):
        res=self.envoyer('GET','scans/'+str(scan_id))
        current = 0.0
        total = 0.0

        for host in res["hosts"]:
            current += host["scanprogresscurrent"]
            total += host["scanprogresstotal"]

        return int(current/(total if total else 1.0)*100.0)



    def listScanStatusAndProgress(self,directory_id):
        '''
        retourne la liste des scans présents dans le repertoire spécifié
        en parametre GLOBAL
        Pour chaque scan, renvoie son id et son etat
        '''
        res=self.listScanStatus(directory_id)

        for scan in res:
            status=scan['status']
            if status=='running':
                scan['progress']=self.getScanProgress(scan['id'])

            elif status=='completed':
                scan['progress']=100

            else:
                scan['progress']=0

        return res


    def supprimerScan(self,scan_id):
        try:
            self.envoyer('DELETE', 'scans/'+str(scan_id))
        except Exception as e:
            if str(e)=='The requested file was not found':
                pass
            else:
                raise Exception(str(e))


    def stopScan(self,scan_id):
        try:
            self.envoyer('POST','scans/'+str(scan_id)+'/stop')
        except ValueError:
            pass
        except Exception as e:
            raise e


