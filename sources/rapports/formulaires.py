#-*- coding: utf-8 -*-
from django import forms


class getPDF_formulaire(forms.Form):
	def __init__(self,*args,**kwargs):
		liste_adresses=kwargs.pop('liste_ip')		

		LISTE_GROUP_BY=[('ip','hote'),
('vuln','vuln')
]
		LISTE_IP=[]
		for i  in range(len(liste_adresses)):
			ip=liste_adresses[i]['ip']
			LISTE_IP.append((ip,ip))

	
		liste_appli=kwargs.pop('liste_appli')
		LISTE_APPLI=[]

		for i  in range(len(liste_appli)):
			nom=liste_appli[i]['nom']
			LISTE_APPLI.append((nom,nom))


		del liste_appli
		del liste_adresses


		super(getPDF_formulaire,self).__init__(*args,**kwargs)
		self.fields['nom']=forms.CharField(label="NomRapport",max_length=50,required=True)
		self.fields['group_by']=forms.CharField(label="Group By",max_length=4,widget=forms.Select( choices=LISTE_GROUP_BY),required=True)
		#self.fields['liste_ip']=forms.MultipleChoiceField(label='Adresses',choices=LISTE_IP,required=True, widget=forms.SelectMultiple(attrs={'size':'10'}))
		self.fields['type_selection']=forms.CharField(label="Selection par",max_length=40,widget=forms.Select( choices=[('',''),('id_adresses','ip'),('id_applis','appli')],attrs={'onchange':'Selection()'}),required=True,initial='')
		self.fields['adresses']=forms.MultipleChoiceField(label='Adresses',choices=LISTE_IP,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))
		self.fields['applis']=forms.MultipleChoiceField(label='Applis',choices=LISTE_APPLI,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))

										
	def is_valid(self):
        	is_valid = super(getPDF_formulaire,self).is_valid()
        	if not is_valid:
            		for field in self.errors.keys():
                		print "ValidationError: %s[%s] <- \"%s\" %s" % (
                    			type(self),
                    			field,
                    			self.data[field],
                    			self.errors[field].as_text()
                		)
        	return is_valid

