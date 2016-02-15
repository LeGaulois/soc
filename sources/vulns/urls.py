from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
		#url(r'^$', views.liste_vulns,name='liste_vulns'),
		url(r'^statistiques/$', views.stats_vulns,name='stats_vulns'),
		url(r'^details/(?P<vuln_id>(\d+))/$', views.details,name='details'),
		url(r'^liste/$', views.liste,name='liste'),
]	

urlpatterns += staticfiles_urlpatterns()	
