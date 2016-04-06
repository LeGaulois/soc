from django.conf.urls import url,include
from django.contrib import admin
from . import views
from django.conf.urls import handler400, handler404, handler500


urlpatterns = [
    url(r'^$',include('maintenance.urls',app_name='maintenance',namespace='maintenance')),
    url(r'^admin/', admin.site.urls),
    url(r'^serveurs/', include('serveurs.urls',app_name='serveurs',namespace='serveurs')),
    url(r'^applications/', include('applications.urls',app_name='applications',namespace='applications')),
    url(r'^scans/', include('scans.urls',app_name='scans',namespace='scans')),
    url(r'^rapports/', include('rapports.urls',app_name='rapports',namespace='rapports')),
    url(r'^vulns/', include('vulns.urls',app_name='vulns',namespace='vulns')),
    url(r'^maintenance/', include('maintenance.urls',app_name='maintenance',namespace='maintenance')),
    url(r'^accounts/login/', views.login_view,name='login_view'),
    url(r'^accounts/logout/', views.logout_view,name='logout_view'),
    #url(r'^codage/', views.view_locale,name='view_locale'),
]

handler400='soc.views.erreur400'
handler404='soc.views.erreur404'
handler500='soc.views.erreur500'
