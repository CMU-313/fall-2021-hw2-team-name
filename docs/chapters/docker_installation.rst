*******************
Docker installation
*******************

Docker is a system that allows running programs in isolated areas which
have restricted access to resources, devices, and memory. Docker usage also
distributing software as a single file.

Make sure Docker is properly installed and working before attempting to install
Mayan EDMS.

Docker can be installed using their automated script::

    wget -qO- https://get.docker.com/ | sh

This installs the latest versions of Docker. If you don't want run an automated
script follow the instructions outlined in their documentation:
https://docs.docker.com/install/

With Docker properly installed, proceed to download the Mayan EDMS image using the command::

    docker pull mayanedms/mayanedms:<version>

Then download version 9.5 of the Docker PostgreSQL image::

    docker pull postgres:9.5

Create and run a PostgreSQL container::

    docker run -d \
    --name mayan-edms-postgres \
    --restart=always \
    -p 5432:5432 \
    -e POSTGRES_USER=mayan \
    -e POSTGRES_DB=mayan \
    -e POSTGRES_PASSWORD=mayanuserpass \
    -v /docker-volumes/mayan-edms/postgres:/var/lib/postgresql/data \
    -d postgres:9.5

The PostgreSQL container will have one database named ``mayan``, with an user
named ``mayan`` too, with a password of ``mayanuserpass``. The container will
expose its internal 5432 port (PostgreSQL's default port) via the host's
5432 port. The data of this container will reside on the host's
``/docker-volumes/mayan-edms/postgres`` folder.

Finally create and run a Mayan EDMS container. Change <version> with the
latest version in numeric form (example: 2.7.3) or use the ``latest``
identifier::

    docker run -d \
    --name mayan-edms \
    --restart=always \
    -p 80:8000 \
    -e MAYAN_DATABASES='{default: {ENGINE: django.db.backends.postgresql, HOST: 172.17.0.1, NAME: mayan, PASSWORD: mayanuserpass, USER: mayan, CONN_MAX_AGE: 60}}' \
    -v /docker-volumes/mayan-edms/media:/var/lib/mayan \
    mayanedms/mayanedms:<version>

The Mayan EDMS container will connect to the PostgreSQL container via the
``172.17.0.1`` IP address (the Docker host's default IP address). It will
connect using the ``django.db.backends.postgresql`` database driver and
connect to the ``mayan`` database using the ``mayan`` user with the password
``mayanuserpass``. The container will keep connections to the database
for up to 60 seconds in an attempt to reuse them increasing response time
and reducing memory usage. The files of the container will be store in the
host's ``/docker-volumes/mayan-edms/media`` folder. The container will
expose its web service running on port 8000 on the host's port 80.

The container will be available by browsing to ``http://localhost`` or to
the IP address of the computer running the container.

If another web server is running on port 80 use a different port in the
``-p`` option. For example: ``-p 81:8000``.


Using a dedicated Docker network
================================
Use this method to avoid having to expose PostreSQL port to the host's network
or if you have other PostgreSQL instances but still want to use the default
port of 5432 for this installation.

Create the network::

    docker network create mayan

Launch the PostgreSQL container with the network option and remove the port
binding (``-p 5432:5432``)::

    docker run -d \
    --name mayan-edms-postgres \
    --network=mayan \
    --restart=always \
    -e POSTGRES_USER=mayan \
    -e POSTGRES_DB=mayan \
    -e POSTGRES_PASSWORD=mayanuserpass \
    -v /docker-volumes/mayan-edms/postgres:/var/lib/postgresql/data \
    -d postgres:9.5

Launch the Mayan EDMS container with the network option and change the
database hostname to the PostgreSQL container name (``mayan-edms-postgres``)
instead of the IP address of the Docker host (``172.17.0.1``)::

    docker run -d \
    --name mayan-edms \
    --network=mayan \
    --restart=always \
    -p 80:8000 \
    -e MAYAN_DATABASES='{default: {ENGINE: django.db.backends.postgresql, HOST: mayan-edms-postgres, NAME: mayan, PASSWORD: mayanuserpass, USER: mayan, CONN_MAX_AGE: 60}}' \
    -v /docker-volumes/mayan-edms/media:/var/lib/mayan \
    mayanedms/mayanedms:<version>
