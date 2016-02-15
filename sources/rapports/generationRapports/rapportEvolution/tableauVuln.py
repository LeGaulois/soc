#-*- coding: utf-8 -*-

def tableauVuln(dictVuln,cheminFichier='./file.tex'):
	fichierLatex=open(cheminFichier,'a')
	fichierLatex.write('''
\\subsection{Nessus}
Le tableau ci-dessous dresse un résumé du résultat du scan Nessus.\\
Les résultats du scan sont comparés avec les informations présentes en base. Le delta nous permet donc d'obtenir les évolutions pour chaque hote.
\\\Le second tableau dresse un portrait détaillé pour chaque hôte avec: le nom de la vulnérabilité, sa description, ainsi que sa vulnérabilitée.\\\\
\\bigskip ''')

	couleur={'Critical':'\\textcolor{red}{\\textbf{Critique}}','High':'\\textcolor{orange}{\\textbf{Haute}}','Medium':'\\textcolor{yellow}{\\textbf{Moyenne}}','Low':'\\textcolor{green}{\\textbf{Faible}}','Info':'\\textcolor{blue}{\\textbf{Info}}'}

	dictResume={}
	for elem in dictVuln:
		if dictResume.has_key(elem['ip_hote'])==False:
			dictResume[elem['ip_hote']]={'entree':0,'sortie':0}

		if elem['date_correction']=='' or elem['date_correction']==None:
			dictResume[elem['ip_hote']]['entree']+=1

		else:
			dictResume[elem['ip_hote']]['sortie']+=1


	if len(dictResume)==0:
		fichierLatex.write('''\\vspace*{0.5cm} \\\\ \\textcolor{red}{Aucune évolution constatée}''')

	else:
		fichierLatex.write('''
	\\tablefirsthead{\hline \centering \\textbf{IP}& \centering \\textbf{\\textcolor{red}{Nouvelles vulnerabilitees}}& \centering \\textbf{\\textcolor{green}{Vulnerabilitees corrigees}}
	\\tabularnewline \hline}

	\\tabletail{%
	\hline
	\multicolumn{3}{|r|}{\small\sl continued on next page}\\\\
	\hline}
	\\tablelasttail{\hline}
	\\begin{supertabular}{|p{5cm}|p{4cm}|p{4cm}|} ''')



		for hote in dictResume.keys():
			fichierLatex.write('\centering '+str(hote)+' & \centering '+str(dictResume[hote]['entree'])+' & \centering '+str(dictResume[hote]['sortie'])+''' 
	\\tabularnewline \hline ''') 

		fichierLatex.write('''
	\end{supertabular}
	\\vspace*{0.5cm}''')



		fichierLatex.write('''
	\\tablefirsthead{\hline \centering \\textbf{IP}& \centering \\textbf{Type}& \centering \\textbf{Nom Vuln}& \centering \\textbf{Description}& \\centering \\textbf{Criticite} 
	\\tabularnewline \hline}
	\\tabletail{%
	\hline
	\multicolumn{4}{|r|}{\small\sl continued on next page}\\\\
	\hline}
	\\tablelasttail{\hline}
	\\begin{landscape}
	\\begin{supertabular}{|p{2.5cm}|p{1cm}|p{3cm}|p{11cm}|p{2cm}|} ''')


		for elem in dictVuln:
			if elem['date_correction']=='' or elem['date_correction']==None:
				type_vuln='\\textcolor{red}{NEW}'

			else:
				type_vuln='\\textcolor{green}{CORRIGE}'

			fichierLatex.write('\centering '+elem['ip_hote']+' & \centering '+type_vuln+' & \centering '+str(elem['nom']).replace('_',' ').replace('&','\&')+' & \centering '+str(elem['description']).replace('_',' ').replace('&','\&')+' & \centering '+couleur[str(elem['criticite'])]+'''\\tabularnewline \hline ''')     


		fichierLatex.write('''
	\end{supertabular}
	\\end{landscape}''')


	fichierLatex.close()
