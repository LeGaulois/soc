#-*- coding: utf-8 -*-
from logging.handlers import RotatingFileHandler
import logging

'''
Permet de logger les erreurs
'''

class log(object):
    def __init__(self,fichier,instance):
        self.logger = logging.getLogger(instance)
        self.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s :: %(levelname)s :: %(message)s')
        self.file_handler = RotatingFileHandler(fichier, 'a', 5000000, 1)
        self.file_handler.setLevel(logging.DEBUG)
        self.file_handler.setFormatter(formatter)
        self.file_handler.createLock()
        self.logger.addHandler(self.file_handler)
        
    def ecrire(self,message,niveau):
        if niveau=='critical':
            self.logger.critical(message)

        elif niveau=='error':
            self.logger.error(message)

        elif niveau=='warning':
            self.logger.warning(message)

        elif niveau=='info':
            self.logger.info(message)
        else:        
            self.logger.debug(message)

    def fermer(self):
        self.file_handler.close()
    
