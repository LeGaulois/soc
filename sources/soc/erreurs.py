#-*- coding: utf-8 -*-

class ErreurScanNessus(Exception):
    '''
    Cette classe permet de renvoyer sous forme de dictionnaire
    la liste des erreurs rencontrés lors de l'importation du rapport Nessus
    en base
    '''

    def __init__(self,erreur,dict_data=None):
        self.str="Erreur lors du scan Nessus: "+str(erreur)
        self.data=dict_data

    def getData(self):
        return self.data

    def __str__(self):
        return self.str




class ErreurImport(Exception):
    '''
    Class permettant la gestion des erreurs d'importation
    d'un fichier
    '''
    def __init__(self,dict_data):
        self.data=dict_data

    def getData(self):
        return self.data
