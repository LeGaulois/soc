from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'^$', views.liste,name='liste'),
    url(r'^liste/$', views.liste,name='liste'),
    url(r'^identite/(?P<ip>([0-9]{1,3}\.){3}([0-9]{1,3}))/$', views.identite,name='identite'),
    url(r'^edit/(?P<ip>([0-9]{1,3}\.){3}([0-9]{1,3}))/$', views.edit,name='edit'),
    url(r'^suppression/(?P<ip>([0-9]{1,3}\.){3}([0-9]{1,3}))/$', views.suppression,name='suppression'),
    url(r'ajout/$', views.ajout,name='ajout'),
    url(r'import/$', views.importXML,name='import'),
]

urlpatterns += staticfiles_urlpatterns()    
