from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from . import views

urlpatterns = [
    url(r'getStatusScans/$', views.getStatusScans,name='getStatusScans'),
    url(r'status-scans/$', views.status_scans,name='status_scans'),
    url(r'status-scans-plannifies/$', views.status_scans_plannifies,name='status_scans_plannifies'),
    url(r'ajout-plannifie/$', views.ajoutScanPlannifie,name='ajoutScanPlannifie'),
    url(r'^ajout-manuel/$', views.ajoutScanManuel,name='ajoutScanManuel'),
    url(r'^ajout-manuel/(?P<ip>([0-9]{1,3}\.){3}([0-9]{1,3}))/$', views.ajoutScanManuel,name='ajoutScanManuel'),
    url(r'liste-scans-plannifies/$', views.liste_scans_plannifies,name='liste_scans_plannifies'),
    url(r'suppression/(?P<id>\d+)/$', views.suppression,name='suppression'),
    url(r'edit-plannifie/(?P<id_scan_plannifie>\d+)/$', views.editScanPlannifie,name='editScanPlannifie'),
    url(r'demarrer-scan-plannifie/(?P<id_scan>\d+)/$', views.demarrerScanPlannifie,name='demarrerScanPlannifie'),
    url(r'parametres-scan-/(?P<id_scan>\d+)/$', views.parametresScan,name='parametresScan'),
    url(r'historique-scan-plannifie/(?P<id_scan_plannifie>\d+)/$', views.historiqueScanPlannifie,name='historiqueScanPlannifie'),
    url(r'historique-scans-manuels/$', views.historiqueScansManuels,name='historiqueScansManuels'),
    url(r'supprimerEntreeHistorique/(?P<id_scan>\d+)/$', views.supprimerEntreeHistorique,name='supprimerEntreeHistorique'),
]    

urlpatterns += staticfiles_urlpatterns()    
