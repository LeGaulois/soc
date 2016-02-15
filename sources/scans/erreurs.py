#-*- coding: utf-8 -*-

class ErreurScanNessus(Exception):
	def __init__(self,erreur,dict_data=None):
		self.str="Erreur lors du scan Nessus: "+str(erreur)
		self.data=dict_data

	def getData(self):
		return self.data

	def __str__(self):
		return self.str
