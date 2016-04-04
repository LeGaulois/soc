#-*- coding: utf-8 -*-

def tableauSolutions(dictVuln,group_by,cheminFichier='./file.tex'):
    fichierLatex=open(cheminFichier,'a')
    fichierLatex.write('''
\\subsection{Solutions}
Le tableau ci-dessous dresse une description détaillée des actions correctrices à effectuer.\\\\''')

    couleur={'Critical':'\\textcolor{red}{\\textbf{Critique}}','High':'\\textcolor{orange}{\\textbf{Haute}}','Medium':'\\textcolor{yellow}{\\textbf{Moyenne}}','Low':'\\textcolor{green}{\\textbf{Faible}}'}

    if group_by=='vuln':
        fichierLatex.write('''Pour chaque vulnérabilité presente, le tableau indique les hôtes affectés, son nom, sa description, une indiquation pour tenter de la résoudre, ainsi que des informations complémentaires (ex: lien vers la page de l'éditeur traitant de cette faille).\\\\
A noter que le tableau tient compte uniquement des adresses entrées en paramètres et non la totalité de la base.\\\\
\\bigskip ''')

        fichierLatex.write('''
        \\tablefirsthead{\hline \centering \\textbf{Crit}& \\centering \\textbf{Nom} & \centering \\textbf{Solution}& \centering \\textbf{Infos complementaires} & \centering \\textbf{Liste IP} 
        \\tabularnewline \hline}
        \\tabletail{%
        \hline
        \multicolumn{4}{|r|}{\small\sl continued on next page}\\\\
        \hline}
        \\tablelasttail{\hline}
        \\begin{landscape}
        \\begin{supertabular}{|p{1.5cm}|p{3cm}|p{8cm}|p{6cm}|p{3cm}|} ''')


        for elem in dictVuln:
            fichierLatex.write('\centering '+couleur[str(elem['criticite'])]+' & \centering '+str(elem['nom']).replace('_',' ').replace('&','\&')+' & \centering '+elem['solution']+' & \centering ')

            for lien in elem['infos_complementaires'].split('\n'):
                if lien==None or lien =='':
                    continue

                fichierLatex.write('\\href{'+str(lien)+'}{\\nolinkurl{'+str(lien).replace('_','\_').replace('&','\&')+'}}\\\\')


            fichierLatex.write('& \centering')

            if len(elem['ip_hote'])>1:
                for ip in elem['ip_hote']:
                    fichierLatex.write(str(ip))

                    if ip!=elem['ip_hote'][-1]:
                        fichierLatex.write('\\\\')

            else:
                fichierLatex.write(elem['ip_hote'][0])


            fichierLatex.write(' \\tabularnewline \hline ')     

    else:
        fichierLatex.write('''Pour chaque hote present, le tableau indique les vulnérabilitées auquelles il est soumis. Pour chaque vulnérabilitée le tableau indique: son nom, sa description, une indiquation pour tenter de la résoudre, ainsi que des informations complémentaires (ex: lien vers la page de l'éditeur traitant de cette faille).\\\\
A noter que le tableau tient compte uniquement des adresses entrées en paramètres et non la totalité de la base.\\\\
\\bigskip ''')


        fichierLatex.write('''
        \\tablefirsthead{\hline \centering \\textbf{IP}& \\centering \\textbf{Crit} & \centering \\textbf{Nom}& \centering \\textbf{Solution} & \centering \\textbf{Infos complementaires} 
        \\tabularnewline \hline}
        \\tabletail{%
        \hline
        \multicolumn{4}{|r|}{\small\sl continued on next page}\\\\
        \hline}
        \\tablelasttail{\hline}
        \\begin{landscape}
        \\begin{supertabular}{|p{2.0cm}|p{1.5cm}|p{3cm}|p{8cm}|p{7.5cm}|} ''')


        for elem in dictVuln:
            fichierLatex.write('\centering '+elem['ip_hote']+' & \centering '+couleur[str(elem['criticite'])]+' & \centering '+str(elem['nom']).replace('_',' ').replace('&','\&')+' & \centering '+elem['solution']+' & \centering ')

            for lien in elem['infos_complementaires'].split('\n'):
                if lien==None or lien =='':
                    continue

                fichierLatex.write(' \\href{'+str(lien)+'}{\\nolinkurl{'+str(lien).replace('_','\_').replace('&','\&')+'}}\\\\')

            fichierLatex.write(' \\tabularnewline \hline ')     


    fichierLatex.write('''
    \end{supertabular}
    \\end{landscape}''')


    fichierLatex.close()
