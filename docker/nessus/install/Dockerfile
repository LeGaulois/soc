FROM debian:jessie

##### INSTALLATION ######
RUN apt-get update \
&& apt-get upgrade -y 


###### Nessus ######
COPY nessus.deb /tmp/ 
RUN dpkg -i /tmp/nessus.deb
EXPOSE 8834

CMD ["/opt/nessus/sbin/nessus-service"]
