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
import datetime,pytz,time
from passlib.hash import django_pbkdf2_sha256 as django_password
import logging
from PIL import Image

logger = logging.getLogger(__name__)

BASE=settings.BASE_DIR+'/'


@ajax
def connectionSQL(request):
    address=request.POST['address']
    port=request.POST['port']
    database=request.POST['database']
    login=request.POST['login']
    password=request.POST['password']

    try:
        testConnectionSQL(address,port,database,login,password)
        return 'OK'
    except ValueError as e:
        return str(e)

@ajax
def connectionNessus(request):
    address=request.POST['address']
    port=request.POST['port']
    login=request.POST['login']
    password=request.POST['password']
    verify=request.POST['verify']

    try:
        testConnectionNessus(address,port,login,password,verify)
        return 'OK'
    except Exception as e:
        return str(e)


@ajax
def connectionMail(request):
    address=request.POST['address']
    port=int(request.POST['port'])
    login=request.POST['login']
    password=request.POST['password']
    tls=request.POST['tls']

    try:
        testConnectionMail(address,port,login,password,tls)
        return 'OK'

    except ValueError as e:
        return str(e)

    except Exception as e:
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
            'pg_password': 'DjangoDBPassWordSOC'},
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
        import psycopg2
        conn = psycopg2.connect(host=host,port=port,database=database,user=user,password=password)

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

        with open(BASE+"soc/default.cfg", 'wb') as configfile:
            self.config.write(configfile)

        #Formulaire 3
        #Importation de l'image
        image=form_list[3].cleaned_data['logo']
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

        self.config.remove_section('MAIL')
        self.config.add_section('MAIL')
        self.config.set('MAIL','SMTP_Addr',str(form_list[4].cleaned_data['serveur']))
        self.config.set('MAIL','SMTP_Port',str(form_list[4].cleaned_data['port']))
        self.config.set('MAIL','Mail_Addr',str(form_list[4].cleaned_data['email']))
        self.config.set('MAIL','Password',str(form_list[4].cleaned_data['password']))
        self.config.set('MAIL','TLS',"True" if (str(form_list[4].cleaned_data['tls'])=="on" or str(form_list[4].cleaned_data['tls'])=="True") else "False")


        with open(BASE+"soc/default.cfg", 'wb',0) as configfile:
            self.config.write(configfile)


        os.chdir(BASE)
        subprocess.check_output("python "+BASE+"manage.py generate_secret_key", shell=True)
        subprocess.check_output("python "+BASE+"manage.py migrate", shell=True)
        os.popen("touch "+BASE+'soc/wsgi.py')

        #Formulaire 5: utilisateur django
        nom=form_list[5].cleaned_data['nom']
        prenom=form_list[5].cleaned_data['prenom']
        email=form_list[5].cleaned_data['email']
        login=form_list[5].cleaned_data['login']
        password=form_list[5].cleaned_data['password']

        tz = pytz.timezone('Europe/Paris')
        d=datetime.datetime.now()
        date_creation=tz.localize(d)

        password=django_password.encrypt(password,rounds=24000)
        cursor= conn.cursor()
        cursor.execute('''INSERT INTO auth_user (first_name,last_name,email,username,password,date_joined,is_superuser,is_staff,is_active) 
                            VALUES(%s,%s,%s,%s,%s,%s,True,True,True)''',[nom,prenom,email,login,password,date_creation])

        conn.commit()
        conn.close()

        password='666'*20
        del password

        self.config.set('PROJET','Initialiser','YES')
        with open(BASE+"soc/default.cfg", 'wb') as configfile:
            self.config.write(configfile)


        #Ajout du script python dans la crontab de www-data
        try:
            subprocess.check_output(['crontab -l | { cat; echo "10 1 * * * '+BASE+'scan_crontab.py; } | crontab -'],shell=True)
        except Exception as e:
            logger.error("Erreur de creation de la crontab: "+str(e))
            pass


        return render(self.request, 'maintenance/success.html')  


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


@login_required
@ajax
def validerInfosRapports(request):
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

    try:
        if ( 'logo' in request.FILES):
            image=request.FILES['logo']
            image_name=image._get_name()
            image_name = desatanize(image_name)
            image_path=BASE+'static/img/'

            image_file=open(image_path+image_name,'wb',0)

            for chunk in image.chunks():
                image_file.write(chunk)

            image_file.close()

            old_image_name= desatanize( str(config.get("Rapports",'Logo') ))
            os.remove(BASE+'static/img/'+str(old_image_name))

            config.set('Rapports','Logo',str(image_name))


        config.set('Rapports','Societe',str(request.POST['societe']))
        config.set('Rapports','Auteur',str(request.POST['auteur']))

        with open(BASE+"soc/default.cfg", 'wb',0) as configfile:
            config.write(configfile)

    except Exception as e:
        return "Erreur de traitement"




