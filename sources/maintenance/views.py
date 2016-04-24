#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import redirect,render
from fonctions import *
from django.db import connection
from django.contrib.auth.decorators import login_required
from django.template.context_processors import csrf
from django.views.decorators.csrf import ensure_csrf_cookie
from formtools.wizard.views import CookieWizardView
from django.utils.encoding import smart_str
from django.core.files.storage import FileSystemStorage
from formulaires import *
import ConfigParser
import codecs
from django.conf import settings
import os,sys,subprocess
import fileinput
from django_ajax.decorators import ajax
from tests_wizard import *
from dump import *
from django.core.files import File
import datetime
import pytz
import time
from passlib.hash import django_pbkdf2_sha256 as django_password


BASE=settings.BASE_DIR+'/'


@ajax
def connectionSQL(request):
    host=request.POST['host']
    port=request.POST['port']
    database=request.POST['database']
    user=request.POST['user']
    password=request.POST['password']

    try:
        testConnectionSQL(host,port,database,user,password)
        return 'OK'
    except ValueError as e:        
        return str(e)

@ajax
def connectionNessus(request):
    host=request.POST['host']
    port=request.POST['port']
    user=request.POST['user']
    password=request.POST['password']

    try:
        testConnectionNessus(host,port,user,password)
        return 'OK'
    except ValueError as e:        
        return str(e)



