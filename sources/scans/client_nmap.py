#-*- coding: utf-8 -*-
from threading import Thread
import re
from subprocess import Popen, PIPE, STDOUT
from fonctions import valideIP
from observable import Observable


class scanNmap(Thread,Observable):
    def __init__(self,tableau_adresse,options,fichier_sortie):
        Thread.__init__(self)
        Observable.__init__(self)
        self.adresse=''
        self.progress=0.0
        self.status='ready'

        #On cree un string a partir de la liste des adresses
        #contenues dans le tableau
        for ip in tableau_adresse:
            try:
                ip=valideIP(ip)
                self.adresse+=' '+str(ip)
            except:
                pass

        liste_arguments=[options,fichier_sortie]


        #Contrôle des arguments
        for arg in liste_arguments:
            error=re.search('[;|<>"`&{}]',str(arg))

            if error!=None:
                raise Exception("Paramètres Nmap invalide")

        #Si pas de levé d'exception
        self.options=options
        self.fichier_sortie=fichier_sortie

    def getStatus(self):
        return self.status

    def getProgress(self):
        return self.progress

    def updateProgress(self,progress):
        self.progress=progress
        self.notify_observers('scan',progress=self.progress)

    def updateStatus(self,status):
        self.status=status
        self.notify_observers('scan',status=self.status)


    def run(self):
        cmd = 'nmap '+str(self.options)+' --privileged --stats-every 10s '+str(self.adresse)+' -oX '+str(self.fichier_sortie)
        self.updateStatus('running')
        process = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        stdout = []

        #Permet de recuperer l'avancement du scan
        while True:
            line = process.stdout.readline()

            stdout.append(line)
            expr1=re.search('([0-9]{1,2}\.[0-9]{1,2}%)',str(line))
            expr2=re.search('performed',str(line))
            expr3=re.search('Usage: ',str(line))
            expr4=re.search('Nmap done',str(line))


            if expr1!=None:
                actuel=float(expr1.group().split('%')[0])

                if(actuel>self.progress):                    
                    self.updateProgress(actuel)

            elif expr2!=None:
                self.updateProgress(100)
                self.updateStatus('completed')
                break

            elif expr3!=None:
                self.updateStatus('error')
                break

            elif expr4!=None:
                self.updateProgress(100)
                self.updateStatus('completed')
                break
            
            if line == '' and process.poll() != None:
                break


