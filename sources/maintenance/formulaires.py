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
        self.fields['pg_ip']=forms.CharField(label="Adresse IP",widget=forms.TextInput(attrs={'id':"postgresql_addr"}))
        self.fields['pg_port']=forms.IntegerField(label="Port",required=True,widget=forms.NumberInput(attrs={'id':"postgresql_port"}))
        self.fields['pg_base']=forms.CharField(label="Nom base",max_length=17,required=True,widget=forms.TextInput(attrs={'id':"postgresql_database"}))
        self.fields['pg_user']=forms.CharField(label="Login",required=True,widget=forms.TextInput(attrs={'id':"postgresql_login"}))
        self.fields['pg_password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput(attrs={'id':"postgresql_password"}, render_value=True))

    def clean_pg_ip(self):
        ip=self.cleaned_data['pg_ip']

        if ip=='postgresql':
            return 'postgresql'

        try:
            ip=valideIP(ip)
            return ip
        except:
            raise forms.ValidationError('adresse IP non valide')


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
        self.fields['nessus_ip']=forms.CharField(label="Adresse IP",widget=forms.TextInput(attrs={'id':"nessus_addr"}))
        self.fields['nessus_port']=forms.IntegerField(label="Port",required=True,widget=forms.NumberInput(attrs={'id':"nessus_port"}))
        self.fields['nessus_user']=forms.CharField(label="Login",required=True,widget=forms.TextInput(attrs={'id':"nessus_login"}))
        self.fields['nessus_password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput(attrs={'id': "nessus_password"},render_value=True))

    def clean_nessus_ip(self):
        ip=self.cleaned_data['nessus_ip']

        if ip=='nessus':
            return 'nessus'

        try:
            ip=valideIP(ip)
            return ip
        except:
            raise forms.ValidationError('adresse IP non valide')


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
    localisation=forms.CharField(label="Localisation",widget=forms.Textarea(attrs={'rows': 7,'cols': 80,'style': 'height: 7em; width:30em;'}),help_text=mark_safe(legende),max_length=200,required=False)
    environnement=forms.CharField(label="Environnement",widget=forms.Textarea(attrs={'rows': 7,'cols': 80,'style': 'height: 7em; width:30em;'}),help_text=legende,max_length=200,required=False)
    type_machine=forms.CharField(label="Type Machine",widget=forms.Textarea(attrs={'rows': 15,'cols': 80,'style': 'height: 12em; width: 30em;'}),help_text=legende,max_length=200,required=False)


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



class email(forms.Form):
    def __init__(self,*args,**kwargs):
        self.titre='Mail'
        self.erreur=None
        self.button="testMail()"

        super(email,self).__init__(*args,**kwargs)
        self.fields['serveur']=forms.CharField(label="Serveur SMTP",max_length=50,required=True,widget=forms.TextInput(attrs={'id':"mail_addr"}))
        self.fields['port']=forms.IntegerField(label="Port",required=True,widget=forms.NumberInput(attrs={'id':"mail_port"}))
        self.fields['email']=forms.EmailField(label="Mail",max_length=50,required=True,widget=forms.EmailInput(attrs={'id':"mail_login"}))
        self.fields['password']=forms.CharField(label="Mot de passe",max_length=50,required=True,widget=forms.PasswordInput(attrs={'id':"mail_password"}))
        self.fields['tls']=forms.BooleanField(label='tls',widget=forms.CheckboxInput(attrs={'id':'mail_tls'}))


    def is_valid(self):
        is_valid = super(email,self).is_valid()
        if not is_valid:
            for field in self.errors.keys():
                print "ValidationError: %s" % (self.errors[field].as_text())
        else:
            try:
                testConnectionMail(self.cleaned_data['serveur'],self.cleaned_data['port'],self.cleaned_data['email'],self.cleaned_data['password'],self.cleaned_data['tls'])
                self.erreur=None
                return is_valid

            except ValueError as e:
                self.erreur=str(e)


class utilisateurs(forms.Form):
    nom=forms.CharField(label="Nom",max_length=30,required=True)
    prenom=forms.CharField(label="Prenom",max_length=30,required=True)
    email=forms.EmailField(label="Email",max_length=30,required=True)
    login=forms.CharField(label="Login",max_length=30,required=True)
    password=forms.CharField(label="Password",max_length=30,required=True,widget=forms.PasswordInput)



class importTAR(forms.Form):
    backup_file = forms.FileField()


class modifNessus(forms.Form):
    def __init__(self,*args,**kwargs):
        addr=kwargs.pop('addr')
        port=kwargs.pop('port')
        login=kwargs.pop('login')
        password=kwargs.pop('password')
        directory_id=kwargs.pop('directory_id')
        verify=kwargs.pop('verify')

        self.titre="Paramètres de connexion au serveur NESSUS"
        self.test="testNessus()"
        self.commit="validerNessus()"

        super(modifNessus,self).__init__(*args,**kwargs)
        self.fields['addr']=forms.CharField(label="Adresse IP",required=True,initial=addr,widget=forms.TextInput(attrs={'id':"nessus_addr"}))
        self.fields['port']=forms.IntegerField(label="Port",required=True,initial=port,widget=forms.NumberInput(attrs={'id':"nessus_port"}))
        self.fields['login']=forms.CharField(label="Login",required=True,initial=login,widget=forms.TextInput(attrs={'id':"nessus_login"}))
        self.fields['password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput(attrs={'id':'nessus_password'},render_value=True),initial=password)
        self.fields['directory_id']=forms.CharField(label="Directory ID",initial=directory_id,widget=forms.TextInput(attrs={'id':"nessus_directory-id"}))
        self.fields['verify']=forms.BooleanField(label="Verify",initial=verify,widget=forms.CheckboxInput(attrs={'id':"nessus_verify"}))


class modifMail(forms.Form):
    def __init__(self,*args,**kwargs):
        addr=kwargs.pop('addr')
        port=kwargs.pop('port')
        login=kwargs.pop('login')
        password=kwargs.pop('password')
        tls=kwargs.pop('tls')

        self.titre="Paramètres de connexion au serveur SMTP"
        self.test="testMail()"
        self.commit="validerMail()"


        super(modifMail,self).__init__(*args,**kwargs)
        self.fields['addr']=forms.CharField(label="Adresse IP",required=True,initial=addr,widget=forms.TextInput(attrs={'id':"mail_addr"}))
        self.fields['port']=forms.IntegerField(label="Port",required=True,initial=port,widget=forms.NumberInput(attrs={'id':"mail_port"}))
        self.fields['login']=forms.CharField(label="Login",required=True,initial=login,widget=forms.EmailInput(attrs={'id':"mail_login"}))
        self.fields['password']=forms.CharField(label="Password",required=True,widget=forms.PasswordInput(attrs={'id':'mail_password'},render_value=True),initial=password)
        self.fields['tls']=forms.BooleanField(label="TLS",widget=forms.CheckboxInput(attrs={'id':"mail_tls"}),initial=tls)



class modifVariables(forms.Form):
    def __init__(self,*args,**kwargs):
        loc=kwargs.pop('localisations')
        env=kwargs.pop('environnements')
        typ=kwargs.pop('types')

        self.titre="Variables de machines"
        self.test=None
        self.commit="validerVariables()"

        super(modifVariables,self).__init__(*args,**kwargs)
        self.fields['localisation']=forms.CharField(label="Localisation",widget=forms.Textarea(attrs={'rows': 7,'cols': 80,'style': 'height: 7em; width:30em;','id':'var_localisation'}),max_length=100,required=False,initial=loc)
        self.fields['environnement']=forms.CharField(label="Environnement",widget=forms.Textarea(attrs={'rows': 7,'cols': 80,'style': 'height: 7em; width:30em;','id':'var_environnement'}),max_length=100,required=False,initial=env)
        self.fields['type_machine']=forms.CharField(label="Type Machine",widget=forms.Textarea(attrs={'rows': 15,'cols': 80,'style': 'height: 12em; width:30em;','id':'var_type'}),max_length=100,required=False,initial=typ)


class modifInfosRapports(forms.Form):
    def __init__(self,*args,**kwargs):
        logo=kwargs.pop('logo')
        societe=kwargs.pop('societe')
        auteur=kwargs.pop('auteur')

        self.titre="Paramètres des rapports"
        self.test=None
        self.commit="validerInfosRapports()"


        super(modifInfosRapports,self).__init__(*args,**kwargs)
        self.fields['societe']=forms.CharField(label="Societe",required=True,initial=societe,widget=forms.TextInput(attrs={'id':'infos-rapports_societe'}))
        self.fields['auteur']=forms.CharField(label="Auteur",required=True,initial=auteur,widget=forms.TextInput(attrs={'id':'infos-rapports_auteur'}))
        self.fields['logo']=forms.ImageField(label="logo",help_text=mark_safe("<span class='helptext'><p>Aucun changement si aucun fichier uploader</p></span>"),widget=forms.FileInput(attrs={'id':'infos-rapports_logo'}),initial=logo)


