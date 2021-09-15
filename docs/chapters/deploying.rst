******************
Direct deployments
******************

Mayan EDMS should be deployed like any other Django_ project and
preferably using virtualenv_. Below are some ways to deploy and use Mayan EDMS.
Do not use more than one method.

Being a Django_ and a Python_ project, familiarity with these technologies is
recommended to better understand why Mayan EDMS does some of the things it
does.


Basic deployment
================
This setup uses less memory and CPU resources at the expense of some speed.

Binary dependencies
-------------------

If using a Debian_ or Ubuntu_ based Linux distribution, get the executable
requirements using::

    sudo apt-get install exiftool g++ gcc ghostscript gnupg1 graphviz \
    libfuse2 libjpeg-dev libmagic1 libpq-dev libpng-dev libreoffice \
    libtiff-dev poppler-utils postgresql python-dev python-virtualenv \
    redis-server sane-utils supervisor tesseract-ocr zlib1g-dev -y

Create an user account for the installation:
--------------------------------------------
::

    sudo adduser mayan --disabled-password --disabled-login --no-create-home --gecos ""

Create the parent directory where the project will be deployed:
---------------------------------------------------------------
::

    sudo mkdir /opt

Create the Python virtual environment for the installation:
-----------------------------------------------------------
::

    sudo virtualenv /opt/mayan-edms

Make the mayan user the owner of the installation directory:
------------------------------------------------------------
::

    sudo chown mayan:mayan /opt/mayan-edms -R

Install Mayan EDMS from PyPI:
-----------------------------
::

    sudo -u mayan /opt/mayan-edms/bin/pip install --no-cache-dir mayan-edms

Install the Python client for PostgreSQL and Redis:
---------------------------------------------------
::

    sudo -u mayan /opt/mayan-edms/bin/pip install --no-cache-dir psycopg2==2.7.3.2 redis==2.10.6

Create the database for the installation:
-----------------------------------------
::

    sudo -u postgres psql -c "CREATE USER mayan WITH password 'mayanuserpass';"
    sudo -u postgres createdb -O mayan mayan

Initialize the project:
-----------------------
::

    sudo -u mayan MAYAN_DATABASES='{default: {ENGINE: django.db.backends.postgresql, NAME: mayan, PASSWORD: mayanuserpass, USER: mayan, HOST=127.0.0.1}}' \
    MAYAN_MEDIA_ROOT=/opt/mayan-edms/media \
    /opt/mayan-edms/bin/mayan-edms.py initialsetup

Collect the static files:
-------------------------
::

    sudo -u mayan MAYAN_MEDIA_ROOT=/opt/mayan-edms/media \
    /opt/mayan-edms/bin/mayan-edms.py preparestatic --noinput

Create the supervisor file at ``/etc/supervisor/conf.d/mayan.conf``:
--------------------------------------------------------------------
::

    [supervisord]
    environment=
        MAYAN_ALLOWED_HOSTS='["*"]',  # Allow access to other network hosts other than localhost
        MAYAN_CELERY_BROKER_URL="redis://127.0.0.1:6379/0",
        MAYAN_CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/0",
        PYTHONPATH=/opt/mayan-edms/lib/python2.7/site-packages:/opt/mayan-edms/data,
        MAYAN_MEDIA_ROOT=/opt/mayan-edms/media,
        MAYAN_DATABASES='{default: {ENGINE: django.db.backends.postgresql, HOST: 127.0.0.1, NAME: mayan, PASSWORD: mayanuserpass, USER: mayan, CONN_MAX_AGE: 60}}',
        DJANGO_SETTINGS_MODULE=mayan.settings.production

    [program:mayan-gunicorn]
    autorestart = true
    autostart = true
    command = /opt/mayan-edms/bin/gunicorn -w 2 mayan.wsgi --max-requests 500 --max-requests-jitter 50 --worker-class gevent --bind 0.0.0.0:8000 --timeout 120
    user = mayan

    [program:mayan-worker-fast]
    autorestart = true
    autostart = true
    command = nice -n 1 /opt/mayan-edms/bin/mayan-edms.py celery worker -l ERROR -Q converter,document_states_fast,sources_fast -n mayan-worker-fast.%%h --concurrency=1
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

    [program:mayan-worker-medium]
    autorestart = true
    autostart = true
    command = nice -n 18 /opt/mayan-edms/bin/mayan-edms.py celery worker -l ERROR -Q checkouts_periodic,documents_periodic,indexing,metadata,sources,sources_periodic,uploads,documents -n mayan-worker-medium.%%h --concurrency=1
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

    [program:mayan-worker-slow]
    autorestart = true
    autostart = true
    command = nice -n 19 /opt/mayan-edms/bin/mayan-edms.py celery worker -l ERROR -Q mailing,tools,statistics,parsing,ocr -n mayan-worker-slow.%%h --concurrency=1
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

    [program:mayan-celery-beat]
    autorestart = true
    autostart = true
    command = nice -n 1 /opt/mayan-edms/bin/mayan-edms.py celery beat --pidfile= -l ERROR
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

