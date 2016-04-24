#-*- coding: utf-8 -*-
from functools import wraps
import ConfigParser
import codecs
from django.conf import settings
from django.http import HttpResponseRedirect


BASE=settings.BASE_DIR+'/'


def projet_initialiser(view_func):
    '''
    Ce décorateur permet de contrôler l'accès à la page d'initialisation du projet
    On n'autorise l'accès aux anonymes que si le projet n'est pas encore initialiser
    '''
    def _decorator(request, *args, **kwargs):
        config = ConfigParser.ConfigParser()
        config.readfp(codecs.open(BASE+"soc/default.cfg","r","utf-8"))
        initialiser=config.get('PROJET','Initialiser')

        if request.user.is_authenticated():
            return view_func(request, *args, **kwargs)

        elif initialiser=='NO':
            return view_func(request, *args, **kwargs)

        else:
            return HttpResponseRedirect('/')

    return wraps(view_func)(_decorator)

