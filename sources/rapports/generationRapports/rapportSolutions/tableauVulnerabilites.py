#-*- coding: utf-8 -*-

def tableauVulnerabilites(dictVuln,group_by,cheminFichier='./file.tex'):
    fichierLatex=open(cheminFichier,'a')
    fichierLatex.write('''
\\section{Vulnerabilites}
\subsection{Liste}
Le tableau ci-dessous dresse une description détaillée des vulnerabilités présentes sur les machines.\\\\''')

    couleur={'Critical':'\\textcolor{red}{\\textbf{Critique}}','High':'\\textcolor{orange}{\\textbf{Haute}}','Medium':'\\textcolor{yellow}{\\textbf{Moyenne}}','Low':'\\textcolor{green}{\\textbf{Faible}}','Info':'\\textcolor{blue}{\\textbf{Info}}'}

    if group_by=='vuln':
        fichierLatex.write('''
        \\tablefirsthead{\hline \centering \\textbf{Crit}& \\centering \\textbf{Nom} & \centering \\textbf{Description} & \centering \\textbf{Liste IP} 
        \\tabularnewline \hline}
        \\tabletail{%
        \hline
        \multicolumn{4}{|r|}{\small\sl continued on next page}\\\\
        \hline}
        \\tablelasttail{\hline}
        \\begin{landscape}
        \\begin{supertabular}{|p{2.5cm}|p{2.0cm}|p{14cm}|p{2.5cm}|} ''')


        for elem in dictVuln:
            fichierLatex.write('\centering '+couleur[str(elem['criticite'])]+' & \centering '+str(elem['nom']).replace('_',' ').replace('&','\&')+' & \centering '+str(elem['description']).replace('_',' ').replace('&','\&')+' & \centering ')


            if len(elem['ip_hote'])>1:
                for ip in elem['ip_hote']:
                    fichierLatex.write(str(ip))

                    if ip!=elem['ip_hote'][-1]:
                        fichierLatex.write('\\\\')

            else:
                fichierLatex.write(elem['ip_hote'][0])


            fichierLatex.write(' \\tabularnewline \hline ')     

    else:


        fichierLatex.write('''
        \\tablefirsthead{\hline \centering \\textbf{IP}& \\centering \\textbf{Crit} & \centering \\textbf{Nom Vuln}& \centering \\textbf{Description} 
        \\tabularnewline \hline}
        \\tabletail{%
        \hline
        \multicolumn{4}{|r|}{\small\sl continued on next page}\\\\
        \hline}
        \\tablelasttail{\hline}
        \\begin{landscape}
        \\begin{supertabular}{|p{2.5cm}|p{2.0cm}|p{3cm}|p{14cm}|} ''')


        for elem in dictVuln:
            fichierLatex.write('\centering '+elem['ip_hote']+' & \centering '+couleur[str(elem['criticite'])]+' & \centering '+str(elem['nom']).replace('_',' ').replace('&','\&')+' & \centering '+elem['description']+' \\tabularnewline \hline  ')
    


    fichierLatex.write('''
    \end{supertabular}
    \\end{landscape}''')


    fichierLatex.close()