Configure Redis to discard data when it runs out of memory, not save its database and only keep 1 database:
-----------------------------------------------------------------------------------------------------------
::

    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
    echo "save \"\"" >> /etc/redis/redis.conf
    echo "databases 1" >> /etc/redis/redis.conf
    systemctl restart redis

Enable and restart the services [1_]:
-------------------------------------
::

    systemctl enable supervisor
    systemctl restart supervisor


.. _deployment_advanced:

Advanced deployment
===================

This variation uses RabbitMQ as the message broker and removes the fast worker
concurrency restriction. RabbitMQ consumes more memory but scales to thousands
of messages. RabbitMQ messages are also persistent, this means that pending
tasks are not lost in the case of a restart. The database connection lifetime
is increased to 10 minutes. The Gunicorn workers are increased to 3.

Binary dependencies
-------------------

If using a Debian_ or Ubuntu_ based Linux distribution, get the executable
requirements using::

    sudo apt-get install exiftool g++ gcc ghostscript gnupg1 graphviz \
    libfuse2 libjpeg-dev libmagic1 libpq-dev libpng-dev libreoffice \
    libtiff-dev poppler-utils postgresql python-dev python-virtualenv \
    rabbitmq-server redis-server sane-utils supervisor tesseract-ocr \
    zlib1g-dev -y

Create an user account for the installation:
--------------------------------------------
::

    sudo adduser mayan --disabled-password --disabled-login --no-create-home --gecos ""

Create the parent directory where the project will be deployed:
---------------------------------------------------------------
::

    sudo mkdir /opt

Create the Python virtual environment for the installation:
-----------------------------------------------------------
::

    sudo virtualenv /opt/mayan-edms

Make the mayan user the owner of the installation directory:
------------------------------------------------------------
::

    sudo chown mayan:mayan /opt/mayan-edms -R

Install Mayan EDMS from PyPI:
-----------------------------
::

    sudo -u mayan /opt/mayan-edms/bin/pip install --no-cache-dir mayan-edms

Install the Python client for PostgreSQL and Redis:
---------------------------------------------------
::

    sudo -u mayan /opt/mayan-edms/bin/pip install --no-cache-dir librabbitmq==2.0.0 psycopg2==2.7.3.2 redis==2.10.6

Create the database for the installation:
-----------------------------------------
::

    sudo -u postgres psql -c "CREATE USER mayan WITH password 'mayanuserpass';"
    sudo -u postgres createdb -O mayan mayan

Initialize the project:
-----------------------
::

    sudo -u mayan MAYAN_DATABASES='{default: {ENGINE: django.db.backends.postgresql, NAME: mayan, PASSWORD: mayanuserpass, USER: mayan, HOST=127.0.0.1}}' \
    MAYAN_MEDIA_ROOT=/opt/mayan-edms/media \
    /opt/mayan-edms/bin/mayan-edms.py initialsetup

Collect the static files:
-------------------------
::

    sudo -u mayan MAYAN_MEDIA_ROOT=/opt/mayan-edms/media \
    /opt/mayan-edms/bin/mayan-edms.py preparestatic --noinput

Create the RabbitMQ user and vhost:
-----------------------------------
::

    sudo rabbitmqctl add_user mayan mayanrabbitmqpassword
    sudo rabbitmqctl add_vhost mayan
    sudo rabbitmqctl set_permissions -p mayan mayan ".*" ".*" ".*"

