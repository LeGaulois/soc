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
  - PostgreSQL
  - Nessus
  - Apache configuré en frontal avec mod-wsgi
  
  
# Installation
Le déploiement de l'application se réaliser simplement grâce à l'utilisation de docker et de docker-compose permettant degérer simultanément plusieurs containers.

L'application s'appuie sur 3 containers:
    - django: contenant le frontal apache et le code sources de l'applications
    - postgresql: pour la base de données
    - nessus: pour le scanner de vulnérabilités


Prérequis: votre machine doit posséder les paquets suivants: git, [docker](https://docs.docker.com/engine/installation/), [docker-compose](https://docs.docker.com/compose/install/) 

Téléchargement du dépôt github:
```
git clone https://github.com/LeGaulois/soc.git
```

Construction des images:
```
cd soc/docker
docker-compose build
```

Création et démarrage des contrôleurs:
```
docker-compose up
```

Normalement vous devriez-voir une erreur:
```
django_1     | (13)Permission denied: AH00072: make_sock: could not bind to address [::]:80
django_1     | (13)Permission denied: AH00072: make_sock: could not bind to address 0.0.0.0:80
django_1     | no listening sockets available, shutting down
django_1     | AH00015: Unable to open logs
docker_django_1 exited with code 1
```

Cette erreur est due au fait que apache n'est pas propriétaire de l'arborescence /var/www/html/soc/


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
    1) Nessus: il vous sera notament demandé de vous inscrire sur le site de l'éditeur afin de récupérer une clé de produit (version gratuite)
        [https://votre_adresse_ip:8834](https://votre_adresse_ip:8834)
    2) Le projet en lui même: [http://votre_adresse_ip/](http://votre_adresse_ip/)

Ces 2 initialisations se font simplement à l'aide d'un wizard


  
# Reste à faire:
    - gestion des mails
    - manuel technique

