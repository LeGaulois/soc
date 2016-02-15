#-*- coding: utf-8 -*-



def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]



def prepareListeSolution(liste_solution):

	for solution in liste_solution:
		liste_liens=solution['infos_complementaires'].split('\n')

		if len(liste_liens)>0 and liste_liens[0]!='' and liste_liens[0]!=None:
			solution['infos_complementaires']=[]
			for lien in liste_liens:
				solution['infos_complementaires'].append(lien)


	return liste_solution
