"""soc URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Add an import:  from blog import urls as blog_urls
    2. Import the include() function: from django.conf.urls import url, include
    3. Add a URL to urlpatterns:  url(r'^blog/', include(blog_urls))
"""
from django.conf.urls import url,include
from django.contrib import admin
from . import views
from django.conf.urls import handler400, handler404, handler500


urlpatterns = [
    url(r'^$',views.login_view,name='login_view'),
    url(r'^admin/', admin.site.urls),
    url(r'^serveurs/', include('serveurs.urls',app_name='serveurs',namespace='serveurs')),
    url(r'^applications/', include('applications.urls',app_name='applications',namespace='applications')),
    url(r'^scans/', include('scans.urls',app_name='scans',namespace='scans')),
    url(r'^rapports/', include('rapports.urls',app_name='rapports',namespace='rapports')),
    url(r'^vulns/', include('vulns.urls',app_name='vulns',namespace='vulns')),
    url(r'^accounts/login/', views.login_view,name='login_view'),
    url(r'^accounts/logout/', views.logout_view,name='logout_view'),
    url(r'^codage/', views.view_locale,name='view_locale'),
]

handler400='soc.views.erreur400'
handler404='soc.views.erreur404'
handler500='soc.views.erreur500'
