#-*- coding: utf-8 -*-
from django.http import HttpResponse
from django.shortcuts import render,redirect
from django.contrib.auth import authenticate, login,logout
from formulaires import *
import locale
import sys
 

def erreur400(request):
	return render(request, 'soc/400.html')

def erreur404(request):
	return render(request, 'soc/404.html')

def erreur500(request):
	return render(request, 'soc/500.html')



def login_view(request):
	if request.method == 'POST':
		form = formulaire_authentification(request.POST)
        	
		if form.is_valid():
			username=form.cleaned_data['username']
			password=form.cleaned_data['password']

			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					login(request,user)
					return redirect('serveurs:liste')

				else:
					return render('soc/login.html',locals())

			else:
				return render(request, 'soc/login.html',locals())

		else:
			return render(request, 'soc/login.html',locals())

	else:
		if request.user.is_authenticated():
			return redirect('serveurs:liste')
		else:
			form = formulaire_authentification()
			return render(request, 'soc/login.html',locals())



def logout_view(request):
	logout(request)
	return redirect('serveurs:liste')


def view_locale(request):
	'''
	Cette vue permet de tester que framework soit bien 
	en UTF8
	'''
	loc_info = "getlocale: " + str(locale.getlocale()) + \
        "<br/>getdefaultlocale(): " + str(locale.getdefaultlocale()) + \
        "<br/>fs_encoding: " + str(sys.getfilesystemencoding()) + \
        "<br/>sys default encoding: " + str(sys.getdefaultencoding())
        "<br/>sys default encoding: " + str(sys.getdefaultencoding())
	return HttpResponse(loc_info)
