#-*- coding: utf-8 -*-

def pageGarde(titre,auteur,entreprise,cheminImage,cheminFichier='./file.tex'):
    fichierLatex=open(cheminFichier,'a')
    temp=titre.split('\n')
    titre=temp[0]

    for i in range(1,len(temp)):
        titre+='\\\[+0mm]'+str(temp[i])

    fichierLatex.write('''
\pagestyle{fancy}
\\renewcommand{\headrulewidth}{1pt}
\\fancyhead[C]{\\textbf{page \\thepage}} 
\\fancyhead[L]{'''+str(auteur)+'''}
\\fancyhead[R]{'''+str(entreprise)+'''}

\\renewcommand{\\footrulewidth}{1pt}
\\fancyfoot[C]{\\textbf{page \\thepage}} 
\\fancyfoot[L]{\\today}
\\fancyfoot[R]{\hyperlink{table_matiere}{Sommaire}}

\\title{\parbox{15cm}{
\\begin{center}
\\includegraphics[width=6cm]{'''+str(cheminImage)+'''}
\end{center}
\\vspace*{1cm}
\\begin{center}\sf\\bfseries\huge
\\rule{15cm}{1pt}
\\medskip
'''
+titre+
'''
\\rule{15cm}{1pt}
\end{center}
}}
\\vfill
\date{\\today}
\\begin{document}

\maketitle

\\newpage
\\renewcommand{\contentsname}{Table des matières}
\hypertarget{table_matiere}
\\tableofcontents
\\newpage''')

    fichierLatex.close()
    
