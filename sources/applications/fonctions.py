#-*- coding: utf-8 -*-
import re
import csv 
from django.db import connection
from math import floor




def dictfetchall(cursor):
    "Retourne le resultat d'une requête SQL dans un tableau de dictionnaire"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


