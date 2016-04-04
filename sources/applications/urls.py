from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'liste/$', views.liste,name='liste'),
    url(r'ajout/$', views.ajout,name='ajout'),
    url(r'edit/(?P<id_application>\d+)/$', views.edit,name='edit'),
    url(r'suppression/(?P<id_application>\d+)/$', views.suppression,name='suppression'),
    url(r'identite/(?P<id_application>\d+)/$', views.identite,name='identite'),
]

urlpatterns += staticfiles_urlpatterns()    
