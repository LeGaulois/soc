from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from views import *
from formulaires import *
from decorateurs import projet_initialiser

urlpatterns = [
    url(r'^$', projet_initialiser(InitWizard.as_view([postgreSQL, Nessus,Variables,rapport,email,utilisateurs]))),
    url(r'^initialisation/$', projet_initialiser(InitWizard.as_view([postgreSQL, Nessus,Variables,rapport,email,utilisateurs]))),
    url(r'testConnectionSQL/$',connectionSQL,name='connectionSQL'),
    url(r'testConnectionNessus/$',connectionNessus,name='connectionNessus'),
    url(r'validerNessus/$',validerNessus,name='validerNessus'),
    url(r'validerMail/$',validerMail,name='validerMail'),
    url(r'validerVariables/$',validerVariables,name='validerVariables'),
    url(r'export/$',export,name='export'),
    url(r'import/$',importConfig,name='import'),
]	


urlpatterns += staticfiles_urlpatterns()