@login_required
@ajax
def validerNessus(request):
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

    config.set('Nessus','adresse',str(request.POST['address']))
    config.set('Nessus','port',str(request.POST['port']))
    config.set('Nessus','login',str(request.POST['login']))
    config.set('Nessus','password',str(request.POST['password']))
    config.set('Nessus','directory_id',str(request.POST['directory-id']))
    config.set('Nessus','verify_ssl','True' if ((str(request.POST['verify'])=='on') or (str(request.POST['verify'])=='True')) else 'False')

    with open(BASE+"soc/default.cfg", 'wb',0) as configfile:
        config.write(configfile)


@login_required
@ajax
def validerMail(request):
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

    config.set('MAIL','SMTP_Addr',str(request.POST['address']))
    config.set('MAIL','SMTP_Port',str(request.POST['port']))
    config.set('MAIL','Mail_Addr',str(request.POST['login']))
    config.set('MAIL','Password',str(request.POST['password']))
    config.set('MAIL','TLS','True' if (str(request.POST['tls'])=="on" or str(request.POST['tls'])=='True') else 'False')

    with open(BASE+"soc/default.cfg", 'wb',0) as configfile:
        config.write(configfile)


@login_required
@ajax
def validerVariables(request):
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

    loc=request.POST['localisation']
    env=request.POST['environnement']
    typ=request.POST['type']


    loc=testTuples(loc)
    env=testTuples(env)
    typ=testTuples(typ)

    config.remove_section('LOCALISATION')
    config.add_section('LOCALISATION')

    for localisation in loc.split('\r\n'):
        loc_tuple=localisation.split(';')
        try:
            config.set('LOCALISATION',loc_tuple[0],loc_tuple[1])
        except IndexError:
            pass


    config.remove_section('ENVIRONNEMENT')
    config.add_section('ENVIRONNEMENT')

    for environnement in env.split('\r\n'):
        env_tuple=environnement.split(';')
        try:
            config.set('ENVIRONNEMENT',env_tuple[0],env_tuple[1])
        except IndexError:
            pass

    config.remove_section('TYPE')
    config.add_section('TYPE')


    for type_machine in typ.split('\r\n'):
        machine_tuple=type_machine.split(';')
        try:
            config.set('TYPE',machine_tuple[0],machine_tuple[1])
        except IndexError:
            pass

    with open(BASE+"soc/default.cfg", 'wb') as configfile:
        config.write(configfile)




@login_required
@ensure_csrf_cookie
def editConfig(request):
    forms=[]
    config = ConfigParser.ConfigParser()
    config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))

    #Récuperation des infos Nessus
    nessus_addr=config.get('Nessus','adresse')
    nessus_port=config.get('Nessus','port')
    nessus_login=config.get('Nessus','Login')
    nessus_password=config.get('Nessus','Password')
    nessus_directory_id=config.get('Nessus','Directory_Id')
    nessus_verify='off' if str(config.get('Nessus','Verify_SSL')).lower()=='false' else 'on'

    form1=modifNessus(addr=nessus_addr,port=nessus_port,login=nessus_login,password=nessus_password,directory_id=nessus_directory_id,verify=nessus_verify)
    forms.append(form1)

    #Récupération des infos du mail
    mail_addr=config.get('MAIL','SMTP_Addr')
    mail_port=config.get('MAIL','SMTP_Port')
    mail_login=config.get('MAIL','Mail_Addr')
    mail_password=config.get('MAIL','Password')
    mail_tls=config.get('MAIL','TLS')

    form2=modifMail(addr=mail_addr,port=mail_port,login=mail_login,password=mail_password,tls=mail_tls)
    forms.append(form2)


    #Récupération des différents paramètres de l'application
    loc=""

    for localisation in config.items('LOCALISATION'):
        loc+=str(localisation[0])+';'+str(localisation[1])+'\r\n'

    env=""

    for environnement in config.items('ENVIRONNEMENT'):
        env+=str(environnement[0])+';'+str(environnement[1])+'\r\n'

    typ=""

    for type_machine in config.items('TYPE'):
        typ+=str(type_machine[0])+';'+str(type_machine[1])+'\r\n'


    form3=modifVariables(localisations=loc, environnements=env, types=typ)
    forms.append(form3)

    nom_logo=config.get('Rapports','logo')
    logo=Image.open(BASE+'static/img/'+str(nom_logo))
    societe=config.get('Rapports','societe')
    auteur=config.get('Rapports','auteur')

    form4=modifInfosRapports(logo=logo,societe=societe,auteur=auteur)
    forms.append(form4)

    return render(request,'maintenance/modif_parametres.html',{'forms':forms})


