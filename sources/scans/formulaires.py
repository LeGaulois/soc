#-*- coding: utf-8 -*-
from django import forms
from fonctions import valideIP,valideMAC
import re


class scanPlannifie(forms.Form):
    '''
    Formulaire de création et d'éditions d'un scan Plannifié
    '''
    def __init__(self,*args,**kwargs):

        try:
            scan=kwargs.pop('scan')        
            self.nom=scan['nom']
            self.description=scan['description']
            self.nmap=scan['nmap']
            self.nmapOptions=scan['nmap_options']
            self.nessus=scan['nessus']
            self.nessus_policy=scan['nessus_policy_id']
            self.jours=scan['jours_execution']
                

        except:
            self.nom=''
            self.description=''
            self.nmap=False
            self.nmapOptions='-A -sS -sU'
            self.nessus=False
            self.nessus_policy=''
            self.jours=''

        try:
            self.mode=kwargs.pop('mode')

        except:
            self.mode='ajout'    



        #################################################
        self.LISTE_JOUR=[('lundi','lundi'),
('mardi','mardi'),
('mercredi','mercredi'),
('jeudi','jeudi'),
('vendredi','vendredi'),
('samedi','samedi'),
('dimanche','dimanche')
]

        JOURS_SELECTIONNES=[]
    
        try:
            for j in self.jours.split(';'):
                JOURS_SELECTIONNES.append(j)
        except:
            pass


        ###########
        self.liste_noms=[]

        try:
            self.liste_noms=kwargs.pop('liste_noms')

            for nom in self.liste_noms:
                self.liste_noms.append(nom['nom'])
        except:
            pass
        


        selection_initiale=''
        #####################
        IP_SELECTIONNEES=[]

        try:
            liste_ip_selectionnees=kwargs.pop('liste_ip_selectionnees')
            selection_initiale='id_adresses' if len(liste_ip_selectionnees)>0 else ''
            for j  in range(len(liste_ip_selectionnees)):
                IP_SELECTIONNEES.append(liste_ip_selectionnees[j]['ip_hote'])

            del liste_ip_selectionnees
        except:
            pass


        ##############
        liste_ip_existantes=kwargs.pop('liste_ip_existantes')
        LISTE_IP=[]

        for i  in range(len(liste_ip_existantes)):
            ip=liste_ip_existantes[i]['ip']
            LISTE_IP.append((ip,ip))

            #if ip in IP_SELECTIONNEES:
            #    LISTE_VALIDATION.append(True)

            #else:
            #    LISTE_VALIDATION.append(True)

        del liste_ip_existantes
        

        ######### APPLIS ###############
        liste_appli=kwargs.pop('liste_appli')
        LISTE_APPLI=[]

        for i  in range(len(liste_appli)):
            nom=liste_appli[i]['nom']
            LISTE_APPLI.append((nom,nom))
        


        APPLIS_SELECTIONNEES=[]
        
        try:
            liste_applis_selectionnees=kwargs.pop('liste_applis_selectionnees')
            
            selection_initiale='id_applis' if len(liste_applis_selectionnees)>0 else selection_initiale
            for j  in range(len(liste_applis_selectionnees)):
                APPLIS_SELECTIONNEES.append(liste_applis_selectionnees[j]['nom'])

            del liste_applis_selectionnees
        except:
            pass

        ########## POLICY ########################

        LISTE_POLICIES=[]

        try:
            liste_policies=kwargs.pop('liste_policies')

            for policy in liste_policies:
                LISTE_POLICIES.append((policy['id'],policy['name']))

            del liste_policies

        except:
            pass

    
        

        super(scanPlannifie,self).__init__(*args,**kwargs)
        self.fields['nom']=forms.CharField(label="Nom",max_length=50,initial=self.nom,required=True,max_length=30)
        self.fields['description']=forms.CharField(label='Description',initial=self.description,max_length=200,required=False)
        self.fields['nmap']=forms.BooleanField(label="Scan Nmap",initial=self.nmap,required=False)
        self.fields['nmapOptions']=forms.CharField(label='Options Nmap',initial=self.nmapOptions,required=False,max_length=50)
        self.fields['nessus']=forms.BooleanField(label="Scan Nessus",initial=self.nessus,required=False)
        self.fields['nessus_policy']=forms.CharField(label="Nessus Policy",max_length=40,initial=self.nessus_policy,widget=forms.Select( choices=LISTE_POLICIES),required=True)
        self.fields['jours']=forms.MultipleChoiceField(label='Jours',choices=self.LISTE_JOUR,required=False, widget=forms.SelectMultiple(attrs={'size':'7'}))
        self.initial['jours']=JOURS_SELECTIONNES

        self.fields['type_selection']=forms.CharField(label="Selection par",max_length=40,widget=forms.Select( choices=[('',''),('id_adresses','adresses ip'),('id_applis','applications')],attrs={'onchange':'Selection()','onload':'Selection()'}),required=True,initial=selection_initiale)
        self.fields['adresses']=forms.MultipleChoiceField(label='Adresses',choices=LISTE_IP,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))
        self.initial['adresses']=IP_SELECTIONNEES
        self.fields['applis']=forms.MultipleChoiceField(label='Applis',choices=LISTE_APPLI,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))
        self.initial['applis']=APPLIS_SELECTIONNEES




    def clean_nom(self):
        nom=self.cleaned_data['nom']

        if (self.mode=='edit'):
            try:
                self.liste_noms.remove(nom)
            except:
                pass
    
        if nom in self.liste_noms:
            raise forms.ValidationError('Nom du scan deja existant')

        else:
            return nom


    def clean_nmapOptions(self):
        error=re.search('[;|<>]',self.cleaned_data['nmapOptions'])

        if error!=None:
            raise forms.ValidationError('Options invalides')

        else:
            return self.cleaned_data['nmapOptions']
                                        
    def is_valid(self):
            is_valid = super(scanPlannifie,self).is_valid()
            if not is_valid:
                    for field in self.errors.keys():
                        print "ValidationError: %s[%s] <- \"%s\" %s" % (
                                type(self),
                                field,
                                self.data[field],
                                self.errors[field].as_text()
                        )
            return is_valid



