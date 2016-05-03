# PRESENTATION
Projet de mise en place d'un SOC (Security Operating Center) alléger.
  
Cette interface WEB développé en Python à l'aide du framework DJANGO s'interface avec:
  - Nessus > Scanner de vulnérabilitées
  - Nmap > scanner de port et détéection de versions des services et OS 


Les résultats des scans servent à alimenter la base de données.
  
L'interface permet de:
  - avoir une vision de la vulnérabilitée de chaque appli métier et serveur
  - génerer des rapports de vulnérabilitées pour des machines et/ou applications données
  - déclencher des scans de vulnérabilitées de façon périodique
  
  
# Prérequis:
Votre machine doit posséder les paquets suivants: 
  - git
  - [docker](https://docs.docker.com/engine/installation/)
  - [docker-compose](https://docs.docker.com/compose/install/)
  
  
# Installation
Le déploiement de l'application se réaliser simplement grâce à l'utilisation de docker et de docker-compose permettant degérer simultanément plusieurs containers.

L'application s'appuie sur 3 containers:
  - django: contenant le frontal apache et le code sources de l'applications
  - postgresql: pour la base de données
  - nessus: pour le scanner de vulnérabilités



Téléchargement du dépôt github:
```
git clone https://github.com/LeGaulois/soc.git
```

Création des certificats:
```
cd soc/docker/django/
mkdir certificats
cd certificats

openssl genrsa 4096 > django.key
openssl req -new -key django.key > django.csr

openssl genrsa -des3 4096 > ca.key
openssl req -new -x509 -days 1000 -key ca.key > ca.crt

openssl x509 -req -in django.csr -out django.crt -CA ca.crt -CAkey ca.key -CAcreateserial -CAserial ca.srl
cd ../..
```

Construction des images:
```
docker-compose build
```

Création et démarrage des containers:
```
docker-compose up
```

Lancement des containers:
```
docker-compose start
```

Modification du propriétaire de l'arborescence:
```
docker exec -i -t `docker ps | awk 'BEGIN {OFS="\t"} $NF=="docker_django_1" {print $1}'` chown -R www-data:www-data /var/www/html/soc
```

Redémarrer le container django:
```
docker-compose restart django
```


L'initialisation du projet se fait en 2 étapes:
  - Nessus: il vous sera notament demandé de vous inscrire sur le site de l'éditeur afin de récupérer une clé de produit (version gratuite)
        [https://votre_adresse_ip:8834](https://votre_adresse_ip:8834)
  - Le projet en lui même: [http://votre_adresse_ip/](http://votre_adresse_ip/)

Ces 2 initialisations se font simplement à l'aide d'un wizard


Le wizard vous invitera à redémarrer le service apache pour finaliser l'installation. Redémarrez simplement le container django
```
docker-compose restart django
```  

