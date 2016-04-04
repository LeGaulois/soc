#-*- coding: utf-8 -*-

def intro(dictScan,liste_ip,cheminFichier='./file.tex',type_scan='plannifie'):
    
    try:
        adresse=liste_ip[0]['ip_hote']
    except:
        adresse=liste_ip[0]['ip']

    for i in range(1,len(liste_ip)):
        try:
            adresse+=', '+str(liste_ip[i]['ip_hote'])
        except:
            adresse+=', '+str(liste_ip[i]['ip'])



    fichierLatex=open(cheminFichier,'a')
    fichierLatex.write('''
    \section{But}
    Ce document a pour but de fournir un rapport d'évolution, suite aux scans de vulnerabilites, et/ou services.\\\\
    En cas de changement, le(s) tableau(x) de la partie 3 indiqueront la ou les nouvelles vulnérabilitées qui sont apparues, ainsi que celles qui ont été corrigées.

    \section{Informations}
    \subsection{Scan}
    ''')


    if (type_scan=='plannifie'):
        fichierLatex.write('''\\begin{tabularx}{15cm}{|X|p{8cm}|}
            \hline
             \centering \\textbf{Nom}& \centering '''+str(dictScan['nom']).replace('_',' ')+''' 
             \\tabularnewline \hline
             \centering \\textbf{Description}& \centering '''+str(dictScan['description'])+'''
             \\tabularnewline \hline     
             \centering \\textbf{Scan Nmap}& \centering '''+str(dictScan['nmap'])+'''
             \\tabularnewline \hline
            \centering \\textbf{Options Nmap}& \centering '''+str(dictScan['nmap_options'])+'''
             \\tabularnewline \hline      
             \centering \\textbf{Scan Nessus}& \centering '''+str(dictScan['nessus'])+'''
             \\tabularnewline \hline     
             \centering \\textbf{Nessus Policy}& \centering '''+str(dictScan['nessus_policy_id'])+'''
             \\tabularnewline \hline
        \end{tabularx}
        \\vspace*{0.5cm}''')

    else:
            fichierLatex.write('''\\begin{tabularx}{15cm}{|X|p{8cm}|}
            \hline
             \centering \\textbf{Nom}& \centering Scan manuel 
             \\tabularnewline \hline     
             \centering \\textbf{Scan Nmap}& \centering '''+str(dictScan['nmap'])+'''
             \\tabularnewline \hline
            \centering \\textbf{Options Nmap}& \centering '''+str(dictScan['nmap_options'])+'''
             \\tabularnewline \hline      
             \centering \\textbf{Scan Nessus}& \centering '''+str(dictScan['nessus'])+'''
             \\tabularnewline \hline     
             \centering \\textbf{Nessus Policy}& \centering '''+str(dictScan['nessus_policy_id'])+'''
             \\tabularnewline \hline
        \end{tabularx}
        \\vspace*{0.5cm}''')

    fichierLatex.write('''\subsection{Hôtes}
    Le scan a été lancé sur le(s) hôte(s) suivant(s): '''+adresse)

    fichierLatex.close()