class InitWizard(CookieWizardView):
    """
    Cette vue permet d'initialiser le projet
    """

    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
    initialiser=config.get('PROJET','Initialiser')

    file_storage = FileSystemStorage(location=BASE+'maintenance/temp/')

    initial= {
        '0': {
            'pg_ip':'postgresql',
            'pg_port': '5432',
            'pg_base': 'django',
            'pg_user': 'django_db',
            'pg_password': 'Django_DB_Pa$$Word'},
        '1': {
            'nessus_ip':'nessus',
            'nessus_port': '8834',
            'pg_user': '',
            'pg_password': ''}}

    form_list=postgreSQL, Nessus,Variables
    initial_dict=initial


    def get_context_data(self,form,**kwargs):
        context=super(InitWizard,self).get_context_data(form=form,**kwargs)
        context.update({'already_init':self.initialiser})
        return context

    def get_template_names(self):
        '''
        Cette fonction permet de renvoyer le template
        2 templates existes:
            - 1 sans menu > utiliser lors de la toute premiere connexion
            - 2 le second > utiliser une fois le site initialiser
        '''
        if self.initialiser=='NO':
            return 'maintenance/wizard_zero.html'
        else:
            return 'maintenance/wizard.html'


    def done(self,form_list, **kwargs):
        #Modification du fichier settings.py
        #Formulaire 0
        tempFile = open(BASE+'soc/settings.tmp', 'w')

        host=str(form_list[0].cleaned_data['pg_ip'])
        port=int(form_list[0].cleaned_data['pg_port'])
        database=str(form_list[0].cleaned_data['pg_base'])
        user=str(form_list[0].cleaned_data['pg_user'])
        password=str(form_list[0].cleaned_data['pg_password'])

        dic=[
            ("'HOST':","\t\t'HOST':'"+host+"',\n"),
            ("'PORT':","\t\t'PORT':'"+str(port)+"',\n"),
            ("'NAME':","\t\t'NAME':'"+database+"',\n"),
            ("'USER':","\t\t'USER':'"+user+"',\n"),
            ("'PASSWORD':","\t\t'PASSWORD':'"+password+"',\n"),
        ]

        for line in fileinput.input(BASE+'soc/settings.py'):
            trouve=False

            for tuple_texte in dic:
                if tuple_texte[0] in line:
                    tempFile.write(line.replace(line,tuple_texte[1]))
                    trouve=True
                    dic.remove(tuple_texte)
                    break

            if trouve==False:
                tempFile.write(line)

        tempFile.close()
        del dic
        os.rename(BASE+'soc/settings.tmp',BASE+'soc/settings.py')


        #Cette etape permet de mettr een page principale la page d'authentification
        tempFile = open(BASE+'soc/urls.tmp', 'w')
        texte_remplacement="url(r'^$',views.login_view,name='login_view'),"
        texte_recherche="url(r'^$',include('maintenance.urls',app_name='maintenance',namespace='maintenance')),"

        for line in fileinput.input(BASE+'soc/urls.py'):
            if texte_recherche in line:
                tempFile.write(line.replace(line,texte_remplacement))

            else:
                tempFile.write(line)

        tempFile.close()
        os.rename(BASE+'soc/urls.tmp',BASE+'soc/urls.py')


        initialiserPG(BASE+'maintenance/django.pg',host,port,database,user,password)


        #Modification du fichier default.cfg
        #Formulaire 1 et 2
        self.config.set('Nessus','Adresse',str(form_list[1].cleaned_data['nessus_ip']))
        self.config.set('Nessus','Port',str(form_list[1].cleaned_data['nessus_port']))
        self.config.set('Nessus','Login',str(form_list[1].cleaned_data['nessus_user']))
        self.config.set('Nessus','Password',str(form_list[1].cleaned_data['nessus_password']))


        self.config.remove_section('LOCALISATION')
        self.config.add_section('LOCALISATION')

        for localisation in form_list[2].cleaned_data['localisation'].split('\r\n'):
            loc_tuple=localisation.split(';')
            try:
                self.config.set('LOCALISATION',loc_tuple[0],loc_tuple[1])
            except IndexError:
                pass
            

        self.config.remove_section('ENVIRONNEMENT')
        self.config.add_section('ENVIRONNEMENT')


        for environnement in form_list[2].cleaned_data['environnement'].split('\r\n'):
            env_tuple=environnement.split(';')
            try:
                self.config.set('ENVIRONNEMENT',env_tuple[0],env_tuple[1])
            except IndexError:
                pass

        self.config.remove_section('TYPE')
        self.config.add_section('TYPE')


        for type_machine in form_list[2].cleaned_data['type_machine'].split('\r\n'):
            machine_tuple=type_machine.split(';')
            try:
                self.config.set('TYPE',machine_tuple[0],machine_tuple[1])
            except IndexError:
                pass

        with open(BASE+"soc/default.cfg", 'wb',0) as configfile:
            self.config.write(configfile)

        #Formulaire 3
        #Importation de l'image
        image=form_list[3].cleaned_data['logo']#self.request.FILES['logo']
        image_name=image._get_name()
        image_path=BASE+'static/img/'

        image_file=open(image_path+image_name,'wb',0)
    
        for chunk in image.chunks():
            image_file.write(chunk)

        image_file.close()

        self.config.remove_section('Rapports')
        self.config.add_section('Rapports')
        self.config.set('Rapports','Logo',str(image_name))
        self.config.set('Rapports','Societe',str(form_list[3].cleaned_data['societe']))
        self.config.set('Rapports','Auteur',str(form_list[3].cleaned_data['auteur']))

        with open(BASE+"soc/default.cfg", 'wb') as configfile:
            self.config.write(configfile)


        os.chdir(BASE)
        subprocess.check_output("python "+BASE+"manage.py generate_secret_key", shell=True)
        subprocess.check_output("python "+BASE+"manage.py migrate", shell=True)
        os.popen("touch "+BASE+'soc/wsgi.py')

        #Formulaire 4: utilisateur django
        nom=form_list[4].cleaned_data['nom']
        prenom=form_list[4].cleaned_data['prenom']
        email=form_list[4].cleaned_data['email']
        login=form_list[4].cleaned_data['login']
        password=form_list[4].cleaned_data['password']

        tz = pytz.timezone('Europe/Paris')
        d=datetime.datetime.now()
        date_creation=tz.localize(d)

        password=django_password.encrypt(password,rounds=24000)


        import django.conf
        reload(django.conf)
        from django.conf import settings

        cursor=connection.cursor()
        cursor.execute('''INSERT INTO auth_user (first_name,last_name,email,username,password,date_joined,is_superuser,is_staff,is_active) 
                            VALUES(%s,%s,%s,%s,%s,%s,True,True,True)''',[nom,prenom,email,login,password,date_creation])

        password='666'*20
        del password

        self.config.set('PROJET','Initialiser','YES')
        with open(BASE+"soc/default.cfg", 'wb') as configfile:
            self.config.write(configfile)

        return redirect('serveurs:liste')  


@login_required
@ensure_csrf_cookie
def export(request):
    '''
    Cette fonction permet de sauveguarder:
        - les fichiers de config (settings.py, default.cfg)
        - la base de donnée
    '''
    if request.method=='POST':
        nom_archive,file_tar=exportProjet()

        response = HttpResponse(file_tar,content_type='application/tar')
        response['Content-Disposition'] = 'attachment; filename=%s' % smart_str(nom_archive)
        response['X-Sendfile'] = smart_str(nom_archive)

        return response

    else:
        return render(request, 'maintenance/export.html')


@login_required
@ensure_csrf_cookie
def importConfig(request):
    if request.method=='POST':
        form=importTAR(request.POST, request.FILES)

        if form.is_valid():

            importProjet(request.FILES['backup_file'])

            return redirect('serveurs:liste')


        else:
             return render(request, 'maintenance/import.html', locals())      

    else:
        form=importTAR()

        return render(request, 'maintenance/import.html', locals())
    
    
    

        
