#-*- coding: utf-8 -*-
from fonctions import toString

def tableauServices(dictServices,cheminFichier='./file.tex'):
    '''
    Cette fonction créer un tableau regroupant les différents services 
    '''

    fichierLatex=open(cheminFichier,'a')
    fichierLatex.write('''
\\subsection{Nmap}
Le tableau ci-dessous dresse un résumé du résultat du scan Nmap.\\
Les résultats du scan sont comparés avec les informations présentes en base. Le delta nous permet donc d'obtenir les évolutions pour chaque hote.
\\\Le second tableau dresse un portrait détaillé pour chaque hôte avec: le nom du service, sa version, le port et protocole utilisé.
\\bigskip ''')


    dictResume={}
    for elem in dictServices:
        if dictResume.has_key(elem['ip_hote'])==False:
            dictResume[elem['ip_hote']]={'entree':0,'sortie':0}

        if elem['date_retrait']=='' or elem['date_retrait']==None:
            dictResume[elem['ip_hote']]['entree']+=1

        else:
            dictResume[elem['ip_hote']]['sortie']+=1



    if len(dictServices)==0:
        fichierLatex.write('''\\vspace*{0.5cm} \\\\ \\textcolor{red}{Aucune évolution constatée}''')

    else:
        fichierLatex.write('''
    \\tablefirsthead{\hline \centering \\textbf{IP}& \centering \\textbf{\\textcolor{red}{Nouveaux Services}}& \centering \\textbf{\\textcolor{green}{Services arrêtés}}
    \\tabularnewline \hline}

    \\tabletail{%
    \hline
    \multicolumn{3}{|r|}{\small\sl continued on next page}\\\\
    \hline}
    \\tablelasttail{\hline}
    \\begin{supertabular}{|p{5cm}|p{4cm}|p{4cm}|} ''')


        
        for hote in dictResume.keys():
            fichierLatex.write('\centering '+toString(hote)+' & \centering '+toString(dictResume[hote]['entree'])+' & \centering '+toString(dictResume[hote]['sortie'])+''' 
    \\tabularnewline \hline ''') 

        fichierLatex.write('''
    \end{supertabular}
    \\vspace*{0.5cm}
    \\\\''')



        fichierLatex.write('''
    \\tablefirsthead{\hline \centering \\textbf{IP}& \centering \\textbf{Type}& \centering \\textbf{Proto}& \centering \\textbf{Port}& \\centering \\textbf{Nom} & \\centering \\textbf{Version} 
    \\tabularnewline \hline}
    \\tabletail{%
    \hline
    \multicolumn{4}{|r|}{\small\sl continued on next page}\\\\
    \hline}
    \\tablelasttail{\hline}
    \\begin{supertabular}{|p{2.5cm}|p{1.5cm}|p{1.0cm}|p{1.5cm}|p{3cm}|p{4.0cm}|} ''')


        for elem in dictServices:
            if elem['date_retrait']=='' or elem['date_retrait']==None:
                type_service='\\textcolor{green}{NEW}'

            else:
                type_service='\\textcolor{red}{OUT}'

            fichierLatex.write('\centering '+toString(elem['ip_hote'])+' & \centering '+toString(type_service)+' & \centering '+toString(elem['protocole']).replace('_',' ').replace('&','\&')+' & \centering '+toString(elem['port']).replace('_',' ').replace('&','\&')+' & \centering '+toString(elem['nom'])+' & \centering '+toString(elem['version'])+'''\\tabularnewline \hline ''')     


        fichierLatex.write('''
    \end{supertabular}''')


    fichierLatex.close()
