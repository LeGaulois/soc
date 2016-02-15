#-*- coding: utf-8 -*-

def intro(dictVuln,liste_ip,cheminFichier='./file.tex'):
	

	adresse=liste_ip[0]

	for i in range(1,len(liste_ip)):
		adresse+=', '+str(liste_ip[i])



	fichierLatex=open(cheminFichier,'a')
	fichierLatex.write('''
	\section{But}
	Ce document a pour but de fournir un rapport détaillé, des différentes vulnérabilité affectant les hôtes ciblés .\\\\
	

	\section{Informations}
	\subsection{Vulnerabilitées}
	''')



	fichierLatex.write('''\\begin{tabularx}{15cm}{|X|p{8cm}|}
		    \hline
		     \centering \\textbf{Criticite}& \centering \\textbf{Nombre} 
		     \\tabularnewline \hline     
		     \centering \\textcolor{red}{\\textbf{Critique}}& \centering '''+str(dictVuln['critique'])+'''
		     \\tabularnewline \hline
			\centering \\textcolor{orange}{\\textbf{Haute}}& \centering '''+str(dictVuln['haute'])+'''
		     \\tabularnewline \hline      
		     \centering \\textcolor{yellow}{\\textbf{Moyenne}}& \centering '''+str(dictVuln['moyenne'])+'''
		     \\tabularnewline \hline     
		     \centering \\textcolor{green}{\\textbf{Faible}}& \centering '''+str(dictVuln['faible'])+'''
		     \\tabularnewline \hline
		\end{tabularx}
		\\vspace*{0.5cm}''')

	fichierLatex.write('''\subsection{Hôtes}
	Le rapport a été généré pour le(s) hôte(s) suivant(s): '''+adresse)

	fichierLatex.close()