Create the supervisor file at ``/etc/supervisor/conf.d/mayan.conf``:
--------------------------------------------------------------------
::

    [supervisord]
    environment=
        MAYAN_ALLOWED_HOSTS='["*"]',  # Allow access to other network hosts other than localhost
        MAYAN_CELERY_BROKER_URL="amqp://mayan:mayanrabbitmqpassword@localhost:5672/mayan",
        MAYAN_CELERY_RESULT_BACKEND="redis://127.0.0.1:6379/0",
        PYTHONPATH=/opt/mayan-edms/lib/python2.7/site-packages:/opt/mayan-edms/data,
        MAYAN_MEDIA_ROOT=/opt/mayan-edms/media,
        MAYAN_DATABASES='{default: {ENGINE: django.db.backends.postgresql, HOST: 127.0.0.1, NAME: mayan, PASSWORD: mayanuserpass, USER: mayan, CONN_MAX_AGE: 60}}',
        DJANGO_SETTINGS_MODULE=mayan.settings.production

    [program:mayan-gunicorn]
    autorestart = true
    autostart = true
    command = /opt/mayan-edms/bin/gunicorn -w 3 mayan.wsgi --max-requests 500 --max-requests-jitter 50 --worker-class gevent --bind 0.0.0.0:8000 --timeout 120
    user = mayan

    [program:mayan-worker-fast]
    autorestart = true
    autostart = true
    command = nice -n 1 /opt/mayan-edms/bin/mayan-edms.py celery worker -l ERROR -Q converter,document_states_fast,sources_fast -n mayan-worker-fast.%%h
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

    [program:mayan-worker-medium]
    autorestart = true
    autostart = true
    command = nice -n 18 /opt/mayan-edms/bin/mayan-edms.py celery worker -l ERROR -Q checkouts_periodic,documents_periodic,indexing,metadata,sources,sources_periodic,uploads,documents -n mayan-worker-medium.%%h --concurrency=1
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

    [program:mayan-worker-slow]
    autorestart = true
    autostart = true
    command = nice -n 19 /opt/mayan-edms/bin/mayan-edms.py celery worker -l ERROR -Q mailing,tools,statistics,parsing,ocr -n mayan-worker-slow.%%h --concurrency=1
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

    [program:mayan-celery-beat]
    autorestart = true
    autostart = true
    command = nice -n 1 /opt/mayan-edms/bin/mayan-edms.py celery beat --pidfile= -l ERROR
    killasgroup = true
    numprocs = 1
    priority = 998
    startsecs = 10
    stopwaitsecs = 1
    user = mayan

Configure Redis to discard data when it runs out of memory, not save its database and only keep 1 database:
-----------------------------------------------------------------------------------------------------------
::

    echo "maxmemory-policy allkeys-lru" >> /etc/redis/redis.conf
    echo "save \"\"" >> /etc/redis/redis.conf
    echo "databases 1" >> /etc/redis/redis.conf
    systemctl restart redis

Enable and restart the services [1_]:
-------------------------------------
::

    systemctl enable supervisor
    systemctl restart supervisor


Troubleshooting
===============

- Due to OS differences some binaries might reside in different locations.
  Use environment variables or the configuration file to tell Mayan EDMS where
  to file these binaries.

  Example: OpenBSD. Add the following entries to supervisor configuration files.
  ::

      MAYAN_DOCUMENT_PARSING_PDFTOTEXT_PATH=/usr/local/bin/pdftotext,
      MAYAN_SIGNATURES_GPG_PATH=/usr/local/bin/gpg,
      MAYAN_SOURCES_SCANIMAGE_PATH: /usr/local/bin/scanimage,

  Alternatively a symlink from the actual binary location to where Mayan
  EDMS is expecting them to be found by default also works for some users::

      ln -s /usr/local/bin/gpg /usr/bin/gpg1

  Example 2: Ubuntu 16.04. Add the following entries to supervisor
  configuration files.
  ::

      MAYAN_SIGNATURES_GPG_PATH=/usr/bin/gpg1,

  Or add a symlink::

      ln -s /usr/bin/gpg /usr/bin/gpg1

[1]: https://bugs.launchpad.net/ubuntu/+source/supervisor/+bug/1594740

.. _Debian: https://www.debian.org/
.. _Django: https://www.djangoproject.com/
.. _Python: https://www.python.org/
.. _SQLite: https://www.sqlite.org/
.. _Ubuntu: http://www.ubuntu.com/
.. _virtualenv: http://www.virtualenv.org/en/latest/index.html
.. _1: https://bugs.launchpad.net/ubuntu/+source/supervisor/+bug/1594740
