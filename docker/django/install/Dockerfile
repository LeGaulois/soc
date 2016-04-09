FROM debian:jessie

##### INSTALLATION ######
RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y apache2 libapache2-mod-wsgi python-pip nmap python2.7 libcap2-bin python-psycopg2 python-dnspython python-dns texlive-latex-base texlive-lang-french


###### NMAP ######
RUN chgrp adm /usr/bin/nmap \
&& chmod 750 /usr/bin/nmap \
#&& setcap cap_net_raw,cap_net_admin,cap_net_bind_service+eip /usr/bin/nmap \
&& usermod -a -G adm www-data 


###### DJANGO ######
RUN pip install --upgrade pip \
&& pip install django django-extensions configparser pytz dnspython djangoajax django-formtools passlib


##### CONF APACHE ####
COPY 000-default.conf /etc/apache2/sites-available/
#Certificats
RUN chown -R www-data /var/www/

VOLUME  ["/var/www/html/soc/"]
USER www-data

###### APACHE ######
EXPOSE 80
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid




CMD ["chown", "-R", "www-data:www-data", "/var/www/html/soc/", "&&", "/usr/sbin/apache2", "-D", "FOREGROUND"]

