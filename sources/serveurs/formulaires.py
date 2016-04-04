#-*- coding: utf-8 -*-
from django import forms
from fonctions import valideIP,valideMAC
import ConfigParser
import codecs
from django.conf import settings

class formUploadXML(forms.Form):
        file = forms.FileField()

##############################################################################################################################"
class formFiltreMachines(forms.Form):
    def __init__(self,*args,**kwargs):
        self.os=kwargs.pop('os')        
        self.applis=kwargs.pop('appli')
        self.typ=kwargs.pop('typ')
        self.criticite=kwargs.pop('criticite')
        self.vulnerabilite=kwargs.pop('vulnerabilite')
        self.localisation=kwargs.pop('localisation')
        self.environnement=kwargs.pop('environnement')

        CHOIX_OS=[]
        CHOIX_TYPE=[]
        CHOIX_APPLI=[]
        CHOIX_CRITICITE=[]
        CHOIX_VULNERABILITE=[]
        CHOIX_LOCALISATION=[]
        CHOIX_ENVIRONNEMENT=[]

        CHOIX_OS.append((None,''))
        for i  in range(len(self.os)):
            CHOIX_OS.append((self.os[i].get('os'),self.os[i].get('os')) )

        CHOIX_VULNERABILITE.append((None,''))
        for j  in range(len(self.vulnerabilite)):
            CHOIX_VULNERABILITE.append((self.vulnerabilite[j].get('vulnerabilite'),self.vulnerabilite[j].get('vulnerabilite')) )

        
        CHOIX_APPLI.append((None,''))
        for k  in range(len(self.applis)):
            CHOIX_APPLI.append((self.applis[k]['nom'], self.applis[k]['nom']) )
        
        for l  in range(len(self.typ)):
            CHOIX_TYPE.append((self.typ[l].get('type_machine'), self.typ[l].get('type_machine')) )

        CHOIX_CRITICITE.append((None,''))
        for m  in range(len(self.criticite)):
            CHOIX_CRITICITE.append((self.criticite[m].get('criticite'), self.criticite[m].get('criticite')) )
    
        CHOIX_ENVIRONNEMENT.append((None,''))
        for o  in range(len(self.environnement)):
            CHOIX_ENVIRONNEMENT.append((self.environnement[o].get('environnement'), self.environnement[o].get('environnement')) )

        for n  in range(len(self.localisation)):
            CHOIX_LOCALISATION.append((self.localisation[n].get('localisation'), self.localisation[n].get('localisation')) )


        super(formFiltreMachines,self).__init__(*args,**kwargs)
        self.fields['os']=forms.CharField(label="OS",max_length=60,initial=None,widget=forms.Select( choices=CHOIX_OS),required=False)
        self.fields['type_machine']=forms.CharField(label='Type machine',initial='',widget=forms.Select( choices=CHOIX_TYPE),required=False)
        self.fields['environnement']=forms.CharField(label='Environnement',initial='',widget=forms.Select( choices=CHOIX_ENVIRONNEMENT),required=False)
        self.fields['appli']=forms.CharField(label="Application",initial=None,widget=forms.Select( choices=CHOIX_APPLI),required=False)
        self.fields['criticite']=forms.CharField(label='Criticite',initial=None,widget=forms.Select(choices=CHOIX_CRITICITE),required=False)
        self.fields['vulnerabilite']=forms.CharField(label='Vulnerabilite',initial=None,widget=forms.Select(choices=CHOIX_VULNERABILITE),required=False)
        self.fields['localisation']=forms.CharField(label='Localisation',initial='',widget=forms.Select( choices=CHOIX_LOCALISATION),required=False)

    def clean_os(self):
        systeme_exploitation=self.cleaned_data['os']
        os_valide=["",None]

        for j  in range(len(self.os)):
            os_valide.append(self.os[j]['os'])


        if systeme_exploitation in os_valide:
            return systeme_exploitation

        else:
            raise forms.ValidationError('OS non valide')

    def clean_type_machine(self):
        type_machine=self.cleaned_data['type_machine']
        type_machine_valide=["",None]

        for j  in range(len(self.typ)):
            type_machine_valide.append(self.typ[j].get('type_machine'))

        if type_machine in type_machine_valide:
            return type_machine

        else:
            raise forms.ValidationError('type de machine non valide')
    
    def clean_appli(self):
        application=self.cleaned_data['appli']
        applications_valide=["",None]

        for j  in range(len(self.applis)):
            applications_valide.append(self.applis[j]['nom'])

        if application in applications_valide:
            return application

        else:
            raise forms.ValidationError('application non valide')
    
    def clean_criticite(self):
        niveauCriticite=self.cleaned_data['criticite']
        criticite_valide=["",None]

        for j  in range(len(self.criticite)):
            criticite_valide.append(self.criticite[j].get('criticite'))

        if niveauCriticite in criticite_valide:
            return niveauCriticite

        else:
            raise forms.ValidationError('Criticite non valide')

    def clean_vulnerabilite(self):
        niveauVulnerabilite=self.cleaned_data['vulnerabilite']
        vulnerabilite_valide=["",None]

        for j  in range(len(self.vulnerabilite)):
            vulnerabilite_valide.append(self.vulnerabilite[j].get('vulnerabilite'))

        if niveauVulnerabilite in vulnerabilite_valide:
            return niveauVulnerabilite

        else:
            raise forms.ValidationError('Vulnerabilite non valide')



    def clean_localisation(self):
        lieu=self.cleaned_data['localisation']
        lieu_valide=["",None]

        for j  in range(len(self.localisation)):
            lieu_valide.append(self.localisation[j].get('localisation'))

        if lieu in lieu_valide:
            return lieu

        else:
            raise forms.ValidationError('Localisation non valide')

    def clean_environnement(self):
        env=self.cleaned_data['environnement']
        env_valide=["",None]

        for j  in range(len(self.environnement)):
            env_valide.append(self.environnement[j].get('environnement'))

        if env in env_valide:
            return env

        else:
            raise forms.ValidationError('Environnement non valide')
    
                                        
    def is_valid(self):
            is_valid = super(formFiltreMachines,self).is_valid()
            if not is_valid:
                    for field in self.errors.keys():
                        print "ValidationError: %s[%s] <- \"%s\" %s" % (
                                type(self),
                                field,
                                self.data[field],
                                self.errors[field].as_text()
                        )
            return is_valid