class scanManuel(forms.Form):
    '''
    Formulaire de création et d'éditions d'un scan manuel
    '''
    def __init__(self,*args,**kwargs):

        ip=kwargs.pop('ip')

        if ip is None:
            selection_initiale=''
            liste_ip=kwargs.pop('liste_ip')
            LISTE_IP=[]

            for i  in range(len(liste_ip)):
                adresse=liste_ip[i]['ip']
                LISTE_IP.append((adresse,adresse))


            

            liste_appli=kwargs.pop('liste_appli')
            LISTE_APPLI=[]

            for i  in range(len(liste_appli)):
                nom=liste_appli[i]['nom']
                LISTE_APPLI.append((nom,nom))
    
    
        else:
            liste_appli=kwargs.pop('liste_appli')
            liste_ip=kwargs.pop('liste_ip')

        del liste_appli
        del liste_ip

        LISTE_POLICIES=[]

        try:
            liste_policies=kwargs.pop('liste_policies')

            for policy in liste_policies:
                LISTE_POLICIES.append((policy['id'],policy['name']))

            del liste_policies

        except:
            pass

    
        

        super(scanManuel,self).__init__(*args,**kwargs)
        self.fields['nmap']=forms.BooleanField(label="Scan Nmap",initial=False,required=False)
        self.fields['nmapOptions']=forms.CharField(label='Options Nmap',initial='-A -sS -sU',required=False,max_length=50)
        self.fields['nessus']=forms.BooleanField(label="Scan Nessus",initial=False,required=False)
        self.fields['nessus_policy']=forms.CharField(label="Nessus Policy",max_length=40,widget=forms.Select( choices=LISTE_POLICIES),required=True)

        if ip is None:
            self.fields['type_selection']=forms.CharField(label="Selection par",max_length=40,widget=forms.Select( choices=[('',''),('id_adresses','ip'),('id_applis','appli')],attrs={'onchange':'Selection()'}),required=True,initial=selection_initiale)
            self.fields['adresses']=forms.MultipleChoiceField(label='Adresses',choices=LISTE_IP,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))
            self.fields['applis']=forms.MultipleChoiceField(label='Applis',choices=LISTE_APPLI,required=False, widget=forms.SelectMultiple(attrs={'size':'10','style':'display:none'}))


    def clean_nmapOptions(self):
        error=re.search('[;|<>]',self.cleaned_data['nmapOptions'])

        if error!=None:
            raise forms.ValidationError('Options invalides')

        else:
            return self.cleaned_data['nmapOptions']
        
                                
    def is_valid(self):
            is_valid = super(scanManuel,self).is_valid()
            if not is_valid:
                    for field in self.errors.keys():
                        print "ValidationError: %s[%s] <- \"%s\" %s" % (
                                type(self),
                                field,
                                self.data[field],
                                self.errors[field].as_text()
                        )
            return is_valid
