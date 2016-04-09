#-*- coding: utf-8 -*-
from django import forms
from django.utils.safestring import mark_safe
from tests_wizard import *


class postgreSQL(forms.Form):
    def __init__(self,*args,**kwargs):
        self.titre='postgreSQL'
        self.erreur=None
        self.button="testPostgreSQL()"
        

        super(postgreSQL,self).__init__(*args,**kwargs)
        self.fields['pg_ip']=forms.GenericIPAddressField(label="Adresse IP")
        self.fields['pg_port']=forms.IntegerField(label="Port",required=True)
        self.fields['pg_base']=forms.CharField(label="Nom base",max_length=17,required=True)
        self.fields['pg_user']=forms.CharField(label="Login",required=True)
        self.fields['pg_password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput)

    def is_valid(self):
        is_valid = super(postgreSQL,self).is_valid()
        if not is_valid:
            for field in self.errors.keys():
                print "ValidationError: %s" % (self.errors[field].as_text())
        else:
            try:
                testConnectionSQL(self.cleaned_data['pg_ip'],self.cleaned_data['pg_port'],self.cleaned_data['pg_base'],self.cleaned_data['pg_user'],self.cleaned_data['pg_password'])
                self.erreur=None
                return is_valid

            except ValueError as e:
                self.erreur=str(e)


class Nessus(forms.Form):
    def __init__(self,*args,**kwargs):
        self.titre='Nessus'
        self.erreur=None
        self.button="testNessus()"
    
        super(Nessus,self).__init__(*args,**kwargs)
        self.fields['nessus_ip']=forms.GenericIPAddressField(label="Adresse IP")
        self.fields['nessus_port']=forms.IntegerField(label="Port",required=True)
        self.fields['nessus_user']=forms.CharField(label="Login",required=True)
        self.fields['nessus_password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput)

    def is_valid(self):
        is_valid = super(Nessus,self).is_valid()
        if not is_valid:
            for field in self.errors.keys():
                print "ValidationError: %s" % (self.errors[field].as_text())
        else:
            try:
                testConnectionNessus(self.cleaned_data['nessus_ip'],self.cleaned_data['nessus_port'],self.cleaned_data['nessus_user'],self.cleaned_data['nessus_password'])
                self.erreur=None
                return is_valid

            except ValueError as e:
                self.erreur=str(e)


class Variables(forms.Form):
    legende="<span class='helptext'><p>Tuples séparés par des ;<br>Un tuple par ligne<br>Valeur_ajoutée_en_base;valeur_affichée<br><br>Ces données seront utilisées par les différents formulaires de l'application</p></span>"
    localisation=forms.CharField(label="Localisation",widget=forms.Textarea(attrs={'rows': 7,'cols': 80,'style': 'height: 7em;'}),help_text=mark_safe(legende),max_length=100,required=False)
    environnement=forms.CharField(label="Environnement",widget=forms.Textarea(attrs={'rows': 7,'cols': 80,'style': 'height: 7em;'}),help_text=legende,max_length=100,required=False)
    type_machine=forms.CharField(label="Type Machine",widget=forms.Textarea(attrs={'rows': 15,'cols': 80,'style': 'height: 7em;'}),help_text=legende,max_length=100,required=False)


    def clean_localisation(self):
        localisation=self.cleaned_data['localisation']

        if localisation==None or localisation=='':
            return localisation

        else:
            try:
                testTuples(localisation)
                return localisation
            except ValueError as e:
                raise forms.ValidationError(str(e))

    def clean_environnement(self):
        environnement=self.cleaned_data['environnement']

        if environnement==None or environnement=='':
            return environnement

        else:
            try:
                testTuples(environnement)
                return environnement

            except ValueError as e:
                raise forms.ValidationError(str(e))

    def clean_type_machine(self):
        type_machine=self.cleaned_data['type_machine']

        if type_machine==None or type_machine=='':
            return type_machine

        else:
            try:
                testTuples(type_machine)
                return type_machine

            except ValueError as e:
                raise forms.ValidationError(str(e))  



    def is_valid(self):
        is_valid = super(Variables,self).is_valid()
        return is_valid

        if not is_valid:
            for field in self.errors.keys():
                print "ValidationError: %s" % (self.errors[field].as_text())



class rapport(forms.Form):
        logo = forms.ImageField(label='Logo',help_text=mark_safe("<span class='helptext'><p>Ce logo sera affiché en page de guarde du rapport</p></span>"))
        societe=forms.CharField(label="Nom Societe",max_length=30,required=True,help_text=mark_safe("<span class='helptext'><p>le nom de la société apparaîtra dans les entêtes et pied de page des rapports</p></span>"))
        auteur=forms.CharField(label="Auteur",max_length=17,required=True,help_text=mark_safe("<span class='helptext'><p>le nom de l'auteur apparaîtra dans les entêtes et pied de page des rapports</p></span>"))



class utilisateurs(forms.Form):
    nom=forms.CharField(label="Nom",max_length=30,required=True)
    prenom=forms.CharField(label="Prenom",max_length=30,required=True)
    email=forms.EmailField(label="Email",max_length=30,required=True)
    login=forms.CharField(label="Login",max_length=30,required=True)
    password=forms.CharField(label="Password",max_length=30,required=True,widget=forms.PasswordInput)



class importTAR(forms.Form):
    backup_file = forms.FileField()




    

    
