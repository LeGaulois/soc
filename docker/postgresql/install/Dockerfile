FROM debian:jessie

##### INSTALLATION ######
RUN apt-get update \
&& apt-get upgrade -y \
&& apt-get install -y postgresql-9.4


###### PSQL ######
COPY django.pg /tmp/
USER postgres
RUN /etc/init.d/postgresql start \
&& psql --command "CREATE USER django_db WITH PASSWORD 'DjangoDBPassWordSOC';" \
&& psql --command "CREATE DATABASE django OWNER django_db;" \
&& psql django < /tmp/django.pg \
&& for table in `psql -tc "select tablename from pg_tables where schemaname = 'public';" django` ; do  psql -c "alter table $table owner to django_db" django ; done \
&& echo "host all  all    0.0.0.0/0  md5" >> /etc/postgresql/9.4/main/pg_hba.conf \
&& echo "listen_addresses='*'" >> /etc/postgresql/9.4/main/postgresql.conf

VOLUME  ["/var/docker/postgresql/data:/etc/postgresql", "/var/docker/postgresql/data:/var/log/postgresql", "/var/docker/postgresql/data:/var/lib/postgresql"]


EXPOSE 5432

CMD ["/usr/lib/postgresql/9.4/bin/postgres", "-D", "/var/lib/postgresql/9.4/main", "-c", "config_file=/etc/postgresql/9.4/main/postgresql.conf"]
