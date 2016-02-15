#-*- coding: utf-8 -*-



def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]


def toString(s):
    return '' if s is None else str(s)


				
		

