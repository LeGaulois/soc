#-*- coding: utf-8 -*-
import requests
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.trouve=False
        self.encours=False
        self.reponse={}
        self.correspondance={
            'CVSS Score':'cvss_score',
            'Confidentiality Impact':'confidentialite',
            'Integrity Impact':'integrite',
            'Availability Impact':'disponibilite',
            'Access Complexity':'complexite',
            'Authentication':'authentification',
            'Vulnerability Type(s)':'type',
            'CWE ID':None,
            'Gained Access':'acces_obtention'
        }

        self.reponse={
            'cvss_score':None,
            'confidentialite':None,
            'integrite':None,
            'disponibilite':None,
            'complexite':None,
            'authentification':None,
            'type':None,
            'acces_obtention':None
        }

        self.precedent=None

    def handle_starttag(self, tag, attrs):
        if tag=='table' and self.trouve==False:
            try:
                if attrs[0][1]=='cvssscorestable' and attrs[1][1]=='details':
                    self.trouve=True
                    self.encours=True
            except:
                pass

    def handle_endtag(self, tag):
        if self.encours==True and tag=='table':
            self.encours=False

    def handle_data(self, data):
        if self.trouve==True and self.encours==True:
            data=data.replace('\t','').replace("\n",'')
            if data!='' and data!=' ':
                trouve=False

                for elem in self.correspondance.keys():
                    if elem==data:
                        self.precedent=self.correspondance[elem]
                        trouve=True
                        break
                try:
                    if trouve==False and self.reponse[self.precedent]==None:
                        self.reponse[self.precedent]=data
                except:
                    pass

    def getReponse(self):
        return self.reponse
                

def requete(cve):
    r = requests.get("http://www.cvedetails.com/cve-details.php?t=1&cve_id="+str(cve))

    if r.status_code != 200:
        raise Exception('Erreur lors de la requête')
    else:
        return r.content



def get_CVE_details(cve):
    html=requete(cve)
    parser = MyHTMLParser()
    parser.feed(html)
    param=parser.getReponse()
    parser.close()
    del parser
    del html

    return param

