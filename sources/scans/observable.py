#-*- coding: utf-8 -*-
from threading import Thread
from collections import defaultdict
from django.conf import settings

BASE=settings.BASE_DIR+'/'


class Observable(object):
    def __init__(self):
        self.observers =defaultdict(list)

    def notify_observers(self,event,*args,**kwargs):
        '''
        On crée un thread pour le traitement de chaque notification
        '''

        for obs in self.observers[event]:
            thread =Thread(target=obs.notify,args=(self,),kwargs=kwargs)
            thread.start()

    def add_observer(self, obs,event):
        if not hasattr(obs, 'notify'):
            raise ValueError("L'observer doit posseder la methode 'notify'")

        self.observers[event].append(obs)
