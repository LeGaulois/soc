#-*- coding: utf-8 -*-
from django import forms


class formulaire_authentification(forms.Form):

	def __init__(self,*args,**kwargs):

		super(formulaire_authentification,self).__init__(*args,**kwargs)
		self.fields['username']=forms.CharField(label="Username",required=True)
		self.fields['password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput)

											
	def is_valid(self):
        	is_valid = super(formulaire_authentification,self).is_valid()
        	if not is_valid:
            		for field in self.errors.keys():
                		print "ValidationError: %s[%s] <- \"%s\" %s" % (
                    			type(self),
                    			field,
                    			self.data[field],
                    			self.errors[field].as_text()
                		)
        	return is_valid
			

		

