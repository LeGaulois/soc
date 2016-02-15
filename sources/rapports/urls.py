from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
	url(r'telecharger-rapport/(?P<id_scan>\d+)/(?P<type_scan>\w+)/(?P<type_rapport>\w+)/$', views.getRapport,name='getRapport'),
	url(r'get-pdf/$',views.getPDF,name='getPDF'),
]	

urlpatterns += staticfiles_urlpatterns()
