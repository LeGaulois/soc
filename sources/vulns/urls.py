from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
        url(r'^statistiques/$', views.stats_vulns,name='stats_vulns'),
        url(r'^details/(?P<vuln_id>(\d+))/$', views.details,name='details'),
        url(r'^details-cve/(?P<cve>(\w+))/$', views.details_cve,name='details_cve'),
        url(r'^liste-cve-famille/(?P<type_cve>(\w+))/$', views.liste_cve_famille,name='liste_cve_famille'),
        url(r'^liste/$', views.liste,name='liste'),
]    

urlpatterns += staticfiles_urlpatterns()    
