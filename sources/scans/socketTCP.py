#-*- coding: utf-8 -*-
import socket
from django.conf import settings

BASE=settings.BASE_DIR+'/'



class socketTCP():
    def __init__(self,sock=None):
        if sock is None:
            self.sock=socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.sock.connect(BASE+"scans/temp/socket_scanner_django")

        else:
            self.sock=sock

    def send(self,data):
        self.sock.send(data)
    
    def recv(self,buff):
        return self.sock.recv(buff)

    def envoyer(self,data):
        data+='[>END<]'

        MSGLEN=len(data)
        d=MSGLEN/4096
        nb_tour=d if MSGLEN%4096==0 else d+1    
        total_envoye=0
   
        for i in range(0,nb_tour):
            taille_paquet=min(MSGLEN-total_envoye,4096)
            self.sock.send(data[total_envoye:total_envoye+taille_paquet])
            total_envoye+=taille_paquet



    def recevoir(self):
        resultats= []

        #Comme on ne connaît pas par avance la taille de la reponse,
        #on se place dans une boucle
        #la fin de la reponse est symbolise par '[END]'
        while True:
            reponse = self.sock.recv(4096).rstrip()

            if not reponse:
                break

            if '[>END<]' in reponse:
                resultats.append(reponse[:reponse.find('[>END<]')])
                break

            resultats.append(reponse)

        return b''.join(resultats)


    def fermer(self):
        self.sock.close()
