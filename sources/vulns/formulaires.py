#-*- coding: utf-8 -*-
from django import forms

class formFiltreVulns(forms.Form):
	def __init__(self,*args,**kwargs):
		self.criticite=kwargs.pop('criticite')


		CHOIX_CRITICITE=[]



		for m  in range(len(self.criticite)):
			CHOIX_CRITICITE.append((self.criticite[m].get('criticite'), self.criticite[m].get('criticite')) )



		super(formFiltreVulns,self).__init__(*args,**kwargs)
		self.fields['criticite']=forms.CharField(label='Criticite',initial=None,widget=forms.Select(choices=CHOIX_CRITICITE),required=False)


	
	def clean_criticite(self):
		niveauCriticite=self.cleaned_data['criticite']
		criticite_valide=["",None]

		for j  in range(len(self.criticite)):
			criticite_valide.append(self.criticite[j].get('criticite'))

		if niveauCriticite in criticite_valide:
			return niveauCriticite

		else:
			raise forms.ValidationError('Criticite non valide')

	
										
	def is_valid(self):
        	is_valid = super(formFiltreVulns,self).is_valid()
        	if not is_valid:
            		for field in self.errors.keys():
                		print "ValidationError: %s[%s] <- \"%s\" %s" % (
                    			type(self),
                    			field,
                    			self.data[field],
                    			self.errors[field].as_text()
                		)
        	return is_valid