########################################################################################################################"
class formEditMachine(forms.Form):

    def __init__(self,*args,**kwargs):

        self.mode=kwargs.pop('mode')
        selection_initiale='id_appli'

        if self.mode=='edit':
            serv=kwargs.pop('dic')
            self.adresse=serv[0].get("ip")
            mac=serv[0].get("mac")
            hostname=serv[0].get("hostname")
            os=serv[0].get("os")
            localisation=serv[0].get("localisation")
            type_machine=serv[0].get("type_machine")
            commentaires=serv[0].get("commentaires")
            environnement=serv[0]["environnement"]

            liste_applis=kwargs.pop('appli_hote')


            APPLIS_SELECTIONNEES=[]
            application=None

            taille_liste=len(liste_applis)

            if taille_liste==1:
                application=liste_applis[0]['nom']

            elif taille_liste==0:
                application=''

            else:
                selection_initiale='id_backend'
                for appli in liste_applis:
                    APPLIS_SELECTIONNEES.append(appli['nom'])
    
            del taille_liste
            del liste_applis
            self.adresses=[]
    
        else:
            self.adresses=kwargs.pop('liste_adresses')
            mode=None
            self.adresse=None
            mac=None
            hostname=None
            os=None
            localisation=None
            type_machine=None
            commentaires=None
            application=None
            environnement=None
            APPLIS_SELECTIONNEES=[]


        
        self.applis=kwargs.pop('dic_applis')

        CHOIX_APPLI=[(None,'inconnue')]

        for k  in range(len(self.applis)):
            CHOIX_APPLI.append((self.applis[k].get('nom'), self.applis[k].get('nom')) )

        BASE=settings.BASE_DIR+'/'
        Config = ConfigParser.ConfigParser()
        Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

        self.CHOIX_LOCALISATION=Config.items('LOCALISATION')
        self.CHOIX_LOCALISATION.append(('','A definir'))

        self.CHOIX_TYPE=Config.items('TYPE')
        self.CHOIX_TYPE.append(('','A definir'))

        self.CHOIX_ENVIRONNEMENT=Config.items('ENVIRONNEMENT')
        self.CHOIX_ENVIRONNEMENT.append(('','A definir'))


        super(formEditMachine,self).__init__(*args,**kwargs)
        self.fields['adresse']=forms.GenericIPAddressField(label="Adresse IP",initial=self.adresse)
        self.fields['mac']=forms.CharField(label="Adresse MAC",initial=mac,max_length=17,required=False)
        self.fields['hostname']=forms.CharField(label="Hostname",initial=hostname,max_length=50,required=False)
        self.fields['os']=forms.CharField(label="OS",initial=os,max_length=60)
        self.fields['type_machine']=forms.CharField(label='Type machine',initial=type_machine,widget=forms.Select( choices=self.CHOIX_TYPE),required=False)
        self.fields['environnement']=forms.CharField(label='Environnement',initial=environnement,widget=forms.Select( choices=self.CHOIX_ENVIRONNEMENT),required=False)
        

        self.fields['type_selection']=forms.CharField(label="Backend",widget=forms.Select(choices=[('id_backend','oui'),('id_appli','non')],attrs={'onchange':'Selection()','onload':'Selection()'}),required=True,initial=selection_initiale)


        self.fields['appli']=forms.CharField(label="Application",initial=application,widget=forms.Select( choices=CHOIX_APPLI,attrs={'style':'display:none'}),required=False)
        self.fields['backend']=forms.MultipleChoiceField(label='Applis',choices=CHOIX_APPLI,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))
        self.initial['backend']=APPLIS_SELECTIONNEES


        self.fields['localisation']=forms.CharField(label='Localisation',initial=localisation,widget=forms.Select( choices=self.CHOIX_LOCALISATION),required=False)
        self.fields['commentaires']=forms.CharField(label="Commentaires",widget=forms.Textarea,initial=commentaires,max_length=200,required=False)


    def clean_mac(self):
        mac=self.cleaned_data['mac']

        if (mac==None or mac==''):
            return None

        elif(valideMAC(mac)==False):
            raise forms.ValidationError('adresse MAC non valide')
        return mac


    def clean_environnement(self):
        environnement=self.cleaned_data['environnement']
        liste_environnement=[]
        
        for env in self.CHOIX_ENVIRONNEMENT:
            liste_environnement.append(env[0])

        if environnement in liste_environnement:
            return environnement

        
        else:
            raise forms.ValidationError('environnement non valide')


    def clean_appli(self):
        application=self.cleaned_data['appli']
        applications_valide=["",None]

        for j  in range(len(self.applis)):
            applications_valide.append(self.applis[j].get('nom'))

        if application in applications_valide:
            return application

        else:
            raise forms.ValidationError('application non valide')

    def clean_localisation(self):
        localisation=self.cleaned_data['localisation']
        liste_localisation=[]

        for loc in self.CHOIX_LOCALISATION:
            liste_localisation.append(loc[0])

        if localisation in liste_localisation:
            return localisation

        else:
            raise forms.ValidationError('Localisation non valide')

    def clean_type_machine(self):
        type_machine=self.cleaned_data['type_machine']
        liste_type=[]

        for type_elem in self.CHOIX_TYPE:
            liste_type.append(type_elem[0])

        if type_machine in liste_type:
            return type_machine

        else:
            raise forms.ValidationError('Type non valide')
                                            
    def is_valid(self):
            is_valid = super(formEditMachine,self).is_valid()
            if not is_valid:
                    for field in self.errors.keys():
                        print "ValidationError: %s[%s] <- \"%s\" %s" % (
                                type(self),
                                field,
                                self.data[field],
                                self.errors[field].as_text()
                        )
            return is_valid
            

        

