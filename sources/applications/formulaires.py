#-*- coding: utf-8 -*-
from django import forms
from django.conf import settings
import ConfigParser
import codecs

BASE=settings.BASE_DIR+'/'

class formFiltreApplis(forms.Form):
    '''
    Formulaire de filtrage des applications
    '''
    def __init__(self,*args,**kwargs):
        self.criticite=kwargs.pop('criticite')

        CHOIX_CRITICITE=[]

        for m  in range(len(self.criticite)):
            CHOIX_CRITICITE.append((self.criticite[m].get('criticite'), self.criticite[m].get('criticite')) )

        super(formFiltreApplis,self).__init__(*args,**kwargs)
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
            is_valid = super(formFiltreApplis,self).is_valid()
            if not is_valid:
                    for field in self.errors.keys():
                        print "ValidationError: %s[%s] <- \"%s\" %s" % (
                                type(self),
                                field,
                                self.data[field],
                                self.errors[field].as_text()
                        )
            return is_valid





class formEditApplication(forms.Form):
    '''
    Formulaire d'ajout et d'édition d'une application
    '''

    def __init__(self,*args,**kwargs):
        try:
            appli=kwargs.pop('dic')
            self.nom=appli[0].get("nom")
            desc=appli[0].get("description")
            criticite=appli[0].get("criticite")
            nb_utilisateurs=appli[0]['nb_utilisateurs']
            type_appli=appli[0]['type']
            technologies=appli[0]['technologies']
            

        except:
            self.nom=None
            desc=None
            criticite=None
            nb_utilisateurs=None
            type_appli=None
            technologies=None

        self.noms=kwargs.pop('dic_noms')

        Config = ConfigParser.ConfigParser()
        Config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
        self.CHOIX_CRITICITE=Config.items('CRITICITE')
        self.CHOIX_CRITICITE.append((None,'A definir'))

        self.mode=kwargs.pop('mode')

        super(formEditApplication,self).__init__(*args,**kwargs)
        self.fields['nom']=forms.CharField(label="Nom",initial=self.nom,required=True,max_length=50)
        self.fields['criticite']=forms.CharField(label='Criticite',initial=criticite,widget=forms.Select( choices=self.CHOIX_CRITICITE),required=True,max_length=10)
        self.fields['desc']=forms.CharField(label="Description",widget=forms.Textarea,initial=desc,max_length=65536,required=False)
        self.fields['nb_utilisateurs']=forms.IntegerField(label="Nombre Utilisateurs",initial=nb_utilisateurs,required=False)
        self.fields['type_appli']=forms.CharField(label="Type",initial=type_appli,max_length=50,required=False,max_length=50)
        self.fields['technologies']=forms.CharField(label="Technologies",widget=forms.Textarea,initial=technologies,max_length=250,required=False)



    def clean_criticite(self):
        criticite=self.cleaned_data['criticite']
        liste_criticite=[]

        for crit in self.CHOIX_CRITICITE:
            liste_criticite.append(crit[0])

        if criticite in liste_criticite:
            return criticite

        else:
            raise forms.ValidationError('criticite non valide')



    def clean_nom(self):
        nom=str(self.cleaned_data['nom'])
        NOM_EXISTANT=[]

        if nom==None:
            return forms.ValidationError('Le nom ne peut etre vide')

        for m  in range(len(self.noms)):
            NOM_EXISTANT.append((self.noms[m].get('nom')))


        for j  in range(len(self.noms)):
            NOM_EXISTANT.append(self.noms[j].get('nom'))

        if (self.mode=='edit' and nom!=str(self.nom)) or self.mode=='ajout':
            if nom in NOM_EXISTANT:
                raise forms.ValidationError('Application déjà présente dans la base')
            else:
                return nom

        else:
            return nom
        

                                    
    def is_valid(self):
            is_valid = super(formEditApplication,self).is_valid()
            if not is_valid:
                    for field in self.errors.keys():
                        print "ValidationError: %s[%s] <- \"%s\" %s" % (
                                type(self),
                                field,
                                self.data[field],
                                self.errors[field].as_text()
                        )
            return is_valid
            

