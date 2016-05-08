FROM debian:jessie

##### INSTALLATION ######
RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y apache2 libapache2-mod-wsgi python-pip nmap python2.7 python3 libcap2-bin python-psycopg2 python-dnspython python-dns texlive-latex-base texlive-lang-french texlive-latex-recommended texlive-pictures texlive-latex-extra python-dev libjpeg-dev libpng3 libfreetype6-dev postgresql-client-9.4 



###### NMAP ######
RUN chgrp adm /usr/bin/nmap \
&& chmod 750 /usr/bin/nmap \
&& usermod -a -G adm www-data \
&& chmod 6750 /usr/bin/nmap 


###### DJANGO ######
RUN pip install --upgrade pip \
&& pip install django django-extensions configparser pytz dnspython djangoajax django-formtools passlib Pillow \
&& a2enmod proxy \
&& a2enmod proxy_http \
&& a2enmod ssl \
&& a2enmod rewrite


##### CONF APACHE ####
COPY django.crt /etc/ssl/certs/
COPY django.key /etc/ssl/private/
COPY 000-default.conf /etc/apache2/sites-available/
VOLUME  ["/var/www/html/soc/"]

###### APACHE ######
EXPOSE 443
ENV APACHE_RUN_USER www-data
ENV APACHE_RUN_GROUP www-data
ENV APACHE_LOG_DIR /var/log/apache2
ENV APACHE_LOCK_DIR /var/lock/apache2
ENV APACHE_RUN_DIR /var/run/apache2
ENV APACHE_PID_FILE /var/run/apache2.pid




CMD ["/usr/sbin/apache2", "-D", "FOREGROUND"]

